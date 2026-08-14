from django.urls import path

from . import views

urlpatterns = [
    path('', views.TargetListView.as_view(), name='target-list'),
    path('target/<int:pk>/terminale/', views.TerminalView.as_view(), name='target-terminal'),
    path('target/<int:pk>/rinomina/', views.TargetRenameView.as_view(), name='target-rename'),
    path('target/<int:pk>/risorse/', views.TargetResourcesView.as_view(), name='target-resources'),
    path('target/<int:pk>/file-manager/', views.FileManagerView.as_view(), name='target-file-manager'),
    path('target/<int:pk>/file-manager/lista/', views.TargetFilesListView.as_view(), name='target-files-list'),
    path('target/<int:pk>/file-manager/nuova-cartella/', views.TargetFilesMkdirView.as_view(), name='target-files-mkdir'),
    path('target/<int:pk>/file-manager/elimina/', views.TargetFilesDeleteView.as_view(), name='target-files-delete'),
    path('target/<int:pk>/file-manager/carica/', views.TargetFilesUploadView.as_view(), name='target-files-upload'),
]
