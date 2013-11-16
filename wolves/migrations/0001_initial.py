# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Badge'
        db.create_table(u'wolves_badge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=63)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=127)),
            ('points', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'wolves', ['Badge'])

        # Adding model 'Game'
        db.create_table(u'wolves_game', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_time', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('cycle_length', self.gf('django.db.models.fields.IntegerField')(default=1800)),
            ('in_progress', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=31, null=True, blank=True)),
        ))
        db.send_create_signal(u'wolves', ['Game'])

        # Adding model 'Account'
        db.create_table(u'wolves_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['auth.User'])),
            ('experience', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'wolves', ['Account'])

        # Adding M2M table for field badges on 'Account'
        m2m_table_name = db.shorten_name(u'wolves_account_badges')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm[u'wolves.account'], null=False)),
            ('badge', models.ForeignKey(orm[u'wolves.badge'], null=False))
        ))
        db.create_unique(m2m_table_name, ['account_id', 'badge_id'])

        # Adding model 'Player'
        db.create_table(u'wolves_player', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wolves.Account'])),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wolves.Game'])),
            ('is_dead', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_wolf', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('vote', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wolves.Player'], null=True, blank=True)),
        ))
        db.send_create_signal(u'wolves', ['Player'])

        # Adding model 'Kill'
        db.create_table(u'wolves_kill', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('killer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='kill-killer', to=orm['wolves.Player'])),
            ('victim', self.gf('django.db.models.fields.related.ForeignKey')(related_name='kill-victim', to=orm['wolves.Player'])),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('time', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'wolves', ['Kill'])


    def backwards(self, orm):
        # Deleting model 'Badge'
        db.delete_table(u'wolves_badge')

        # Deleting model 'Game'
        db.delete_table(u'wolves_game')

        # Deleting model 'Account'
        db.delete_table(u'wolves_account')

        # Removing M2M table for field badges on 'Account'
        db.delete_table(db.shorten_name(u'wolves_account_badges'))

        # Deleting model 'Player'
        db.delete_table(u'wolves_player')

        # Deleting model 'Kill'
        db.delete_table(u'wolves_kill')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'wolves.account': {
            'Meta': {'object_name': 'Account'},
            'badges': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['wolves.Badge']", 'symmetrical': 'False', 'blank': 'True'}),
            'experience': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['auth.User']"})
        },
        u'wolves.badge': {
            'Meta': {'object_name': 'Badge'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '127'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '63'}),
            'points': ('django.db.models.fields.IntegerField', [], {})
        },
        u'wolves.game': {
            'Meta': {'object_name': 'Game'},
            'cycle_length': ('django.db.models.fields.IntegerField', [], {'default': '1800'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_progress': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '31', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'wolves.kill': {
            'Meta': {'object_name': 'Kill'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'killer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'kill-killer'", 'to': u"orm['wolves.Player']"}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'time': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'victim': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'kill-victim'", 'to': u"orm['wolves.Player']"})
        },
        u'wolves.player': {
            'Meta': {'object_name': 'Player'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wolves.Account']"}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wolves.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_dead': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_wolf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['wolves.Player']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['wolves']