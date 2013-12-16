from django.template import Template
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime

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


def create_account(username, password):
    if User.objects.filter(username=username).count() > 0:
        return respond("Invalid Username or Password")
    new_user = User.objects.create_user(username, '', password)
    return respond("success")


def respond(message):
    json_dump = json.dumps({"message":message})
    return HttpResponse(json_dump, content_type="application/json")

@csrf_exempt
def check_login(request):
    
    # The user/pass exists.
    user = validate_mobile(request)
    
    if user == None:
      try:
        username, password = base64.b64decode(request.POST['HTTP_AUTHORIZATION']).split(":")
        return create_account(username, password)
      except:
        return respond("Invalid username or password format")

 
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
    time = datetime.now()

    expected_names = ["HIGHALPHA", "HIGHBETA", "MIDGAMMA", 
        "LOWALPHA", "LOWBETA", "LOWGAMMA", "DELTA", "THETA"]

    for wave_id, name in enumerate(expected_names):
        if name in request.POST:
            dp = DataPoint(user=user, value=request.POST[name], wave=wave_id+1, time=time)
            dp.save()

    emotion = request.POST["EMOTION"]
    if emotion != "":
       save_emotion(user, emotion, time)
      
def save_emotion(user, emotion, time):
   for current_emotion in EMOTIONS:
      if current_emotion[1] == emotion:
         ep = EmotionPoint(user=user, emotion=current_emotion[0], time=time)
         ep.save()

def chart(request):
    columnData = genColumnData()
    chartData = genChartData(2)
    users = User.objects.all()
    
    return render_to_response('eeg/chart.html', {
        'data':chartData,
        'columnData':columnData,
        'users':users,
      },context_instance=RequestContext(request) )


def genChartData(user_id):
    # TODO: Paramaters from chart page
    if user_id == '0':
      data_points = DataPoint.objects.all().order_by('time')
    else:
      data_points = DataPoint.objects.filter(user=user_id).order_by('time')
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

        # for emotion.
        row.append("undefined")
        row.append("undefined")

        # Try to add the emotion if this is the first time seeing the datetime.
        emotion_points = EmotionPoint.objects.filter(time=point.time)
        all_emotions = EmotionPoint.objects.all().order_by('time').values('time')
        if len(emotion_points) > 0: # There should be 0 or 1 points here. Extras are ignored.
          emotion_point = emotion_points[0]
          column_index = len(WAVE_TYPES)+1
          row[column_index] = 1
          row[column_index+1] = '"'+EMOTIONS[emotion_point.emotion-1][1]+'"' # ("Happy", etc.)

      row[point.wave] = point.value
      last_row = row

    cleanData = cleanString(data)
    return cleanData


def genColumnData():
    output = ""
    for wave_tuple in WAVE_TYPES:
      output += "table.addColumn('number', '" + wave_tuple[1] + "');\n"
          
    output += "table.addColumn('number', 'Emotion');\n"
    output += "table.addColumn('string', 'Emotion Name');\n"

    return output

# Takes a 2d array and converts it to a string without quotes on string values
def cleanString(data):
   output = "[\n" 
   for row in data:
      output += "["
      for cell in row:
         output += str(cell) + ","
      output += "],\n"
   output = output + "]"
   return output

# returns a json {message:"data as string"} response
@csrf_exempt
def fetch_data(request):
   user_id = request.POST['user_id']
   chartData = genChartData(user_id)
   return render_to_response('eeg/fetchData.html', {
        'chartData':chartData,
      },context_instance=RequestContext(request) )
