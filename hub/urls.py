from django.urls import path

from . import views

urlpatterns = [
    path('targets/', views.InternalTargetListView.as_view(), name='internal-target-list'),
    path('targets/<int:pk>/resources/', views.InternalTargetResourcesView.as_view(), name='internal-target-resources'),
]
