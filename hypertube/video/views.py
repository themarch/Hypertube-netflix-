from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
import requests, json
from django.contrib.auth import authenticate, login
from django.contrib import messages
from video.models import Torrent
from django.utils.html import escape
import sys, webbrowser, bs4
import time, urllib.request
from .forms import CommentForm
from django.http import HttpRequest, JsonResponse
from django.db.models import Q, query
from users.models import Profile
import uuid

@login_required
def list(request):
    #get token to 42
    if request.GET.get('code'):
        code = request.GET.get('code')
        data = {'grant_type': 'authorization_code', 'client_id': '5123688fe53d089acd8fb1f9bf1bd437e8d4f3628dc5d79b033b357deafbb01a', 'client_secret': '3ede04d9a435c18f69ae2c9e0e91fc486c38349327418f49e7b6910da663903b', 'code': code, 'redirect_uri': 'http://localhost:8000'}
        access_token_response = requests.post("https://api.intra.42.fr/oauth/token", data=data)
        access = json.loads(access_token_response.text)
    #data user access
        headers = {"Authorization": 'Bearer ' + str(access['access_token'])}
        req = requests.post('http://api.intra.42.fr/v2/me', headers=headers)
        content = json.loads(req.text)
        if content and 'id' in content:
            if not User.objects.filter(username=content['login']):
                user = User.objects.create_user(content['login'], email=content['email'], password="", first_name=content['first_name'], last_name=content['last_name'])
                token = Token.objects.create(user=user)
    #log user with token
            else:
                user = User.objects.get(username=content['login'])
                print(user)
            userlog = authenticate(request, username=content['login'], password='')
            if userlog is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        else:
            messages.error(request, f'Bad Response HA HA HA')
            return redirect('login')
        return redirect('list')
    inshalah = request.POST.get('tok')
    if request.method == 'POST' and 'tok' in request.POST:
        name = request.user
        id_profile = User.objects.get(username=name).pk
        token = Profile.objects.get(id=id_profile)
        token.token = ''
        token.save()
    req = request.POST.get('val')
    if req :
        filters = req.split(' ')
        print(filters)
        if not '|' in filters :
            if filters[0] == 'release' or filters[0] == 'rate':
                filters[0] = '-' + filters[0]
                movies = Torrent.objects.filter(category__contains=filters[1], rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1] 
            else: 
                movies = Torrent.objects.filter(category__contains=filters[1], rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1] 
        elif filters[1] == '|':
            if filters[0] == 'release' or filters[0] == 'rate':
                filters[0] = '-' + filters[0]
                movies = Torrent.objects.filter(rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1] 
            else: 
                movies = Torrent.objects.filter(rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1] 
        return JsonResponse({'movie' : movies})
    else:
        movies = Torrent.objects.order_by('-rate').values()
        genre = []
        tab = []
        name = request.user
        id_profile = User.objects.get(username=name).pk
        bd_already = Profile.objects.filter(id=id_profile).first()
        trysplit = bd_already.already.split()
        for notes in movies:
            cat = notes['category']
            id_gris = notes['id']
            id_gris = str(id_gris)
            for aff in trysplit:
                if (aff == id_gris):
                    tab.append(int(aff))
            if cat:
                cat = json.loads(notes['category'])
                for c in cat:
                    if not c in genre:
                        genre.append(c)
        return render(request, 'video/list.html', {'movies' : movies, 'genre' : genre, 'grey' : tab})

@login_required
def search(request):
    inshalah = request.POST.get('tok')
    if request.method == 'POST' and 'tok' in request.POST:
        name = request.user
        id_profile = User.objects.get(username=name).pk
        token = Profile.objects.get(id=id_profile)
        token.token = ''
        token.save()
    if request.method == 'POST' and not 'val' in request.POST:
        film_search = request.POST["film_search"]
        film_search = escape(film_search)
        film_search = film_search.replace(' ', '%20')
        film_search = film_search.strip()
        address = 'https://yts.lt/browse-movies/' + film_search + '/all/all/0/latest'
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
        for f in film:
            video = requests.get(f[0])
            try :
                result.raise_for_status()
            except Exception as exc:
                print('There was a problem: %s' %(exc))
            vid = bs4.BeautifulSoup(video.text, features='lxml')
            info = vid.find('div', id='movie-info')
            if (info):
                info2 = info.find_all('h2')
                rate = vid.find('span', itemprop="ratingValue").text
                f.append(rate)
                if not Torrent.objects.filter(name = f[1]):
                    torrent = Torrent()
                    torrent.name = f[1]
                    torrent.miniature = f[2]
                    torrent.release = info2[0].text
                    category = info2[1].text
                    cat = category.split('/')
                    torrent.category = json.dumps({'category' : cat})
                    imdbid = vid.find('a', title="IMDb Rating")
                    imdbid = imdbid['href'].replace('https://www.imdb.com/title/', '')
                    imdbid = imdbid.replace('/', '')
                    torrent.idimdb = imdbid
                    print(imdbid)
                    torrent.rate = float(rate)
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
                mov = Torrent.objects.only('id').get(name=f[1]).id
                s = Torrent.objects.only('serie').get(name=f[1]).serie
                f.append(mov)
                f.append(s)
        address = 'https://www.imdb.com/find?q=' + film_search + '&s=tt&ttype=tv&exact=true&ref_=fn_tt_ex'
        result = requests.get(address)
        try :
            result.raise_for_status()
        except Exception as exc:
            print('There was a problem: %s' %(exc))
        poupou = bs4.BeautifulSoup(result.text, features="lxml")
        prou = poupou.find('table')
        if prou:
            a = prou.find_all('a')
            if (a):
                blink = []
                for b in a:
                    add = b['href'].replace('/title', '')
                    link = 'https://tv-v2.api-fetch.website/show' + add
                    if not link in blink:
                        blink.append(link)
                for l in blink:
                    serie = requests.get(l).json()
                    if serie and not Torrent.objects.filter(name = serie['title'] + ' (' + serie['year'] + ')') and not serie['title'] + ' (' + serie['year'] + ')' in film:
                        torrent = Torrent()
                        torrent.name = serie['title'] + ' (' + serie['year'] + ')'
                        if 'images' in serie and 'banner' in serie['images']:
                            torrent.miniature = serie['images']['banner']
                        torrent.magnets = json.dumps(serie['episodes'])
                        torrent.release = serie['year']
                        torrent.category =  json.dumps({'category' : serie['genres']})
                        torrent.rate = float(serie['rating']['percentage'] * 10 / 100)
                        torrent.synopsis = serie['synopsis']
                        torrent.movie_length = serie['runtime']
                        torrent.serie = True
                        torrent.episodes = json.dumps(serie['episodes'])
                        torrent.idimdb = serie['_id']
                        torrent.seasons = serie['num_seasons']
                        torrent.save()
                        mov = Torrent.objects.only('id').get(name = serie['title'] + ' (' + serie['year'] + ')').id
                        film.append(['rien', torrent.name, torrent.miniature, torrent.rate, mov, torrent.serie])
                    elif serie:
                        name = serie['title'] + ' (' + serie['year'] + ')'
                        if not name in film:
                            miniature = serie['images']['banner']
                            rate = float(serie['rating']['percentage'] * 10 / 100)
                            mov = Torrent.objects.only('id').get(name = name).id
                            film.append(['rien', name, miniature, rate, mov, True])
        genre = []
        search = []
        for notes in film:
            toto = Torrent.objects.get(name=notes[1])
            search.append(toto.pk)
            cat = json.loads(toto.category)
            ca = cat['category']
            for c in ca:
                if not c in genre:
                    genre.append(c)
        request.session['search'] = search
    req = request.POST.get('val')
    if req :
        filters = req.split(' ')
        if not '|' in filters :
            if filters[0] == 'release' or filters[0] == 'rate':
                filters[0] = '-' + filters[0]
                movies = Torrent.objects.filter(pk__in=request.session['search'], category__contains=filters[1], rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1]  
            else: 
                movies = Torrent.objects.filter(pk__in=request.session['search'], category__contains=filters[1], rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1]  
        elif filters[1] == '|':
            if filters[0] == 'release' or filters[0] == 'rate':
                filters[0] = '-' + filters[0]
                movies = Torrent.objects.filter(pk__in=request.session['search'], rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1]  
            else:
                movies = Torrent.objects.filter(pk__in=request.session['search'], rate__range=[filters[2], filters[3]], release__range=[filters[4], filters[5]]).order_by(filters[0]).values_list()[::1]      
        return JsonResponse({'movie' : movies})
    else:  
        return render(request, 'video/list.html', {'film' : film, 'genre' : genre})

@login_required
def video(request, tittle):
    try:
        req = request.POST.get('pal')
        if request.method == 'POST' and 'pal' in request.POST:
            name = request.user
            id_profile = User.objects.get(username=name).pk
            token = Profile.objects.get(id=id_profile)
            token.token = uuid.uuid4().hex[:12].upper()
            token.save()
            ids = Torrent.objects.get(pk=tittle).idimdb
            lang = request.user.pk
            toto = Profile.objects.only('language').get(id=lang).language
            print(toto)
            inf = {'ids' : ids, 'lan' : toto, 'token' : token.token}
            return JsonResponse({'infos' : inf })
        grey = 0
        count = request.POST.get('yeah')
        if request.method == 'POST' and 'yeah' in request.POST:
            name = request.user
            id_profile = User.objects.get(username=name).pk
            bd_already = Profile.objects.filter(id=id_profile).first()
            if tittle not in bd_already.already:
                bd_already.already = bd_already.already + tittle + ' '
                bd_already.save()
        inshalah = request.POST.get('tok')
        if request.method == 'POST' and 'tok' in request.POST:
            name = request.user
            id_profile = User.objects.get(username=name).pk
            token = Profile.objects.get(id=id_profile)
            token.token = ''
            token.save()
        if request.method == 'POST' and not 'pal' in request.POST:
            comment_form = CommentForm(request.POST)
            data = comment_form.data['comment']
            print (data)
            if len(data) < 200:
                movie = Torrent.objects.filter(id=tittle).first()
                if not movie.comments:
                    movie.comments = json.dumps({'comments': []})
                    movie.save()
                tmp = json.loads(movie.comments)
                tmp['comments'].append(request.user.username)
                tmp['comments'].append(data)
                movie.comments = json.dumps(tmp)
                movie.save()
        else:
            comment_form = CommentForm()
    except:
        pass
    try:
        id_film = Torrent.objects.filter(id=tittle).first().name
        miniature = Torrent.objects.filter(id=tittle).first().miniature
        annee = Torrent.objects.filter(id=tittle).first().release
        synopsis = Torrent.objects.filter(id=tittle).first().synopsis
        category = Torrent.objects.filter(id=tittle).first().category
        notes = Torrent.objects.filter(id=tittle).first().rate
        actors = Torrent.objects.filter(id=tittle).first().actors
        act = actors[actors.find('[')+1:actors.find(']')]
        actors = act.replace('"', '')
        actors = actors.replace(',', ' / ')
        name = request.user
        id_profile = User.objects.get(username=name).pk
        bd_already = Profile.objects.filter(id=id_profile).first()
        trysplit = bd_already.already.split()
        for aff in trysplit:
            if (aff == tittle):
                grey = 1
        if category and ('{' in category or '[' in category):
            category = category[category.find('[')+1:category.find(']')]
            category = category.replace('"', '')
            category = category.replace(' ,', '  /  ')
        context = {
            'form': comment_form,
            'grey' : grey,
            'titre' : id_film,
            'miniature' : miniature,
            'annee' : annee,
            'synopsis' : synopsis,
            'category' : category,
            'notes' : notes,
            'acteurs' : actors
        }
        coms = Torrent.objects.filter(id=tittle).first()
        tmp = None
        if coms.comments:
            tmp = json.loads(coms.comments)
        if tmp:
            comments = []
            authors = []
            id_authors = []
            i = 0
            while i < len(tmp['comments']):
                if i % 2:
                    comments.append(tmp['comments'][i])
                else:
                    authors.append(tmp['comments'][i])
                    id_authors.append(User.objects.filter(username=tmp['comments'][i]).first().id)
                i += 1
            mylist = zip(authors, comments, id_authors)
            context_1 = {
                'form': comment_form,
                'comments': mylist,
                'grey' : grey,
                'titre' : id_film,
                'miniature' : miniature,
                'annee' : annee,
                'synopsis' : synopsis,
                'category' : category,
                'notes' : notes,
                'acteurs' : actors
            }
            return render(request, 'video/video.html', context_1)
        return render(request, 'video/video.html', context)
    except AttributeError:
        return (redirect('/'))

@login_required
def serie(request, title):
    try:
        seasons = Torrent.objects.get(pk=title).serie
    except :
        return redirect('/')
    grey = 0
    count = request.POST.get('yeah')
    print(count)
    if (request.method == 'POST' and 'yeah' in request.POST):
        name = request.user
        id_profile = User.objects.get(username=name).pk
        bd_already = Profile.objects.filter(id=id_profile).first()
        if title not in bd_already.already:
            bd_already.already = bd_already.already + title + ' '
            bd_already.save()
    lang = request.user.pk
    name = request.user
    id_profile = User.objects.get(username=name).pk
    token = Profile.objects.get(id=id_profile)
    token.token = uuid.uuid4().hex[:12].upper()
    token.save()
    toto = Profile.objects.only('language').get(id=lang).language
    torrent = Torrent.objects.get(pk=title)
    infos = json.loads(torrent.episodes)
    infos = sorted(infos, key=lambda e: e['episode'])
    name = request.user
    id_profile = User.objects.get(username=name).pk
    bd_already = Profile.objects.filter(id=id_profile).first()
    trysplit = bd_already.already.split()
    for aff in trysplit:
        if (aff == title):
            grey = 1
    saison = []
    for p in infos:
        if not p['season'] in saison:
            saison.append(p['season'])
    saison.sort()
    cat = json.loads(torrent.category)
    cat = cat['category']
    if request.method == 'POST' and 'tok' in request.POST:
        name = request.user
        id_profile = User.objects.get(username=name).pk
        token = Profile.objects.get(id=id_profile)
        token.token = ''
        token.save()
    return render(request, 'video/serie.html', {'tok': token.token, 'toto' : toto, 'infos' : infos, 'season' : saison, 'title' : title, 'torrent' : torrent, 'cat' : cat, 'grey' : grey,})

@login_required
def watch_serie(request, title, season, episode):
    return render(request, 'video/video.html')

@login_required
def filtre(requests):
    if requests.method == 'POST':
        print(requests.POST.getlist('genre1'))
    return render(requests, 'list.html')