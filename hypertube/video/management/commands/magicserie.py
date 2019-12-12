import requests
import bs4
from video.models import Torrent
from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        address = 'https://www.imdb.com/chart/toptv?ref_=helpms_ih_gi_siteindex'
        result = requests.get(address)
        try :
            result.raise_for_status()
        except Exception as exc:
            print('There was a problem: %s' %(exc))
        poupou = bs4.BeautifulSoup(result.text, features="lxml")
        prou = poupou.find('tbody')
        a = prou.find_all('a')
        link = []
        for b in a:
            add = b['href'].replace('/title', '')
            link.append('https://tv-v2.api-fetch.website/show' + add)
        link = list(set(link))
        print(link)
        for l in link:
            serie = requests.get(l).json()
            if serie:
                torrent = Torrent()
                torrent.name = serie['title'] + ' (' + serie['year'] + ')'
                print(serie['title'])
                if 'images' in serie and 'banner' in serie['images']:
                    torrent.miniature = serie['images']['banner']
                torrent.magnets = json.dumps(serie['episodes'])
                torrent.release = serie['year']
                torrent.idimdb = serie['_id']
                torrent.category =  json.dumps({'category' : serie['genres']})
                torrent.rate = float(serie['rating']['percentage'] * 10 / 100)
                torrent.synopsis = serie['synopsis']
                torrent.movie_length = serie['runtime']
                torrent.serie = True
                torrent.episodes = json.dumps(serie['episodes'])
                torrent.seasons = serie['num_seasons']
                torrent.save()
