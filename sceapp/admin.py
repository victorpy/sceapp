from django.contrib import admin

# Register your models here.
from sceapp.models import Ticket,Payment,Configs

admin.site.register(Ticket)
admin.site.register(Payment)
admin.site.register(Configs)
