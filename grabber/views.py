from django.shortcuts import render, redirect
from .forms import FTP_Login_Form
from django.views import View
from .models import ConnectionData

import os
from ftplib import FTP, error_perm 
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
				# Check if object with an id value of 1 exists. if it does overrite it with
				# new ftp login details. Else, create a new object with provided details.

				data_queryset = ConnectionData.objects.filter(id=1)
				
				if data_queryset:
					data = data_queryset[0] 
					data.host = host
					data.port = port
					data.save()
				else:
					ConnectionData.objects.create(id=1, host=host, port=port)

				return redirect('navigator')

			# should there be any errors, display index.html templated with a login error 
			except:
				return render(request, 'errors.html', {'form': form, 'error':'login_error'})

		return render(request, 'index.html', {'form': form, 'error':'form_error'})			



def navigator(request):
	""" 
	navigates to a given 'path'.
	If 'path' is a file, it is downloaded

	"""
	# check connection
	try:
		ftp = log_in_to_ftp() # function defined in mixin.py 
	except:	
		return render(request, 'errors.html', {'error': 'connection_lost_error'})
	

	# get the request url (in the format '/navigator/path/') and slice out the absolute path of 
	# the requested directory by removing the prepended '/navigator' string

	path = request.path

	directory_path = path[10:]

	# change to the requested directory and retrieve listing

	try:
		ftp.cwd(directory_path)

	except error_perm as error:
		
		redirect("navigator")
		print("There was an error!! Directory may be nonexistent")	

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
			dir_list.append(a.lower())

		else:
			file_list.append(a.lower())	 

	# sort file and dir lists
	dir_list.sort()
	file_list.sort()

	return render(request, 'listing.html', {'file_list': file_list, 'dir_list': dir_list, 'path': directory_path}) 


class FileDownload(View):

	def post(self, request):
		
		# get selected download path and check if it exists.
		download_path = request.POST.get('download_path')

		if not os.path.exists(download_path):
			return render(request, 'errors.html', {'error': 'download_path_error'})


		# use getlist instead of get to retrieve our checkbox list from POST. 
		# see https://code.djangoproject.com/ticket/1130
		selected_files_list = request.POST.getlist('files')
		ftp = log_in_to_ftp()

		if ftp == 'error':
			return redirect('login')
		
		def getfile(save_path, file_path, ftp):
			""" fetches 'file' from FTP server and saves it to the destination at 'save_path'.

				save_path: the path to save downloaded files
				file_path: the absolute path to the file to be downloaded
			"""
			def writer(chunk):
				""" callback function to FTP retrbinary().

					writes a 'chunk' of data to a file object on each call to the function	
				"""
				
				file_object.write(chunk)

		
			# get filename from splitting the file path at the FTP server and retrieving the filename part
			parts = file_path.split('/')
			file_name = parts[-1]

			# append filename to save path
			save_path = '{}/{}'.format(save_path, file_name)

			# open file for writing
			with open(save_path, 'wb') as file_object:
				ftp.retrbinary('RETR ' + file, writer, blocksize=10000)

		
		# download selected files 
		for file in selected_files_list:
			getfile(download_path, file, ftp)

		# format downloaded file names for display on front end
		files = [file[1:] for file in selected_files_list ]

		return render(request, 'downloads.html', {'files':files})

			




