import spotipy
import vk_api
from spotipy.oauth2 import SpotifyClientCredentials
from vk_api.audio import VkAudio
import collections
from collections import OrderedDict
from math import floor

vkDump = True;
cid = ''
secret = ''
redirect = ''
vkNumber = ''
vkPass = ''



def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device
def divide_chunks(l, n):  
    for i in range(0, len(l), n):  
        yield l[i:i + n]

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

if(vkDump):
	vk_session = vk_api.VkApi(vkNumber,vkPass , auth_handler=auth_handler)
	vk_session.auth()
	vk = vk_session.get_api()
	vkaudio = VkAudio(vk_session)
	with open("vktracks.txt", "w", encoding='utf-8') as f:
	    for track in vkaudio.get():
	    	f.write(track['artist'] + '|' + track['title'] + "\n")


oauth = spotipy.SpotifyOAuth(
           client_id=cid, client_secret=secret, redirect_uri=redirect,cache_path = '.spotify-cache',
           scope = "playlist-modify-private user-library-modify user-library-read playlist-modify-public"
       )
sp = spotipy.Spotify(auth_manager=oauth)
spCount = 0
count = 0
skip = 0
uris = []
with open("vktracks.txt", "r", encoding='utf-8') as f:
	lines = f.readlines()
	for line in lines:
		count+=1
		x = line.split('|')
		if(len(x) < 2):
			skip+=1
			continue;
		artist = x[0]
		title = x[1]
		
		res = sp.search(artist + ' ' + title, type='track', limit = 40)
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
					break;
		print('-------------------------------------------------------')
		if(not found): print(bcolors.FAIL + artist +' ' + title + ' not found' + bcolors.ENDC)
		else: print(bcolors.OKGREEN + artist + ' '+ title + ' found: true, track uri: ' + t['uri'] + bcolors.ENDC)
 
retrieved = list(OrderedDict.fromkeys(uris))
print('\n' + bcolors.OKBLUE + 'accuracy: ' + str((spCount/count) * 100) + ' the number of missed: ' + str(skip) + bcolors.ENDC)
print(bcolors.OKBLUE + 'found track count: ' + str(len(retrieved)) + bcolors.ENDC + '\n')

user_id = sp.me()['id']
results = sp.current_user_playlists(limit=50)
findVkMus = False
playlistUri = ""
for i, item in enumerate(results['items']):
	if item['name'] == 'VkMusic':
		findVkMus = True
		playlistUri = item['uri']

if not findVkMus:
	res = sp.user_playlist_create(user_id, name = 'VkMusic')
	playlistUri = res['uri']
chankSize = floor(len(retrieved) / 60)
chanks = [ retrieved[i::chankSize] for i in range(chankSize)]
for rn in chanks:
	sp.user_playlist_add_tracks(user_id, playlistUri, rn)