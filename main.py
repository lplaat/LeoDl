import leodl, json, _thread, subprocess, urllib.parse, urllib.request, time
from youtube_search import YoutubeSearch
from mutagen.mp4 import MP4, MP4Cover

artist_id = 14749353
download_threads = 5
search_limit = 20
seconds_in_range = 12

#getting all information off the artist
albums = leodl.GetArtistAlbums(artist_id)
tracks = leodl.ExtractSongFromAlbums(albums)

#setting up threads
threads_tracks = []
threads_done = 0
for i in range(download_threads):
    threads_tracks.append([])

thread_point = 0
for song in tracks:
    threads_tracks[thread_point].append(song)
    thread_point += 1
    if thread_point == download_threads:
        thread_point = 0

#downloading tracks
put_data = []
def DownloadTracks(tracks):
    global put_data, threads_done
    for track in tracks:
        try:
            print('Downloaded ' + track['title'] + ' from ' + track['artist']['name'])
            #making path if not exist
            audio_path = leodl.checkpath('./data', '')
            audio_path = leodl.checkpath('music', audio_path)
            audio_path = leodl.checkpath(leodl.FilterSting(track['artist']['name']), audio_path)
            audio_path = leodl.checkpath(leodl.FilterSting(track['album']['title']), audio_path)

            #get youtube source link
            search_text = track['artist']['name'] + ' - ' + track['title']
            search_data = json.loads(YoutubeSearch(search_text, max_results = search_limit).to_json())['videos']

            for search in search_data:
                duration = int(search['duration'].split(':')[0])*60 + int(search['duration'].split(':')[1])
                if leodl.NumberInRange(duration, track['duration'], seconds_in_range) == True and track['metadata']['yt-link'] == '':
                    track['metadata']['yt-link'] = 'https://www.youtube.com/watch?v=' + search['id']
            
            #download music
            if not track['metadata']['yt-link'] == '':
                temp_audio_path = audio_path + leodl.FilterSting(track['title']) + '.m4a'
                subprocess.check_output(['yt-dlp', '-f', 'bestaudio[ext=m4a]', track['metadata']['yt-link'], '-o', temp_audio_path])

                track['metadata']['downloaded'] = True
                track['metadata']['path'] = temp_audio_path.replace('./data', '.')
            else:
                print('Cant find youtube link, ' + search_text)

            #download album cover
            coverFilePath = audio_path + 'cover.jpg'

            go = True
            while go:
                try:
                    urllib.request.urlretrieve(track['album']['cover_xl'], coverFilePath)
                    go = False
                except:
                    pass

            #download artist cover
            go = True
            while go:
                try:
                    urllib.request.urlretrieve(track['artist']['picture_xl'], './data/music/' + leodl.FilterSting(track['artist']['name']) + '/artist.jpg')
                    go = False
                except:
                    pass

            #set metadata
            if not track['metadata']['yt-link'] == '':
                file = MP4(temp_audio_path)
                file['\xa9nam'] = track['title']
                file['\xa9ART'] = track['artist']['name']
                file['\xa9alb'] = track['album']['title']
                file['\xa9day'] = track['release_date'].split('-')[0]
                file['\xa9gen'] = ', '.join([ genre['name'] for genre in track['album']['genres']['data']])
                file['trkn'] = [(track['track_position'], track['album']['nb_tracks'])]
                with open(coverFilePath, 'rb') as coverFile:
                    file['covr'] = [MP4Cover(coverFile.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                file.save()

            #log song
            put_data.append(track)
        except:
            pass
    threads_done += 1

#put data in file
def pdif():
    global put_data, threads_done
    while not (threads_done == download_threads and len(put_data) == 0):
        if not len(put_data) == 0:
            tracks_data = json.loads(open('./data/tracks.json', 'r').read())
            found = False

            for track in tracks_data:
                if track['title'] == put_data[0]['title'] and track['artist']['name'] == put_data[0]['artist']['name'] and track['album']['title'] == put_data[0]['album']['title']:
                    found = True

            if found == False:
                tracks_data.append(put_data[0])
                open('./data/tracks.json', 'w').write(json.dumps(tracks_data, indent=4))
            else:
                put_data.pop(0)
        else:
            time.sleep(1)
    threads_done += 1

_thread.start_new_thread(pdif, ())
for i in range(download_threads):
    _thread.start_new_thread(DownloadTracks, (threads_tracks[i], ))

while not threads_done == download_threads+1:
    time.sleep(3)