# vk-to-spotify

## Install libs
[vk_api](https://github.com/python273/vk_api)
[spotipy](https://spotipy.readthedocs.io/en/2.13.0/)

# Usage
Basic installation:
Open 'src.py' and set the values to variables
- spotify auth: cid(SPOTIPY_CLIENT_ID), secret(SPOTIPY_CLIENT_SECRET), redirect(SPOTIPY_REDIRECT_URI)
- vk auth: vkNumber, vkPass

Then you have two ways:
- #### The first way
	- Go to 'src.py' and make sure that the 'vkDump' flag is set to True
	- Run the file in the console ```python src.py```
	- After some time, the music from VK will be saved to a file 'vktracks.txt', then the search for music from the file in Spotify will start automatically
- #### Second way
	- Create a file vktracks.txt 
	- Fill it with your tracks, pattern: ArtistName|Title 
	- Open the file 'src.py', set the vkDump flag to False 
	- Run the file in the console ```python src.py``` 