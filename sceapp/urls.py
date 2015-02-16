from django.conf.urls import patterns, url, include

from sceapp import views

urlpatterns = patterns('',
    #ex: /sceapp/login
    url(r'^login/$', views.login_user, name='auth'),
    #ex: /sceapp/logout
    url(r'^logout/$', views.logout_user, name='logout'),
    #ex: /sceapp/
    url(r'^index/$', views.index, name='index'),
    #ex: /sceapp/5/
    url(r'^(?P<ticket_id>\d+)/$', views.detail, name='detail'),
    #ex: sceapp/newticket/ handles the ticket creation
    url(r'^newticket/$', views.newticket, name='newticket'),
    #ex: sceapp/newtabticket/ handles the ticket creation
    url(r'^newtabticket/$', views.newtabticket, name='newtabticket'),
    #ex: sceapp/ticketsuccess/
    url(r'^(?P<ticket_id>\w+)/ticketsuccess/$', views.ticketsuccess, name='ticketsuccess'),
    #ex: sceapp/newpayticket
    url(r'^newpayticket/$', views.newpayticket, name='newpayticket'),
    #ex: sceapp/5/payticket
    url(r'^payticket/$', views.payticket, name='payticket'),
     #ex: sceapp/payticketpreview
    url(r'^payticketpreview/$', views.payticketpreview, name='payticketpreview'),

    #ex: sceapp/listticket
    url(r'^listtickets/$', views.listtickets, name='listtickets'),
    #ex: sceapp/listticketsbyday
    url(r'^listticketsbyday/$', views.listticketsbyday, name='listticketsbyday'),

    url(r'^ticketsbydayform/$', views.ticketsbydayform, name='ticketsbydayform'),

    #ex: sceapp/nullticketform
    url(r'^nullticketform/$', views.nullticketform, name='nullticketform'),

    #ex: sceapp/nullticket
    url(r'^nullticket/$', views.nullticket, name='nullticket'),
    
    #ex: sceapp/nullticketpreview
    url(r'^nullticketpreview/$', views.nullticketpreview, name='nullticketpreview'),

    #ex: sceapp/manualpaymentform
    url(r'^manualpaymentform/$', views.manualpaymentform, name='manualpaymentform'),
    #ex: sceapp/manualpaymentpreview
    url(r'^manualpaymentpreview/$', views.manualpaymentpreview, name='manualpaymentpreview'),
    #ex: sceapp/manualpayment
    url(r'^manualpayment/$', views.manualpayment, name='manualpayment'),


    url(r'^listticketsbymonth/$', views.listticketsbymonth, name='listticketsbymonth'),

    url(r'^ticketsbymonthform/$', views.ticketsbymonthform, name='ticketsbymonthform'),

    url(r'^(?P<ticket_id>\w+)/pdfview/$', views.pdfview, name='pdfview'),

    url(r'^(?P<ticket_id>\w+)/paypdfview/$', views.paypdfview, name='paypdfview'),
)
