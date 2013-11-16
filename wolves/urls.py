from django.conf.urls.defaults import *

urlpatterns = patterns('wolves.views',
    url(r'^ping$', 'ping'),
    url(r'^create_account$', 'create_account'),
    url(r'^delete_account$', 'delete_account'),
    url(r'^create_game$', 'create_game'),
    url(r'^join_game$', 'join_game'),  
    url(r'^restart_game$', 'restart_game'),
    url(r'^post_position$', 'post_position'),
    url(r'^get_votable_players$', 'get_votable_players'),
    url(r'^place_vote$', 'place_vote'),
    url(r'^get_highscores$', 'get_highscores'),
    url(r'^kill$', 'kill'),
    url(r'get_killable_players', 'get_killable_players'),
)
