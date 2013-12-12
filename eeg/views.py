from django.shortcuts import render_to_response
from django.template import RequestContext

from eeg.models import *

def chart(request):
	# Basic data for testing.	
        # data = [['100',10],['90',9],['80',8]]
        
        high_alpha = DataPoint.objects.all().order_by('time')
 
        data = '[\n'
 
        for point in high_alpha:
          data+='[' + str(point.js_time())+ ',' + str(point.value)+'],\n'
 
        data = data[:-1]+']'
	
        return render_to_response('eeg/chart.html', {
            'data':data,
        },context_instance=RequestContext(request) )
