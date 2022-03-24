import requests
import json
import math
import os
import time

#---------------------------------------------------------------------------
def GetArtistAlbums(artist_id):
    return json.loads(requests.get('https://api.deezer.com/artist/'+str(artist_id)+'/albums').text)['data']

#---------------------------------------------------------------------------
letters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
def FilterSting(input):
    string = ""
    for part in input:
        found = False
        for part_abc in letters:
            if part == part_abc:
                found = True
        if found == False:
            string += part
        else:
            string += '#'
    return string

#---------------------------------------------------------------------------

def ExtractSongFromAlbums(albums):
    Songs = []
    for album_data in albums:
        try:
            lgo = True
            while lgo:
                album = json.loads(requests.get('https://api.deezer.com/album/'+str(album_data['id'])).text)
                album_pre = json.loads(json.dumps(album))
                del album_pre['tracks']
                del album_pre['artist']
                del album_pre['contributors']
                for song in album['tracks']['data']:
                    go = True
                    while go:
                        song_data = json.loads(requests.get('https://api.deezer.com/track/'+str(song['id'])).text)
                        try:
                            Songs.append({
                                'title': song_data['title'],
                                'release_date': song_data['release_date'],
                                'duration': song_data['duration'],
                                'track_position': song_data['track_position'],
                                'artist': song_data['artist'],
                                'album': album_pre,
                                'metadata': {
                                    'downloaded': False,
                                    'yt-link': '',
                                    'path': ''
                                }
                            })
                            go = False
                        except:
                            print('throttled')
                            time.sleep(2)
                lgo = False
        except:
            print('throttled')
            time.sleep(2)
    return Songs

#---------------------------------------------------------------------------
def ExtractCoversFromAlbums(albums):
    Covers = {}
    for album_data in albums:
        Covers[album_data['title']] = album_data['cover_xl']
    return Covers

#---------------------------------------------------------------------------
def NumberInRange(a, b, steps):
    found = False
    k = 0-steps
    for _ in range(steps*2):
        if a == b-k:
            found = True
        k += 1
    return found

#---------------------------------------------------------------------------

def RoundWithZero(num):
    if int(num) < 10:
        num = '0' + str(num)
    return str(num)

#---------------------------------------------------------------------------
def SplitFromMax(num, Max):
    a = 0
    b = math.floor(num)
    steps = 0
    for _ in range(math.floor(num)):
        if steps == Max:
            b = b - Max
            a += 1
            steps = 0
        steps += 1
    if b == Max:
        a += 1
        b = 0
    return [a, b]

def FromSecToTimeDis(num):
    min1 = SplitFromMax(num, 60)[0]
    sec = SplitFromMax(num, 60)[1]
    min = SplitFromMax(min1, 60)[1]
    uur = SplitFromMax(min1, 60)[0]
    
    return RoundWithZero(uur) + ':' + RoundWithZero(min) + ':' + RoundWithZero(sec)

#---------------------------------------------------------------------------
def checkpath(path, old_path):
    try: os.mkdir(old_path + path + '/')
    except: pass
    return old_path + path + '/'
