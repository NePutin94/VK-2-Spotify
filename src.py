import spotipy
import vk_api
from spotipy.oauth2 import SpotifyClientCredentials
from vk_api.audio import VkAudio
import collections
from collections import OrderedDict
from math import floor
import json

vkDump = False
FastSearch = False
cid = ''
secret = ''
redirect = ''
vkNumber = ''
vkPass = ''


class bcolors:
    INFO = '\033[5;37;40m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[0;31;40m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[0;34;40m'


def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def just_search():
    return 0


def search_by_artist(artistUri):
    res = sp.artist_albums(artistUri, limit=50)
    albums = []
    for i in res['items']:
        albums.append(i['uri'])
    print(bcolors.INFO + 'Find ' + str(len(albums)) + ' albums' + bcolors.ENDC)
    tr = []
    k = 0
    for i in albums:
        offset = 0
        trackss = sp.album_tracks(i, limit=50, offset=offset)
        for t in trackss['items']:
            d = {'Name': t['name'],
                 'Uri': t['uri']}
            tr.append(d)
        offset += len(trackss['items'])
        while trackss['total'] > offset:
            trackss = sp.album_tracks(i, limit=50, offset=offset)
            offset += len(trackss['items'])
            for t in trackss['items']:
                d = {'Name': t['name'],
                     'Uri': t['uri']}
            tr.append(d)
    print(bcolors.INFO + 'Find ' + str(len(tr)) + ' tracks' + bcolors.ENDC)
    return tr


def slow_search(sp):
    spCount = 0
    count = 0
    skip = 0
    uris = []
    cha = []
    cha2 = json.load(open("vk2spotify_cash.txt", 'r', encoding='utf-8'))
    with open("vktracks.txt", "r", encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            count += 1
            x = line.split('|')
            if(len(x) < 2):
                skip += 1
                continue
            artist = x[0]
            title = x[1].replace('\n', '')
            print('\n' + bcolors.HEADER + 'Start search for ' +
                  artist + ' ' + title + bcolors.ENDC)
            foundArtist = False
            tracks = []
            title = title.lower().replace(' ', '')
            if cha2:
                for c in cha2:
                    if c['Artist'] == artist:
                        foundArtist = True
                        tracks = c['tracks']
                        print(bcolors.BOLD + 'Static chache hint!' + bcolors.ENDC)
                        break
            if cha:
                for c in cha:
                    if c['Artist'] == artist:
                        foundArtist = True
                        tracks = c['tracks']
                        print(bcolors.BOLD + 'Runtime chache hint!' + bcolors.ENDC)
                        break

            if not foundArtist:
                res = sp.search(artist, type='artist')
                if res['artists']['total'] > 0:
                    tracks = search_by_artist(
                        res['artists']['items'][0]['uri'])
                    print(bcolors.BOLD + 'Start build the chache' + bcolors.ENDC)
                    cha.append({'Artist': artist, 'tracks': tracks})
                else:
                    print(bcolors.FAIL + 'artist: ' +
                          artist + ' not found' + bcolors.ENDC)

            foundTrack = False
            for t in tracks:
                name1 = t['Name'].lower().replace(' ', '')
                if title.find(name1) >= 0 or name1.find(title) >= 0:
                    foundTrack = True
                    spCount += 1
                    uris.append(t['Uri'])
                    break
            if(not foundTrack):
                print(bcolors.FAIL + artist + ' ' +
                      title + ' not found' + bcolors.ENDC)
            else:
                print(bcolors.OKGREEN + artist + ' ' + title +
                      ' found: true, track uri: ' + t['Uri'] + bcolors.ENDC)
        print('\n' + bcolors.OKBLUE + 'accuracy: ' + str((spCount / count) * 100) + ' the number of missed: ' + str(skip) + bcolors.ENDC)
        chache = open("vk2spotify_cash.txt", "w", encoding='utf-8')
        cha2 += cha
        chache.write(json.dumps(cha2, ensure_ascii=False, indent=2))
        return uris


def fast_search(sp):
    spCount = 0
    count = 0
    skip = 0
    uris = []
    with open("vktracks.txt", "r", encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            count += 1
            x = line.split('|')
            if(len(x) < 2):
                skip += 1
                continue
            artist = x[0]
            title = x[1].replace('\n', '')
            print('\n' + bcolors.HEADER + 'Start search for ' +
                  artist + ' ' + title + bcolors.ENDC)
            res = sp.search(artist + ' ' + title, type='track', limit=40)
            found = False
            for t in res['tracks']['items']:
                str1 = title.lower().replace(' ', '')
                str2 = t['name'].lower().replace(' ', '')
                str3 = artist.lower().replace(' ', '')
                str4 = t['artists'][0]['name'].lower().replace(' ', '')
                if(str3.find(str4) >= 0 or str4.find(str3) >= 0):
                    if(str2.find(str1) >= 0 or str1.find(str2) >= 0):
                        found = True
                        spCount += 1
                        uris.append(t['uri'])
                        break
            if(not found):
                print(bcolors.FAIL + artist + ' ' +title + ' not found' + bcolors.ENDC)
            else:
                print(bcolors.OKGREEN + artist + ' ' + title +' found: true, track uri: ' + t['uri'] + bcolors.ENDC)
    print('\n' + bcolors.OKBLUE + 'accuracy: ' + str((spCount / count) * 100) + ' the number of missed: ' + str(skip) + bcolors.ENDC)
    return uris

if(vkDump):
    vk_session = vk_api.VkApi(vkNumber, vkPass, auth_handler=auth_handler)
    vk_session.auth()
    vk = vk_session.get_api()
    vkaudio = VkAudio(vk_session)
    with open("vktracks.txt", "w", encoding='utf-8') as f:
        for track in vkaudio.get():
            print(track['artist'] + '|' + track['title'] + "\n")
            f.write(track['artist'] + '|' + track['title'] + "\n")


oauth = spotipy.SpotifyOAuth(
    client_id=cid, client_secret=secret, redirect_uri=redirect, cache_path='.spotify-cache',
    scope="playlist-modify-private user-library-modify user-library-read playlist-modify-public"
)
sp = spotipy.Spotify(auth_manager=oauth)

uris = []
if FastSearch:
    uris = fast_search(sp)
else:
    uris = slow_search(sp)
print(uris)
retrieved = list(OrderedDict.fromkeys(uris))
print(bcolors.OKBLUE + 'found track count: ' + str(len(retrieved)) + bcolors.ENDC + '\n')
print(bcolors.OKBLUE + 'Adding music to spotify: ' + str(len(retrieved)) + bcolors.ENDC)

user_id = sp.me()['id']
results = sp.current_user_playlists(limit=50)
findVkMus = False
playlistUri = ""
for i, item in enumerate(results['items']):
    if item['name'] == 'VkMusic':
        findVkMus = True
        print(bcolors.INFO + 'The vkMusic playlist has already been created' + bcolors.ENDC)
        playlistUri = item['uri']

if not findVkMus:
    print(bcolors.INFO + 'Created a vkMusic playlist' + bcolors.ENDC)
    res = sp.user_playlist_create(user_id, name='VkMusic')
    playlistUri = res['uri']

chankSize = floor(len(retrieved) / 60)
if chankSize == 0:
    chankSize = 1
chanks = [retrieved[i::chankSize] for i in range(chankSize)]
print('\n' + bcolors.INFO + 'Chanks count: ' + str(len(chanks)) + bcolors.ENDC)
count = 0
for rn in chanks:
    print(bcolors.INFO + 'Chank[' + str(count) +
          '] added to playlist' + bcolors.ENDC)
    sp.user_playlist_add_tracks(user_id, playlistUri, rn)
    count += 1