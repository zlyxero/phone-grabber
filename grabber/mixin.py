from ftplib import FTP
from .models import ConnectionData


def log_in_to_ftp():
	""" 
	mixin to log in to given ftp credentials 
	returns an ftp object
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