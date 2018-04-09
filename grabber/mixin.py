from ftplib import FTP
from .models import ConnectionData
from django.shortcuts import redirect


def log_in_to_ftp():
	""" 
	[function] logs in to given ftp credentials. 

	Returns an ftp object
	"""
	# get ftp login credentials
	data = ConnectionData.objects.get(id=1)
	host = data.host
	port = data.port

	# login to ftp server
	ftp = FTP()
	ftp.connect(host, port) 
	ftp.login()

	return ftp