import json
import requests

from flask import Flask
from flask import render_template, request

CREDENTIALS_FILE = 'creds.json'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_api_key():
	"""
		Read API key from creds.json file.

	"""

	creds_file_obj = open(CREDENTIALS_FILE, 'r')
	creds_json = creds_file_obj.read()
	creds_dict = json.loads(creds_json)
	api_key = creds_dict['api_key']
	return api_key

def get_weather_details(city_name):
	"""
		Make the weather API hit and get the weather details.

	"""

	base_url = "http://api.openweathermap.org/data/2.5/weather?"
	api_key = get_api_key()
	complete_url = base_url + "appid=" + api_key + "&q=" + city_name
	response = requests.get(complete_url) 

	api_response_dict = response.json()
	if api_response_dict["cod"] == "404":
		return render_template('page_not_found.html')
	
	# {u'temp': 302.15, u'temp_max': 302.15, u'humidity': 70, u'pressure': 1010, u'temp_min': 302.15, u'feels_like': 305.2}
	weather_details = api_response_dict["main"]

	# Convert from Kelvin to Celsius
	temp = weather_details['temp'] - 273.15
	temp_min = weather_details['temp_max'] - 273.15
	temp_max = weather_details['temp_max'] - 273.15
	humidity = weather_details['humidity']
	pressure = weather_details['pressure']
	weather_description = api_response_dict['weather'][0]['description']
	country = api_response_dict['sys']['country']
	wind = api_response_dict['wind']['speed']

	# Tuple packing/ Adding all necessary fields
	weather_details_tuple = (temp, temp_min, temp_max, humidity, pressure, country, wind, weather_description)
	return weather_details_tuple

@app.route("/process/", methods=['POST'])
def display_weather_details():
	"""
		method to display the weather details using wather API.

	"""

	city = request.form["city"]
	weather_details_tuple = get_weather_details(city)
	try:
		# Tuple unpacking
		# For 404 page, the tuple will have contents of the page_not_found.html and throws ValueError
		(temp, temp_min, temp_max, humidity, pressure, country, wind, description) = weather_details_tuple
		return render_template(
			'weather_details.html', city=city, temp=temp, temp_min=temp_min, temp_max=temp_max,
			humidity=humidity, pressure=pressure, country=country, wind=wind, weather_description=description
			)
	except ValueError:
		return weather_details_tuple

if __name__ == '__main__':
	# Remove "debug = True" when deployed in production 
    app.run(debug = True)
