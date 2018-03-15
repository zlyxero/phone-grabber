from django.db import models

# Create your models here.

class ConnectionData(models.Model):
	""" Contains ftp login credentials """

	host = models.CharField(max_length=70)
	port = models.IntegerField()

	def __str__(self):

		return "connection to {}:{}".format(self.host, self.port)