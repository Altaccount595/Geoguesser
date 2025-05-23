import requests
import random
import urllib.parse
import numpy as np
from PIL import Image
from db import getRandLoc #, getRandAddress
#import os
#from .db import getRandLoc
def images_are_equal(img1_path, img2_path):
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')
    return np.array_equal(np.array(img1), np.array(img2))

def address_lat():
	address = getRandAddress()
	key=getKey()
	encoded_address=urllib.parse.quote(address)
	url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={key}"
	response = requests.get(url)
	data= response.json()
	if data['status'] == 'OK':
		location = data['results'][0]['geometry']['location']
		lat = location['lat']
		lng = location['lng']
		print(f"Latitude: {lat}, Longitude: {lng}")
	else:
		print("Geocoding Error", data['status'])

	return [lat, lng]
def image(lat,long,heading=0, fov=90):
	url = f'https://maps.googleapis.com/maps/api/streetview?size=600x300&location={lat},{long}&heading={heading}&fov={fov}&key={getKey()}'
	print(url)
	#meta_url= "https://maps.googleapis.com/maps/api/streetview/metadata"
	#params={
	#	'location':f"{loc[0]}, {loc[1]}",
	#	'key':getKey()}
	response = requests.get(url)
	print(response)
	if response.status_code == 200:
		with open('static/streetview_image.jpg', 'wb') as file:
			print('attempting to download')
			file.write(response.content)
		print("Image successfully downloaded")
	else:
		print(f"Error: {response.status_code}")
	if (images_are_equal('static/bad.jpg', 'static/streetview_image.jpg')):
		location = getRandLoc()
		lat = location[0]
		long = location[1]
		image(location[0], location[1])
	return [lat, long, heading, fov]

def getKey():
    try:
        with open('keys/streetview.txt', 'r') as file:
            key = file.read()
    except:
        print('error')
        return
    return key
	#return os.environ["MAPS_KEY"] for droplet
