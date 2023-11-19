from django.urls import path

from . import views

urlpatterns = [
    path('generate-doc/', views.GenerateChunkDoc.as_view(), name="generate-doc"),
    path('get-doc/<str:file_name>/<str:project_name>/', views.getFileDoc, name="get doc"),
    path('new-project/', views.createNewProject, name="new project"),
    path('update-file/', views.updateFile, name="update file"),
    path('update-doc/', views.editChunkDoc, name="update doc"),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
]
