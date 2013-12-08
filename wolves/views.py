from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt #for POST requests from mobile devices that couldn't have gotten a csrf token.
from django.contrib.auth.models import User
from models import *

import json
import base64
from django.contrib.auth import authenticate, login

@csrf_exempt # allows POST requests without a csrf token
def ping(request):
    if not validate_mobile(request):
        return respond('Invalid Login Credentials')
    return respond("success")


# Called whenever a mobile request is sent which requires authentication
def validate_mobile(request):
    try:
        username, password = base64.b64decode(request.POST['HTTP_AUTHORIZATION']).split(":")
    except:
        return None
    return authenticate(username=username, password=password)

def validate_game(request):
    try:
        return Game.objects.get(id=request.POST['game_id'])
    except:
        return None
    

# Helper method for returning json responses
def respond(response_data):
    if isinstance(response_data, str):
        data = {"message":response_data}
    else:
        data = response_data
        if "message" not in data:
            data["message"] = "success" 

    json_dump = json.dumps(data)
    return HttpResponse(json_dump, content_type="application/json")


@csrf_exempt
def create_account(request):
    username, password = base64.b64decode(request.POST['HTTP_AUTHORIZATION']).split(":")
    if User.objects.filter(username=username).count() > 0:
        return respond("Username already taken")
    new_user = User.objects.create_user(username, '', password)
    new_account = Account(user=new_user)
    new_account.save()
    return respond("success")


@csrf_exempt
# TODO: Transfer administrator status to active games
def delete_account(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
    user.delete()
    return respond("success")


@csrf_exempt
def get_account_data(request):
    user = validate_mobile(request)

    account = Account.objects.get(user = user)
    players = Player.objects.filter(account=account).order_by("game__start_time").values(
        "game__id",
        "game__name",
        "game__in_progress",
        "is_wolf", 
        "is_dead",
    )

    badges = account.badges.values("tag",)

    response_data = {
        "players" : list(players),
        "badges" : list(badges),
        "experience" : account.experience,
        "kills" : Kill.objects.filter(killer__account = account).count()
    }

    return respond(response_data)

@csrf_exempt
def get_games_data(request):
    user = validate_mobile(request)

    account = Account.objects.get(user = user)
    
    players = Player.objects.filter(account=account).order_by("game__start_time").values(
        "game__id",
        "game__name",
        "game__in_progress",
        "is_wolf", 
        "is_dead",
    )

    response_data = {
        "players" : list(players),
    }

    return respond(response_data)


@csrf_exempt
# TODO: Honor settings in request
def create_game(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")

    account = Account.objects.get(user=user)
    game = Game(administrator=account)
    game.save()
    player = game.add_player(account) 
    response_data = {
        "message":"success",
        "game_id":game.id,
        "player_id":player.id,
    }
    return respond(response_data)


@csrf_exempt
def join_game(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")

    game = validate_game(request)
    if game == None:
        return respond("Game does not exist")
    
    if len(Player.objects.filter(account__user=user, game=game)) > 0:
        return respond("You've already joined that game")
    
    player = game.add_player(Account.objects.get(user=user))
    response_data = {
        "message":"success",
        "player_id":player.id,
    }
    return respond(response_data)


@csrf_exempt
def restart_game(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")

    account = Account.objects.get(user=user)

    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")

    if game.administrator != account:
        return respond("You are not the administrator")

    game.restart()
    return respond("success")


@csrf_exempt
def post_position(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
     
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")
    
    try:
        player = Player.objects.get(account__user=user, game=game)
    except:
        return respond("No player in game")

    try:
        player.latitude = request.POST['latitude']
        player.longitude = request.POST['longitude']
    except:
        return respond("Invalid position")

    player.save()
    return respond("success")


@csrf_exempt
def get_votable_players(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
     
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")
     
    try:
        player = Player.objects.get(account__user=user, game=game)
    except:
        return respond("No player in game")
    
    votable_players = str(game.get_votable_players(player)) #Return a list

    response_data = {
        'votable_players':votable_players,
    }
    return respond(response_data)

@csrf_exempt
def place_vote(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
     
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")

    try:
        voter = Player.objects.get(account__user=user, game=game)
    except:
        return respond("No player in game")
    
    try:
        votee = Player.objects.get(id=request.POST['votee_id'])
    except:
        return respond("Player not found.")

    if votee == voter:
        return respond("You cannot vote for yourself")

    if votee.game != voter.game:
        return respond("Players cannot vote outside of their game.")

    voter.vote = votee
    voter.save()
    return respond("success")


@csrf_exempt
# TODO: Order this and include more information (#games, win% etc)
def get_highscores(request):
    top_accounts = Account.objects.all().order_by('experience')[:10]
    highscores = {}
    for account in top_accounts:
        highscores[str(account.user)] = account.experience
    return respond({'highscores':highscores})
   

@csrf_exempt
def get_smellable_players(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Invalid Login Credentials")
     
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")
     
    smellable_players = str(game.get_smellable_players(player)) #Return a list
    response_data = {
        'smellable_players':smellable_players,
    }
    return respond(response_data)

#TODO: Write test cases for smellable and killable
 
@csrf_exempt
def get_killable_players(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
     
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")
     
    killable_players = str(game.get_killable_players(player)) #Return a list
    response_data = {
        'killable_players':killable_players,
    }
    return respond(response_data)

@csrf_exempt
def kill(request): 
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
    
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")
    
    try:
        killer = Player.objects.get(account__user=user, game=game)
    except:
        return respond("No player in game")
    
    try:
        victim = Player.objects.get(id=request.POST['victim_id'])
        assert(victim.game.id == killer.game.id)
        assert(victim.is_wolf == False)
        assert(victim.is_dead == False)
        #assert(killer.is_wolf) #Temporarily disabled for testing. 
    except:
        return respond("Invalid target")

    if killer.in_kill_range(victim):
        kill = killer.kill(victim)
    else:
        return respond("Victim out of range")

    response_data = {
        "kill": str(kill), #TODO: write serialization methods
        "message":"success",
    }
    return respond(response_data)


        

     


     

