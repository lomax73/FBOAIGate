from django.urls import path

from . import views

urlpatterns = [
    path('', views.TargetListView.as_view(), name='target-list'),
    path('target/<int:pk>/terminale/', views.TerminalView.as_view(), name='target-terminal'),
]
