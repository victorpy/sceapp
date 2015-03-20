from django.contrib import admin

# Register your models here.
from sceapp.models import Ticket,Payment,Configs

class TicketAdmin(admin.ModelAdmin):
	fields = ['start_date', 'end_date', 'token', 'state']
	list_display = ('start_date', 'end_date', 'token', 'state')
	list_filter = ['start_date']

class PaymentAdmin(admin.ModelAdmin):
        #fields = ['payment_date', 'token']
	search_fields = ['token']
	list_display = ('payment_date', 'token')
	
	def token(self, obj):
		return obj.ticket.token
	token.short_description = 'Token'

admin.site.register(Ticket,TicketAdmin)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Configs)
