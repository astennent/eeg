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
    

def respond(response_data):
    return respond_with_method(response_data, "X")

# Helper method for returning json responses
def respond_with_method(response_data, response_method):
    if isinstance(response_data, str):
        data = {"message":response_data, "method":response_method,}
    else:
        data = response_data
        if "message" not in data:
            data["message"] = "success"
        if "method" not in data:
            data["method"] = response_method 

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
    badges = account.badges.values("tag",)

    response_data = {
        "badges" : list(badges),
        "experience" : account.experience,
        "kills" : Kill.objects.filter(killer__account = account).count()
    }

    return respond(response_data)

@csrf_exempt
def get_games_data(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")

    account = Account.objects.get(user = user)

    players = Player.objects.filter(account=account).order_by("-game__start_time").values(
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
# Returns the game information for a single game. Expects a game_id paramter.
def get_game_data(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")

    game = validate_game(request)
    if game == None:
        return respond("Game does not exist")

    account = Account.objects.get(user = user)
    player = Player.objects.get(account__user=user, game=game)

    is_day = game.is_day()
    num_wolves = game.count_living_wolves()
    num_villagers = game.count_living_villagers()
    minutes_remaining = game.minutes_remaining()

    # Get the list of votable players, and who you voted for
    actions = {}
    if is_day:
        voted_player = player.vote
        if voted_player:
            voted = True
            your_vote = str(voted_player.account)
        else:
            voted = False
            your_vote = None

        actions["your_vote"] = your_vote
        actions["voted"] = voted

    elif player.is_wolf:
        actions["killable_players"] = game.get_killable_players(player)
        actions["smellable_players"] = game.get_smellable_players(player)
    
    actions["all_players"] = game.get_all_players(player)

    response_data = {
        "is_day" : is_day,
        "num_wolves" : num_wolves,
        "num_villagers" : num_villagers,
        "minutes_remaining" : minutes_remaining,
        "actions" : actions,
        "game_name" : game.name,
        "player_is_wolf" : player.is_wolf,
    }

    return respond_with_method(response_data, "get_game_data")


@csrf_exempt
# TODO: Honor settings in request
def create_game(request):
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")

    account = Account.objects.get(user=user)

    name = request.POST['name'];
    cycle_length = request.POST['cycle_length'];
    scent_range = request.POST['scent_range'];
    kill_range = request.POST['kill_range'];    

    game = Game(administrator=account, name=name, 
        cycle_length=cycle_length, scent_range=scent_range, kill_range=kill_range)
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
    return respond_with_method("success", "place_vote")


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


@csrf_exempt
def smell(request): 
    user = validate_mobile(request)
    if user == None:
        return respond("Incorrect Username or Password")
    
    try:
        game = Game.objects.get(id=request.POST['game_id'])
    except:
        return respond("Game does not exist")
    
    try:
        smeller = Player.objects.get(account__user=user, game=game)
    except:
        return respond("No player in game")

    try:
        victim = Player.objects.get(id=request.POST['victim_id'])
        assert(victim.is_wolf == False)
        assert(victim.is_dead == False)
        assert(smeller.is_wolf == True)
    except:
        return respond("Invalid target") 

    response_data = {
        "smell_distance" : smeller.distance_to(victim),
        "in_smell_range" : smeller.in_scent_range(victim),
    }
    return respond_with_method(response_data, "smell")


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
        assert(victim.is_wolf == False)
        assert(victim.is_dead == False)
        assert(killer.is_wolf == True)
    except:
        return respond("Invalid target")

    if killer.in_kill_range(victim):
        kill = killer.kill(victim)
    else:
        return respond("Victim out of range")

    response_data = {
        "kill": kill.dictify(), 
        "message":"success",
    }
    return respond_with_method(response_data, "kill")


        

     


     

