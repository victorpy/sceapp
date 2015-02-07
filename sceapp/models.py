from django.db import models
from datetime import datetime 
from django.utils import timezone
# Create your models here.

class Ticket(models.Model):
	start_date = models.DateTimeField('Fecha Entrada', default=timezone.now)
	end_date = models.DateTimeField('Fecha Salida',  blank=True, null=True)
	description = models.CharField(max_length=200)
        token = models.CharField(max_length=12, default="No token")
	created_by = models.CharField(max_length=64, default="None")
	state = models.CharField(max_length=1, default="A")
	def __unicode__(self):
		return self.token

class Payment(models.Model):
	ticket = models.ForeignKey(Ticket)
	payment_date = models.DateTimeField('Fecha Pago')
	amount = models.IntegerField(default=0)
	description = models.CharField(max_length=200, default="No desc")
	created_by = models.CharField(max_length=64, default="None")
		
	def __unicode__(self):
		return self.ticket.token

class Configs(models.Model):
	key = models.CharField(max_length=64)
	value = models.CharField(max_length=128)

	def __unicode__(self):
                return self.key
