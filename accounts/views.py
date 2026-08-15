import json

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

LOGIN_RATE_LIMIT_WINDOW_SECONDS = 3600
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = 10


def _client_ip(request):
    # X-Real-IP è impostato solo da nginx (deploy/nginx-fboaigate.conf, sempre
    # sovrascritto con $remote_addr), quindi il client non può manometterlo -
    # a differenza di X-Forwarded-For.
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')


class RateLimitedLoginView(LoginView):
    """Dietro questo login c'è accesso a terminale/SFTP completo sugli host
    registrati: limita i tentativi falliti per IP (finestra scorrevole)
    invece di lasciare il login senza alcuna protezione anti-bruteforce."""

    def _cache_key(self, request):
        return f'login-attempts:{_client_ip(request)}'

    def post(self, request, *args, **kwargs):
        key = self._cache_key(request)
        if cache.get(key, 0) >= LOGIN_RATE_LIMIT_MAX_ATTEMPTS:
            form = self.get_form_class()(request=request)
            form.add_error(None, 'Troppi tentativi falliti. Riprova più tardi.')
            return self.render_to_response(self.get_context_data(form=form))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._cache_key(self.request)
        cache.set(key, cache.get(key, 0) + 1, LOGIN_RATE_LIMIT_WINDOW_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._cache_key(self.request))
        return super().form_valid(form)


def _check_token(request):
    expected = getattr(settings, 'INTERNAL_API_TOKEN', '')
    provided = request.headers.get('Authorization', '')
    if not expected or provided != f'Token {expected}':
        return False
    return True


def _serialize(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'date_joined': user.date_joined.isoformat(),
    }


@method_decorator(csrf_exempt, name='dispatch')
class InternalUserListView(View):
    def dispatch(self, request, *args, **kwargs):
        if not _check_token(request):
            return JsonResponse({'detail': 'Non autorizzato.'}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        users = User.objects.all().order_by('username')
        return JsonResponse({'users': [_serialize(u) for u in users]})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse({'detail': 'JSON non valido.'}, status=400)

        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '')
        if not username or not password:
            return JsonResponse({'detail': 'username e password sono obbligatori.'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'detail': 'Username già esistente.'}, status=409)

        user = User.objects.create_user(username=username, password=password, email=email)
        return JsonResponse(_serialize(user), status=201)


@method_decorator(csrf_exempt, name='dispatch')
class InternalUserDetailView(View):
    def dispatch(self, request, *args, **kwargs):
        if not _check_token(request):
            return JsonResponse({'detail': 'Non autorizzato.'}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def _get_user(self, pk):
        return User.objects.filter(pk=pk).first()

    def patch(self, request, pk):
        user = self._get_user(pk)
        if user is None:
            return JsonResponse({'detail': 'Utente non trovato.'}, status=404)
        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse({'detail': 'JSON non valido.'}, status=400)

        if 'email' in data:
            user.email = data['email']
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        if data.get('password'):
            user.set_password(data['password'])
        user.save()
        return JsonResponse(_serialize(user))

    def delete(self, request, pk):
        user = self._get_user(pk)
        if user is None:
            return JsonResponse({'detail': 'Utente non trovato.'}, status=404)
        user.delete()
        return JsonResponse({}, status=204)
