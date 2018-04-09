from django.urls import path, re_path
from . import views
urlpatterns = [

	path('login/', views.FTP_Login.as_view(), name='login'),
	path('download_file/', views.FileDownload.as_view(), name='download'),
	re_path(r'^navigator/', views.navigator, name='navigator'),
]