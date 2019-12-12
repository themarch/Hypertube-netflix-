import requests
import bs4
from video.models import Torrent
from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        i = 1
        while i < 10:
            address = 'https://yts.lt/browse-movies?page=' + str(i)
            result = requests.get(address)
            try :
                    result.raise_for_status()
            except Exception as exc:
                    print('There was a problem: %s' %(exc))
            poupou = bs4.BeautifulSoup(result.text, features="lxml")
            section = poupou.find('section')
            film = []  
            row = section.find('div', class_='row')
            div = row.find_all('div', class_='browse-movie-wrap')
            for di in div:
                a = di.find('a', class_='browse-movie-link')
                img = di.find('img', class_='img-responsive')
                img_alt = img['alt']
                img_alt = img_alt.replace(' download', '')
                film.append([a['href'], img_alt, img['src']])
                print(img_alt)
            for f in film:
                    video = requests.get(f[0])
                    try :
                        result.raise_for_status()
                    except Exception as exc:
                        print('There was a problem: %s' %(exc))
                    vid = bs4.BeautifulSoup(video.text, features='lxml')
                    info = vid.find('div', id='movie-info')
                    if info:
                        torrent = Torrent()
                        torrent.name = f[1]
                        torrent.miniature = f[2]
                        info2 = info.find_all('h2')
                        torrent.release = info2[0].text
                        if info2[1].text:
                            cat = info2[1].text.split('/')
                            torrent.category = json.dumps({'category' : cat})
                        imdbid = vid.find('a', title="IMDb Rating")
                        imdbid = imdbid['href'].replace('https://www.imdb.com/title/', '')
                        imdbid = imdbid.replace('/', '')
                        torrent.idimdb = imdbid
                        print(imdbid)
                        rate = vid.find('span', itemprop="ratingValue").text
                        torrent.rate = rate
                        f.append([float(rate)])
                        torrentlk = vid.find('a', class_='magnet-download')
                        torrent.magnets= torrentlk['href']
                        syn = vid.find('div', id='synopsis')
                        if syn:
                            torrent.synopsis = syn.find('p').text
                        direct = vid.find('div', id='crew')
                        if direct:
                            director = direct.find('span', itemprop='name')
                            if director:
                                torrent.director = director.text
                            actor = direct.find('div', class_='actors')
                            if actor:
                                ac = []
                                actors = actor.find_all('span', itemprop='name')
                                if actors:
                                    for act in actors:
                                        ac.append(act.text)
                                    torrent.actors = json.dumps({'actors' : ac })
                        torrent.serie = False
                        torrent.save()
            i = i + 1
