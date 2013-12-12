from django.shortcuts import render_to_response

def 

def chart(request):
	# Basic data for testing.
	data = [['100',10],['90',9],['80',8]]

	return render_to_response('eeg/chart.html', {
        'data':data,
        },context_instance=RequestContext(request) )