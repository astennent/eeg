from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt #for POST requests from mobile devices that couldn't have gotten a csrf token.

from eeg.models import *
import json
import base64
from django.contrib.auth import authenticate, login

# Called whenever a mobile request is sent which requires authentication
def validate_mobile(request):
    try:
        username, password = base64.b64decode(request.POST['HTTP_AUTHORIZATION']).split(":")
    except:
        return None
    return authenticate(username=username, password=password)

def respond(message):
    json_dump = json.dumps({"message":message})
    return HttpResponse(json_dump, content_type="application/json")



# Retrieves data from the mobile app
@csrf_exempt
def post_data(request):
    user = validate_mobile(request)
    
    if user == None:
        return respond("Invalid username and password")

    extract_waves(request, user)
 
    # TODO: Handle any additional data.

    return respond("success")

def extract_waves(request, user):
    data = {}

    expected_names = ["HIGHALPHA", "HIGHBETA", "MIDGAMMA", 
        "LOWALPHA", "LOWBETA", "LOWGAMMA", "DELTA", "THETA"]

    for wave_id, name in enumerate(expected_names):
        if name in request.POST:
            dp = DataPoint(user=user, value=request.POST[name], wave=wave_id)
            dp.save()

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
