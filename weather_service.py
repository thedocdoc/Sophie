'''
Copyright (c) 2023 Apollo Timbers. All rights reserved.

This work is licensed under the terms of the Apache License 2.0.
For a copy, see https://github.com/apache/.github/blob/main/LICENSE.

Sophie robot project:

Weather report class

This class retrieves the current weather report for a specified city using the OpenWeather API. It constructs
and sends a request to the API with the city name, desired units (imperial or metric), and the API key. After
receiving the response, the function parses the JSON data to extract key weather details such as temperature,
humidity, and weather description.

Based on the weather data, it formulates a user-friendly weather report which includes temperature, feels-like
temperature, humidity, and a general description of the weather conditions. Additionally, the function provides
attire recommendations based on the current weather (e.g., suggesting a raincoat for rainy weather, or warm
clothing for cold temperatures). This function enhances the robot's interactive capabilities by providing useful
and practical information to the user in a conversational manner.

'''

import requests

class WeatherService:
    def __init__(self, api_key, default_city="Webster", units="imperial"):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather?"
        self.default_city = default_city
        self.units = units

    def get_weather_report(self, city=None):
        city = city or self.default_city
        url = f"{self.base_url}q={city}&units={self.units}&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return self._format_weather_response(response.json())
        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data: {e}"

    def _format_weather_response(self, data):
        temperature = round(data['main']['temp'])
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']

        report = (f"Current weather in {self.default_city} is {description}. "
                  f"Temperature is {temperature} degrees, it feels like {feels_like}. "
                  f"Humidity is {humidity}%.")

        return report + " " + self._suggest_attire(temperature, description)

    def _suggest_attire(self, temperature, weather_description):
        attire_suggestion = "If you are adventuring outside today, make sure to wear "

        if "rain" in weather_description:
            return attire_suggestion + "A raincoat."
        elif temperature >= 76:
            return attire_suggestion + "Light clothing, like shorts and a t-shirt."
        elif 50 <= temperature < 76:
            return attire_suggestion + "A long-sleeve shirt and pants."
        elif 40 <= temperature < 50:
            return attire_suggestion + "A jacket or a sweater."
        else:
            return attire_suggestion + "warm clothing, like a heavy coat, gloves, and a hat."

    def get_temperature(self, city=None):
        city = city or self.default_city
        url = f"{self.base_url}q={city}&units={self.units}&appid={self.api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            temperature = round(data['main']['temp'])
            return temperature
        except requests.exceptions.RequestException as e:
            return f"Error fetching temperature data: {e}"
