from django.urls import path, re_path
from . import views
urlpatterns = [

	path('login/', views.FTP_Login.as_view(), name='login'),
	path('dir-listing/', views.dir_listing, name='dir_listing'),
	re_path(r'^', views.navigator, name='navigator'),
]