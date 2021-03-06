from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from sceapp.models import Ticket, Payment, Configs, Nullment
# Create your views here.

import cStringIO as StringIO
import ho.pisa as pisa
from django.template.loader import get_template
from django.template import Context
from cgi import escape

from base64 import b64encode
from reportlab.lib import units
#from reportlab.lib.units import mm
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
import binascii
import os
import logging
import math
import time
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger(__name__)


def underconst(request):
	return HttpResponse("Under Construction!")

@login_required(login_url='/sceapp/login/')
def index(request):
	lastest_tickets_list = Ticket.objects.order_by('-start_date')[:5]
        #output = ', '.join([p.description for p in lastest_tickets_list])
        context = {'lastest_tickets_list': lastest_tickets_list}
        return render(request,'sceapp/index.html', context)

#	return HttpResponse("Hola mundo. SCEAPP")

@login_required(login_url='/sceapp/login/')
def newticket(request):
	user_str = str(request.user)
	data = binascii.hexlify(os.urandom(6))
	plate_id = request.POST['plate_id']

	logger.debug("newticket: plate_id: %s ", plate_id)
	
	t = Ticket(description="Generated By SCEAPP", token=data, plate_id=plate_id ,created_by=user_str)
	t.save()
	#logger.debug("newticket: %s ", data)
	#return HttpResponseRedirect(reverse('sceapp:ticketsuccess', args=("1")))
	#return HttpResponseRedirect(reverse('sceapp:pdfview', args=("1"), kwargs={'ticket_id': data}))
	return HttpResponseRedirect(reverse('sceapp:pdfview', args=(data,)))

@login_required(login_url='/sceapp/login/')
def newtabticket(request):
	return render(request, 'sceapp/newtabticket.html')

@login_required(login_url='/sceapp/login/')
def ticketsuccess(request, ticket_id):
	ticket = get_object_or_404(Ticket, pk=ticket_id)
	return render(request, 'sceapp/ticketsuccess.html', {'ticket':ticket})

@login_required(login_url='/sceapp/login/')
def newpayticket(request):
	return render(request, 'sceapp/newpayticket.html')

@login_required(login_url='/sceapp/login/')
def payticketpreview(request):

	t_array = Ticket.objects.filter(token=request.POST['typed_id']).order_by('-start_date')

        if len(t_array) >= 1:
                t = t_array[0]
        else:
                return render(request, 'sceapp/paymenterror.html')

	#ticket abierto
	if t.state == 'A':
	
		paydate = timezone.now()

		#TODO: create error return for config not found
        	configMinTime = Configs.objects.get(key="minTime")
        	minTime = configMinTime.value

		configMinRate = Configs.objects.get(key="minRate")
        	rate = configMinRate.value

		time_diff = paydate - t.start_date
        	logger.debug("payticketpreview: time_diff: %s ", time_diff)

        	total_seconds = time_diff.total_seconds()
        	logger.debug("payticketpreview: total_seconds: %s ", total_seconds)
		total_time_str = time.strftime('%H:%M:%S', time.gmtime(total_seconds))

		if(total_seconds < int(minTime)):
                	amount = rate
                	logger.debug("payticketpreview: total < time rate: %s ", amount)
        	else:
			configTolerance = Configs.objects.get(key="tolerance")
			tolerance = configTolerance.value
			total_min_time_rounds_floor = math.floor(total_seconds/int(minTime))
			logger.debug("payticketpreview: floor %d", total_min_time_rounds_floor)
                	total_min_time_rounds_ceil = math.ceil(total_seconds/int(minTime))
			logger.debug("payticketpreview: ceil %d", total_min_time_rounds_ceil)
			if (total_seconds < ((int(minTime)*total_min_time_rounds_floor) + int(tolerance))):
                		amount = int(total_min_time_rounds_floor * int(rate))
                		logger.debug("payticketpreview: total > time rate + tolerance: %d , %s ",(int(minTime)*total_min_time_rounds_floor + int(tolerance)), amount)
			else:
				amount = int(total_min_time_rounds_ceil * int(rate))
                                logger.debug("payticketpreview: total < time rate + tolerance: %d , %s ", (int(minTime)*total_min_time_rounds_ceil + int(tolerance)), amount)

        	return render(request, 'sceapp/payticketpreview.html', {'start_date': t.start_date, 'end_date': paydate, 'total_time_str': total_time_str, 'amount': amount, 'ticket_token': t.token})
	
	else:
		
		time_diff = t.end_date - t.start_date
                logger.debug("payticketpreview: time_diff: %s ", time_diff)

                total_seconds = time_diff.total_seconds()
                logger.debug("payticketpreview: total_seconds: %s ", total_seconds)
                total_time_str = time.strftime('%H:%M:%S', time.gmtime(total_seconds))

		for p in t.payment_set.all():
			amount = p.amount
		
		return render(request, 'sceapp/paymentexist.html', {'start_date': t.start_date, 'end_date': t.end_date, 'total_time_str': total_time_str, 'amount': amount, 'ticket_token': t.token, 'state': t.state})


@login_required(login_url='/sceapp/login/')
def payticket(request):

	t_array = Ticket.objects.filter(token=request.POST['typed_id']).order_by('-start_date')
	
	if len(t_array) >= 1:
		t = t_array[0]
	else:
		logger.debug("payticket: No ticket found!. ticket_id from post %s", request.POST['typed_id'])
		return render(request, 'sceapp/paymenterror.html')		

	
	#check if a payment already exist for the ticket id. Avoid Double Payment for a ticket
	p_array = Payment.objects.filter(ticket=t)
	
	if len(p_array)  >= 1:
		logger.debug("payticket: Payment for ticket %s already exist.", request.POST['typed_id'])
		return render(request, 'sceapp/paymentexisterror.html')

	#t = get_object_or_404(Ticket, pk=request.POST['typed_id'])
	logger.debug("payticket: end_time: %s ", request.POST['end_date'])
	t.end_date = request.POST['end_date']
	t.state = "P"
	amount = float(request.POST['amount'])

	payment = Payment(ticket=t,amount=amount, payment_date=t.end_date)

	t.save()
	payment.save()
	
	#return render(request, 'sceapp/paymentsuccess.html')
	return HttpResponseRedirect(reverse('sceapp:paypdfview', args=(t.token,)))

@login_required(login_url='/sceapp/login/')
def listtickets(request):
	lastest_tickets_list = Ticket.objects.order_by('-start_date')[:5]
	#output = ', '.join([p.description for p in lastest_tickets_list])
	template = loader.get_template('sceapp/index.html')
	context = RequestContext(request, {
        	'lastest_tickets_list': lastest_tickets_list,
    	})
	return HttpResponse(template.render(context))

@login_required(login_url='/sceapp/login/')
def ticketsbydayform(request):
	return render(request, 'sceapp/ticketsbydayform.html')

@login_required(login_url='/sceapp/login/')
def listticketsbyday(request):
	date_str = request.POST.get('dateSelected')
	logger.debug("listticketsbyday: date_str: %s ", date_str)


#for pagination we use GET
	if not date_str:
		date_str = request.GET.get('dateSelected')

	ticket_list = Ticket.objects.filter(start_date__startswith=date_str).order_by('-start_date')
	total_amount=0
	total_tickets=0
	for t in ticket_list:
		if t.payment_set.all():
			total_amount = total_amount + t.payment_set.all()[0].amount
	total_tickets=len(ticket_list)
	#ticket_list = Ticket.objects.filter(start_date=datetime.date(year,month,day))
	#logger.debug("listticketsbyday: ticket_list[0]: %s ", str(ticket_list))
	paginator = Paginator(ticket_list, 20)
	page = request.GET.get('page')

	try:
		tickets = paginator.page(page)
	except PageNotAnInteger:
		tickets = paginator.page(1)
	except EmptyPage:
		tickets = paginator.page(paginator.num_pages)

	return render_to_response('sceapp/ticketlistbyday.html', {"tickets": tickets, "total_amount": total_amount,"dateSelected": date_str,"total_tickets": total_tickets})

@login_required(login_url='/sceapp/login/')
def ticketsbymonthform(request):
        return render(request, 'sceapp/ticketsbymonthform.html')



@login_required(login_url='/sceapp/login/')
def listticketsbymonth(request):
        date_str = request.POST.get('yearSelected')
        logger.debug("listticketsbyday: date_str: %s ", date_str)
        if not date_str:
                date_str = request.GET.get('yearSelected')
        #       date_array = date_str.split('/')
        #       new_date_str = "%s-%s-%s"%(date_array[2],date_array[1],date_array[0])
        #       logger.debug("listticketsbyday: y-m-d: %s", new_date_str)
	total_list = []

	for i in range(1,13):
		logger.debug("listticketsbymonth: datestr+i %s",date_str+"-"+str(i))
		ticket_list_count = Ticket.objects.filter(start_date__year=date_str, start_date__month=i).count()
		payed_count = Ticket.objects.filter(start_date__year=date_str, start_date__month=str(i)).filter(state="A").count()
		open_count = Ticket.objects.filter(start_date__year=date_str, start_date__month=str(i)).filter(state="P").count()
		null_count = Ticket.objects.filter(start_date__year=date_str, start_date__month=str(i)).filter(state="N").count()
		item_list = { 'ticket_count': ticket_list_count, 'payed_count': payed_count, 'open_count': open_count, 'null_count': null_count }
		logger.debug("listticketsbymonth: itemlist: %s ", str(item_list))
		total_list.insert(i,item_list)

	
        #ticket_list = Ticket.objects.filter(start_date=datetime.date(year,month,day))
        #logger.debug("listticketsbyday: ticket_list[0]: %s ", str(ticket_list))

        return render_to_response('sceapp/ticketlistbymonth.html',  { 'total_list': total_list })


@login_required(login_url='/sceapp/login/')
def detail(request, ticket_id):
	try:
		ticket = Ticket.objects.get(pk=ticket_id)
	except Ticket.DoesNotExist:
		raise Http404
	return render(request, 'sceapp/detail.html', {'ticket':ticket})

@login_required(login_url='/sceapp/login/')
def manualpaymentform(request):
	return render(request, 'sceapp/manualpaymentform.html')

@login_required(login_url='/sceapp/login/')
def manualpaymentpreview(request):
	
	ticket_id = request.POST['typed_id']
        t_array = Ticket.objects.filter(token=ticket_id).order_by('-start_date')

        if len(t_array) >= 1:
                t = t_array[0]
        else:
                return render(request, 'sceapp/ticketnotexist.html', {'ticket_id': ticket_id} )

        return render(request, 'sceapp/manualpaymentpreview.html', {'ticket_id': t.token, 'start_date': t.start_date, 'state': t.state} )

@login_required(login_url='/sceapp/login/')
def manualpaymentpreview2(request):

	ticket_id = request.POST['typed_id']
        t_array = Ticket.objects.filter(token=ticket_id).order_by('-start_date')

        if len(t_array) >= 1:
                t = t_array[0]
        else:
                return render(request, 'sceapp/ticketnotexist.html', {'ticket_id': ticket_id} )
	
	end_date = timezone.now()
	period = request.POST['period']
	amount = request.POST['amount']
	description = request.POST['description']
	

        return render(request, 'sceapp/manualpaymentpreview2.html', {'ticket_id': t.token, 'start_date': t.start_date, 'state': t.state, 'end_date': end_date, 'period': period, 'amount':amount, 'description': description})


@login_required(login_url='/sceapp/login/')
def manualpayment(request):

	t_array = Ticket.objects.filter(token=request.POST['typed_id']).order_by('-start_date')

        if len(t_array) >= 1:
                t = t_array[0]
        else:
                return render(request, 'sceapp/paymenterror.html')

        #t = get_object_or_404(Ticket, pk=request.POST['typed_id'])
        logger.debug("manualpayment: end_time: %s ", request.POST['end_date'])
	logger.debug("manualpayment: period: %s ", request.POST['period'])
        t.end_date = request.POST['end_date']
        t.state = "P"
        amount = request.POST['amount']
	period = request.POST['period']
	description = request.POST['description']

        payment = Payment(ticket=t,amount=amount, payment_date=t.end_date,period=period,description=description)

        t.save()
        payment.save()

        #return render(request, 'sceapp/paymentsuccess.html')
        return HttpResponseRedirect(reverse('sceapp:paypdfview', args=(t.token,)))

@login_required(login_url='/sceapp/login/')
def nullticketform(request):
	return render(request, 'sceapp/nullticketform.html')

@login_required(login_url='/sceapp/login/')
def nullticketpreview(request):

	ticket_id = request.POST['typed_id']
        t_array = Ticket.objects.filter(token=ticket_id)

        if len(t_array) >= 1:
                t = t_array[0]
        else:
                return render(request, 'sceapp/ticketnotexist.html', {'ticket_id': ticket_id} )

        return render(request, 'sceapp/nullticketpreview.html', {'ticket_id': t.token, 'start_date': t.start_date, 'state': t.state} )


@login_required(login_url='/sceapp/login/')
def nullticket(request):

	ticket_id = request.POST['typed_id']
	t_array = Ticket.objects.filter(token=ticket_id)

        if len(t_array) >= 1:
                t = t_array[0]
        else:
                return render(request, 'sceapp/ticketnotexist.html', {'ticket_id', ticket_id} )

	description = request.POST['description']
	
	nullment_date = timezone.now()

	t.state = "N"

	nullment = Nullment(ticket=t, nullment_date=nullment_date , description=description)
	nullment.save()
	t.save()
	
        return render(request, 'sceapp/nullticket.html', {'ticket_id': t.token, 'start_date': t.start_date, 'state': t.state, 'nullment_date': nullment_date, 'description': description} )


def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/sceapp/index/')
	else:
	     state = "Usuario o clave incorrecto."

    return render_to_response('login.html', {'state':state, 'username': username} ,context_instance=RequestContext(request))

def logout_user(request):
	state = "Usuario deslogueado del sistema..."
	logout(request)
	return render_to_response('login.html', {'state':state}, context_instance=RequestContext(request))


def get_barcode(value, width, barWidth = 0.03*units.inch, fontSize = 70, humanReadable = False):

    barcode = createBarcodeDrawing('Code128', value = value, barWidth = barWidth, fontSize = fontSize, humanReadable = humanReadable)

    drawing_width = width
    barcode_scale = drawing_width / barcode.width
    drawing_height = barcode.height * barcode_scale

    drawing = Drawing(drawing_width, drawing_height)
    drawing.scale(barcode_scale, barcode_scale)
    drawing.add(barcode, name='barcode')

    return drawing

def get_image(value):

    barcode = get_barcode(value = value, width = 600)
    data = b64encode(renderPM.drawToString(barcode, fmt = 'PNG'))
    #print '<img src="data:image/png;base64,{0}">'.format(data)
    #return '<img src="data:image/png;base64,{0}">'.format(data)
    return 'data:image/png;base64,{0}'.format(data)

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()

    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error <pre>%s</pre> por favor intente nuevamente' % escape(html))

def pdfview(request, ticket_id):
    #Retrieve data or whatever you need
    tickets = Ticket.objects.filter(token=ticket_id)
    t = tickets[0]
    start_date=t.start_date
    plate_id=t.plate_id

    bc = get_image(ticket_id)
    results=[ bc ]
    header= ""
    top_title_config = Configs.objects.get(key="topTitle")
    top_title = top_title_config.value
    logger.debug("pdfview: topTitle: %s", top_title)
    return render_to_pdf(
            'tickettemplate.html',
            {
                'pagesize':'b6',
                'mylist': results,
		'barcode': bc,
		'ticket_id': ticket_id,
		'plate_id': plate_id,
		'top_title': top_title,
		'start_date': start_date
            }
        )

def paypdfview(request, ticket_id):
    #Retrieve data or whatever you need
    tickets = Ticket.objects.filter(token=ticket_id)
    t = tickets[0]
    start_date=t.start_date
    end_date=t.end_date
    logger.debug("paypdfview: enddate %s startdate %s ", end_date, start_date)
    time_diff=t.end_date - t.start_date
    logger.debug("paypdfview: time_diff: %s ", time_diff.total_seconds())
    total_time= time.strftime('%H:%M:%S', time.gmtime(time_diff.total_seconds()))
    logger.debug("paypdfview: total_time: %s ", total_time)
    amount=t.payment_set.all()[0].amount

    top_title_config = Configs.objects.get(key="topTitle")
    top_title = top_title_config.value
    logger.debug("paypdfview: topTitle: %s", top_title)
    
    header= ""
    return render_to_pdf(
            'paytemplate.html',
            {
                'pagesize':'b6',
                'ticket_id': ticket_id,
		'start_date': start_date,
		'end_date': end_date,
		'total_time': total_time,
		'amount': amount,
		'top_title': top_title
            }
        )

