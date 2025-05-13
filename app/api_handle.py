import requests, random
from PIL import Image

def image():
	url = f'https://maps.googleapis.com/maps/api/streetview?size=600x300&location=Z%C3%BCrich&key={getKey()}'
	response = requests.get(url)
	if response.status_code == 200:
		with open('streetview_image.jpg', 'wb') as file:
			print('attempting to download')
			file.write(response.content)
		print("Image successfully downloaded")
	else:
		print(f"Error: {response.status_code}")
	image = Image.open('streetview_image.jpg')
	image.show()

def getKey():
	try:
		with open('keys/streetview.txt', 'r') as file:
			key = file.read()
	except:
		print('error')
	return key

image()
