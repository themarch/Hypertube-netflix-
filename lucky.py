#!/usr/bin/python3

import sys, webbrowser, bs4, requests
from qbittorrent import Client

def parse_pirate(keyword):
    address = 'https://tpb.party/search/' + ''.join(keyword)
    result = requests.get(address)
    try :
        result.raise_for_status()
    except Exception as exc:
        print('There was a problem: %s' %(exc))
    poupou = bs4.BeautifulSoup(result.text)
    print(address)

    magnets = poupou.find('a', title='Download this torrent using magnet')
    return(magnets.get('href'))

qb  =  Client('http://127.0.0.1:8080/')
qb . login ('admin' , 'admin')
qb.download_from_link(parse_pirate('blanche+neige'))
print(qb.torrents())


