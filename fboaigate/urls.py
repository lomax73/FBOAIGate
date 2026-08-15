from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.views import RateLimitedLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', RateLimitedLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/internal/', include('accounts.urls')),
    path('', include('console.urls')),
]
