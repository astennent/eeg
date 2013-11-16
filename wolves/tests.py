import requests
import urllib2, base64
# Should use HTTPBasicAuth
# r = requests.get("url", auth=HTTPBasicAuth(username, password))

# Ping the server with an invalid user/pass
username = "notauser"
password = "password"
payload= { 'HTTP_AUTHORIZATION' : base64.encodestring('%s:%s' % (username, password)), }
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/ping', data=payload)
print r.text
assert(r.json()['message'] == "Error: Invalid Login Credentials")

# Ping the server with a valid username and password
username = "astennent"
password = "password"
payload= { 	'HTTP_AUTHORIZATION' : base64.encodestring('%s:%s' % (username, password)), }
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/ping', data=payload)
print r.text
assert(r.json()['message'] == "success")

username = "testuser"
password = "werewolf"
userpass1 = base64.encodestring('%s:%s' % (username, password))
payload = { 'HTTP_AUTHORIZATION' : userpass1, }

# Delete the user if it exists 
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/delete_account', data=payload)
# Create a new user
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/create_account', data=payload)
assert(r.json()['message'] == "success")

# Create a new game
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/create_game', data=payload)
print r.text
assert(r.json()['message'] == "success")

# Use the returned game_id and player_id for later tests
game_id = r.json()['game_id']
player_id1 = r.json()['player_id']
payload['game_id'] = game_id


# Attempt to re-join the game you just created.
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/join_game', data=payload)
print r.text
assert(r.json()['message'] == "Error: You've already joined that game")


# Create another user and join the game.
username = "testuser2"
password = "werewolf"
userpass2 = base64.encodestring('%s:%s' % (username, password))
payload['HTTP_AUTHORIZATION'] = userpass2
# Delete the user if it exists 
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/delete_account', data=payload)
# Create the user
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/create_account', data=payload)
assert(r.json()['message'] == "success")
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/join_game', data=payload)
print r.text
assert(r.json()['message'] == "success")


# Use the returned player_id 
player_id2 = r.json()['player_id']


# Attempt to restart the game without being the administrator
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/restart_game', data=payload)
print r.text
assert(r.json()['message'] == "Error: You are not the administrator")


# Switch to the administrator, restart the game.
payload['HTTP_AUTHORIZATION'] = userpass1
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/restart_game', data=payload)
print r.text
assert(r.json()['message'] == "success")


# Move the first player to a new position
payload['latitude'] = 5
payload['longitude'] = 5
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/post_position', data=payload)
print r.text
assert(r.json()['message'] == "success")


# Get the votable players for player 1 (this should only be player 2)
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/get_votable_players', data=payload)
print r.text
assert(r.json()['votable_players'] == "["+str(player_id2)+"]")


# Have player 1 vote for player 2.
payload['votee_id'] = player_id2
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/place_vote', data=payload)
print r.text
assert(r.json()['message'] == "success")


# Have player 1 attempt to kill player 2. Note that it is currently out of range.
payload['victim_id'] = player_id2
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/kill', data=payload)
print r.text
assert(r.json()['message'] == "Error: Victim out of range")


# Move the first player closer to player 2 and kill him
payload['latitude'] = 2
payload['longitude'] = 2
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/post_position', data=payload)
assert(r.json()['message'] == "success")
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/kill', data=payload)
print r.text
assert(r.json()['message'] == "success")


# Have player 1 attempt to kill the now dead player 2
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/kill', data=payload)
print r.text
assert(r.json()['message'] == "Error: Invalid target")


# Restart the game and have player 1 kill player 2 again.
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/restart_game', data=payload)
assert(r.json()['message'] == "success")
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/kill', data=payload)
print r.text
assert(r.json()['message'] == "success")


# Get the highscore list
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/get_highscores', data=payload)
print r.text
assert('highscores' in r.json())

# Clean up. These deletes cascade, so all test data is removed by removing users.
payload = { 'HTTP_AUTHORIZATION' : userpass1, }
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/delete_account', data=payload)
payload = { 'HTTP_AUTHORIZATION' : userpass2, }
r = requests.post(r'http://ec2-54-235-36-112.compute-1.amazonaws.com/wolves/delete_account', data=payload)



print("All tests passed!")