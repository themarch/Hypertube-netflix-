from django.db import models
import json 

class Torrent(models.Model):
    name = models.CharField(max_length=300, blank=True)
    content = models.FileField(upload_to="torrents/torrents", blank=True,)
    miniature = models.URLField()
    magnets = models.URLField()
    release = models.IntegerField(blank=True)
    category = models.CharField(max_length=300, blank=True)
    rate = models.FloatField(blank=True)
    synopsis = models.TextField(blank=True)
    director = models.CharField(max_length=300, blank=True)
    actors = models.TextField(blank=True)
    movie_length = models.CharField(max_length=300, blank=True)
    language = models.CharField(max_length=300, blank=True)
    dlPath = models.CharField(max_length=300, blank=True)
    comments = models.TextField(blank=True)
    serie = models.BooleanField()
    episodes = models.TextField(blank=True)
    seasons = models.CharField(max_length=4, blank=True)
    idimdb = models.CharField(max_length=10, blank=True)
    watch_date = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f'{self.name} Torrent'