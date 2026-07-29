import os
import requests
from flask import Blueprint, render_template, flash, current_app
from app.forms import WeatherForm

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/', methods=['GET', 'POST'])
def index():
    form = WeatherForm()
    weather_data = None
    if form.validate_on_submit():
        city = form.city.data
        weather_data = get_weather(city)
    return render_template('weather/index.html', form=form, weather_data=weather_data)

def get_weather(city):
    api_key = current_app.config.get('OPENWEATHERMAP_API_KEY', '')
    if not api_key:
        flash('Weather API key not configured. Set OPENWEATHERMAP_API_KEY in your .env file.', 'warning')
        return None
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'city': city,
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
        }
    else:
        flash('City not found!', 'danger')
        return None
