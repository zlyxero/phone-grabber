from django.forms import ModelForm
from .models import ConnectionData

class FTP_Login_Form(ModelForm):
	""" mirrors the ConnectionData model fields """

	class Meta:
		model = ConnectionData
		fields = '__all__'

