from django.shortcuts import render, redirect
from .forms import FTP_Login_Form
from django.views import View
from ftplib import FTP 
from .models import ConnectionData
from .mixin import log_in_to_ftp
# Create your views here.

class FTP_Login(View):

	def get(self, request):
		""" display ftp login form """

		form = FTP_Login_Form()
		return render(request, 'index.html', {'form':form})

	def post(self, request):
		""" 
		verifies ftp login form fields and tries to connect 
		to ftp server. If connection is  established, login
		data is saved in the database. Else the user is notified
		of any errors and retries to login
		"""
		
		form = FTP_Login_Form(request.POST)

		if form.is_valid():

			# get login fields data
			host = form.cleaned_data['host']
			port = form.cleaned_data['port']
			
			# attempt to login
			try:
				ftp = FTP()
				ftp.connect(host, port) 
				ftp.login()
				
				# save data to database
				# NB: the program is only meant to work with one database object at id = 1
				# previous login details are discarded(overwritten)
				# Check if object with an id value of 1 exists. if it does overrite it
				# with new ftp login details. else, create a new object with provided details.

				data_queryset = ConnectionData.objects.filter(id=1)
				
				if data_queryset:
					data = data_queryset[0] 
					data.host = host
					data.port = port
					data.save()
				else:
					ConnectionData.objects.create(id=1, host=host, port=port)

				return redirect('dir_listing')

			except:
				return render(request, 'index.html', {'form': form, 'error':'login_error'})

		return render(request, 'index.html', {'form': form, 'error':'form_error'})			


def dir_listing(request):
	""" retrieves directory listing of ftp host device """

	# get ftp login credentials
	data = ConnectionData.objects.get(id=1)
	host = data.host
	port = data.port

	# connect to ftp
	try:
		ftp = log_in_to_ftp() # function defined in mixin.py 
	except:	
		return render(request, 'listing.html', {'error': 1})
		
	
	items_list = [] # will hold both files and directories
	long_listing = [] # will hold both files and directories with long listing format
	file_list = [] # will only hold files
	dir_list = [] # will only hold directories

	def add_to_items_list(file_string):
		""" 
		callback function for ftp.retrlines()
		appends each file/dir string to items_list
		"""
		items_list.append(file_string)

	def add_to_long_listing(file_string):	
		""" 
		callback function for ftp.retrlines()
		appends items to long_listing list
		"""
		long_listing.append(file_string)	

	# retrieve directory listing
	ftp.retrlines('NLST', add_to_items_list)

	# get long listing of the current working directory 
	ftp.dir(add_to_long_listing)

	# populate file_list and dir_list with files and directories respectively
	for a, b in zip(items_list, long_listing):

		if b.startswith('d'):
			dir_list.append(a)

		else:
			file_list.append(a)	 

	return render(request, 'listing.html', {'file_list': file_list, 'dir_list': dir_list, 'path': '/'}) 


def navigator(request):
	""" 
	navigates to a given 'path'.
	If 'path' is a file, it is downloaded

	"""
	# check connection
	try:
		ftp = log_in_to_ftp() # function defined in mixin.py 
	except:	
		return render(request, 'listing.html', {'error': 1})
	

	path = request.path

	# change to path dir and retrieve listing
	ftp.cwd(path)

	items_list = [] # will hold both files and directories
	long_listing = [] # will hold both files and directories with long listing format
	file_list = [] # will only hold files
	dir_list = [] # will only hold directories

	def add_to_items_list(file_string):
		""" 
		callback function for ftp.retrlines()
		appends each file/dir string to items_list
		"""
		items_list.append(file_string)

	def add_to_long_listing(file_string):	
		""" 
		callback function for ftp.retrlines()
		appends items to long_listing list
		"""
		long_listing.append(file_string)	

	# retrieve directory listing
	ftp.retrlines('NLST', add_to_items_list)

	# get long listing of the current working directory 
	ftp.dir(add_to_long_listing)

	# populate file_list and dir_list with files and directories respectively
	for a, b in zip(items_list, long_listing):

		if b.startswith('d'):
			dir_list.append(a)

		else:
			file_list.append(a)	 

	return render(request, 'listing.html', {'file_list': file_list, 'dir_list': dir_list, 'path': path}) 



	

			




