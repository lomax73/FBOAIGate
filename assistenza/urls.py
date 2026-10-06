from django.urls import path

from . import views

urlpatterns = [
    path('', views.PostazioneListView.as_view(), name='assistenza-list'),
    path('postazione/nuova/', views.PostazioneCreateView.as_view(), name='assistenza-postazione-new'),
    path('postazione/<int:pk>/modifica/', views.PostazioneUpdateView.as_view(), name='assistenza-postazione-edit'),
    path('postazione/<int:pk>/elimina/', views.PostazioneDeleteView.as_view(), name='assistenza-postazione-delete'),
    path('postazione/<int:pk>/connetti/', views.ConnettiView.as_view(), name='assistenza-connetti'),
    path('cliente/nuovo/', views.ClienteCreateView.as_view(), name='assistenza-cliente-new'),
    path('cliente/<int:pk>/modifica/', views.ClienteUpdateView.as_view(), name='assistenza-cliente-edit'),
    path('onboarding/', views.OnboardingView.as_view(), name='assistenza-onboarding'),
    path('onboarding/script/<str:sistema>/', views.ScriptDownloadView.as_view(), name='assistenza-script'),
]
