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

@csrf_exempt
def check_login(request):
    user = validate_mobile(request)
    
    if user == None:
        return respond("Invalid username and password")
 
    return respond("success")

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
            dp = DataPoint(user=user, value=request.POST[name], wave=wave_id+1)
            dp.save()

def chart(request):
    # Basic data for testing.	
    # data = [['100',10],['90',9],['80',8]]

    columnData = genColumnData()

    data_points = DataPoint.objects.all().order_by('time')
    data = []

    last_row = None 
    for point in data_points:
      js_time = point.js_time()
      if last_row != None and js_time == last_row[0]:
        row = last_row
      else: 
        row = [js_time,]
        data.append(row)
        for wave_type in WAVE_TYPES:
          row.append("undefined")

      row[point.wave] = point.value
      last_row = row

    cleanData = cleanString(data)

    return render_to_response('eeg/chart.html', {
        'data':cleanData,
        'columnData':columnData,
      },context_instance=RequestContext(request) )

def genColumnData():
    output = ""
    for wave_tuple in WAVE_TYPES:
      output += "table.addColumn('number', '" + wave_tuple[1] + "');\n"
    return output

def cleanString(data):
  output = "[\n" 
  for row in data:
     output += "["
     for cell in row:
        output += str(cell) + ","
     output += "],\n"
  output = output + "]"
  return output


