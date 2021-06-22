import requests


BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
API_KEY = "f74151d4b5f90c889199a59ce16026e8"


def get_current_weather(city_name):
    url = BASE_URL + "q=" + city_name + "&appid=" + API_KEY
    response = requests.get(url)

    if response.status_code == 200:
        result = []
        data = response.json()
        weather = data["weather"]
        main = data["main"]
        temperature = main["temp"] - 273
        humidity = main["humidity"]
        pressure = main["pressure"]
        result.append(f"{data['name']:-^30}")
        result.append(f"Temperature: {temperature:.1f} oC")
        result.append(f"Humidity: {humidity}%")
        result.append(f"Pressure: {(pressure//1.333224):.1f} mm Hg")
        result.append(f"Weather Report: {weather[0]['description']}")

    else:
        return "Sorry;(\nError in the HTTP request or can't find city."

    return " \n".join(result)


if __name__ == "__main__":
    print(get_current_weather("ivano-frankivsk"))
    city = input("Input city: ")
    print(get_current_weather(city))
