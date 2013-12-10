from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
import math #for distance calculations

class Badge(models.Model):
    tag = models.PositiveIntegerField(unique=True) # used as a more controllable ID.
    name = models.CharField(max_length=63)
    description = models.CharField(max_length=127)
    points = models.IntegerField()

    def __unicode__(self):
        return str(self.name)


class Account(models.Model):
    user = models.ForeignKey(User, related_name='+') #use the django admin user
    badges = models.ManyToManyField(Badge, blank=True)
    experience = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __unicode__(self):
        return str(self.user)


class Game(models.Model):
    start_time = models.DateTimeField(auto_now_add=True) #use current time.
    cycle_length = models.IntegerField(default=720) #12 hours
    in_progress = models.BooleanField(default=True)
    name = models.CharField(max_length=31, null=True, blank=True)
    administrator = models.ForeignKey(Account, related_name="game_admin", null=True)    
    kill_range = models.FloatField(default=0.5) #TODO: Lookup how big gps coords are
    scent_range = models.FloatField(default=1.0)
    public = models.BooleanField(default=True)
 
    def __unicode__(self):
        if self.name:
            return str(self.name) + " (" + str(self.id) + ")"
        else:
            return "<Unnamed Game> (" + str(self.id) + ")"
    
    def add_player(self, account):
        player = Player(account=account, game=self)
        player.save()
        return player

    def restart(self):
        # Restore dead players and clear their current votes
        players = Player.objects.filter(game = self).order_by('?')
        wolf_count = len(players)/3
        for player in players:
            player.vote = None
            player.is_dead = False
            if (wolf_count > 0):
                wolf_count -= 1
                player.is_wolf = True
            else:
                player.is_wolf = False
            player.save()
        self.in_progress = True
        self.start_time = datetime.now()
        self.save()

    def get_all_players(self, asker):
        players_in_game = Player.objects.filter(game=self).exclude(id=asker.id)
        all_players = []
        for player in players_in_game:
            all_players.append(player.dictify(asker.is_wolf))
        return all_players 
    
    def get_killable_players(self, asker):
        players_in_game = Player.objects.filter(game=self, is_dead=False, is_wolf=False).exclude(id=asker.id)
        players_in_range = []
        for player in players_in_game:
             if asker.in_kill_range(player):
                 players_in_range.append(player.dictify(asker.is_wolf))
        return players_in_range

    def get_smellable_players(self, asker):
        players_in_game = Player.objects.filter(game=self, is_dead=False, is_wolf=False).exclude(id=asker.id)
        players_in_range = []
        for player in players_in_game:
             if asker.in_scent_range(player):
                 players_in_range.append(player.dictify(asker.is_wolf))
        return players_in_range


    def get_all_kills(self):
        all_kills = Kill.objects.filter(killer__game=self)
        kills = []
        for kill in all_kills:
            if kill.killer == None:
                killer = None
            else:
                killer = str(kill.killer.account);
            kills.append({
                "killer" : killer,
                "victim" : str(kill.victim.account),
                "time" : str(kill.time),
                })
        return kills

    def is_day(self):
        minutes_passed = (timezone.now() - self.start_time).seconds / 60
        num_cycles = minutes_passed / self.cycle_length
        return (num_cycles % 2 == 0)

    # Calculates the minutes until the day/night shift.
    def minutes_remaining(self):
        minutes_passed = (timezone.now() - self.start_time).seconds / 60
        return self.cycle_length - (minutes_passed % self.cycle_length)


    def count_living_wolves(self):
        return Player.objects.filter(game=self, is_dead=False, is_wolf=True).count()

    def count_living_villagers(self):
        return Player.objects.filter(game=self, is_dead=False, is_wolf=False).count()

    def check_game_over(self):
        if self.count_living_villagers() == 0 or self.count_living_wolves == 0:
            in_progress = False

    def toggle_cycle(self):
        if is_day(self): # switch to day. 
            pass #TODO: Anything?
        else: # switch to night.
            players = Player.objects.filter(game=self).order_by('?')
            highest_vote_count = 0
            highest_vote_player = players[0]
            
            for player in players:
                vote_count = Player.objects.filter(vote=player).count()
                if vote_count > highest_vote_count:
                    highest_vote_count = vote_count
                    highest_vote_player = player

            # kill the highest voted player.
            highest_vote_player.is_dead = True
            highest_vote_player.save()

            # record the kill for posterity.
            hangman_kill = Kill(victim=highest_vote_player, 
                latitude=highest_vote_player.account.latitude, 
                longitude=highest_vote_player.account.longitude)
            hangman_kill.save()

class Player(models.Model):
    account = models.ForeignKey(Account)
    game = models.ForeignKey(Game)
    is_dead = models.BooleanField(default=False)
    is_wolf = models.BooleanField(default=False)
    vote = models.ForeignKey('self', null=True, blank=True) #reset to null at the start of the day cycle.

    def __unicode__(self):
        return str(self.account) + " (" + str(self.id) + ")"

    def in_kill_range(self, other):
        distance = self.distance_to(other)
        return distance <= self.game.kill_range
          
    def in_scent_range(self, other):
        distance = self.distance_to(other)
        return distance <= self.game.scent_range
     
    def distance_to(self, other):
        distance = math.sqrt( float((self.account.latitude-other.account.latitude))**2 + float((self.account.longitude-other.account.longitude))**2 )
        return distance

    def kill(self, other):
        self.account.experience += 5
        self.account.save()
        other.is_dead = True
        other.save()
        kill = Kill(killer=self, victim=other, latitude=other.account.latitude, longitude=other.account.longitude)
        kill.save()
        self.game.check_game_over()
        return kill

    # Converts the player to something that can be seen by others. 
    # Wolf perspective allows you to see if the player is a wolf.
    def dictify(self, wolf_perspective):
        if wolf_perspective:
            if self.is_wolf:
                wolf_identifier = 1
            else:
                wolf_identifier = 0
        else:
            wolf_identifier = -1
        return {
            "wolf_identifier" : wolf_identifier,
            "name" : str(self.account),
            "id" : self.id,
            "is_dead" : self.is_dead,
        }


class Kill(models.Model):
    killer = models.ForeignKey(Player, related_name="kill-killer", null=True, blank=True)
    victim = models.ForeignKey(Player, related_name="kill-victim")
    latitude = models.FloatField() #these are victim's coordinates
    longitude = models.FloatField()
    time = models.DateField(auto_now_add=True)

class PendingBadge(models.Model):
    account = models.ForeignKey(Account)
    badge = models.ForeignKey(Badge)