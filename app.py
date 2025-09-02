from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")  # Replace with your actual API key
is_metric = True  # Global flag for units


# --- Weather Fetcher ---
def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    units = "metric" if is_metric else "imperial"

    params = {"q": city, "appid": API_KEY, "units": units}
    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get("cod") != 200:
        return None, data.get("message", "Error fetching weather")

    weather_info = {
        "temp": float(data["main"]["temp"]),
        "feels_like": float(data["main"]["feels_like"]),
        "temp_min": float(data["main"]["temp_min"]),
        "temp_max": float(data["main"]["temp_max"]),
        "pressure": int(data["main"]["pressure"]),  # ✅ numeric only
        "humidity": int(data["main"]["humidity"]),
        "wind_speed": float(data["wind"]["speed"]),  # ✅ numeric only
        "description": data["weather"][0]["description"],
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"], timezone.utc),
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"], timezone.utc),
    }

    return weather_info, None


# --- Conversion Helpers ---
def convert_pressure(hpa):
    """Convert pressure depending on selected units."""
    if is_metric:
        return f"{hpa} hPa"
    else:
        return f"{round(hpa * 0.02953, 2)} inHg"


def convert_wind(speed):
    """Convert wind speed depending on selected units."""
    if is_metric:
        return f"{speed} m/s"
    else:
        return f"{round(speed, 2)} mph"


# --- Recommendations ---
def get_recommendation(category, weather_info):
    temperature = weather_info['temp']
    humidity = weather_info['humidity']

    if category == 'food':
        if temperature >= 25 and humidity < 60:
            return "🥗 How about enjoying a colorful fruit salad with a light vinaigrette? 🍓🍉🍊"
        elif 20 <= temperature < 25 and humidity < 70:
            return "🥪 Opt for a nutritious picnic with whole-grain sandwiches, fresh vegetables, and fruit 🍎🥒."
        elif temperature < 10:
            return "🍲 Warm up with a comforting bowl of vegetable soup, packed with nutrient-rich ingredients 🥕🥦."
        else:
            return "🍛 Consider a balanced meal with lean protein, whole grains, and plenty of vegetables 🥩🍚🥗."

    elif category == 'clothing':
        if temperature >= 25 and humidity < 60:
            return "👕 Dress light and comfortably. Consider wearing shorts, a t-shirt, and sunglasses 😎."
        elif 20 <= temperature < 25 and humidity < 70:
            return "👔 Choose breathable and comfortable clothing for a pleasant day outdoors 🌤️."
        elif temperature < 10:
            return "🧥 Bundle up for the cooler weather. Wear a warm jacket, scarf, and gloves ❄️🧣."
        else:
            return "🧶 Select comfortable and layered clothing. A light jacket or sweater might be suitable 🌦️."

    elif category == 'fitness':
        if temperature >= 25 and humidity < 60:
            return "🏃‍♂️ Consider outdoor activities like running, cycling 🚴, or playing a sport ⚽."
        elif 20 <= temperature < 25 and humidity < 70:
            return "🚶‍♀️ Enjoy a brisk walk, hike 🥾, or outdoor yoga session 🧘."
        elif temperature < 10:
            return "💪 Opt for indoor exercises like strength training, yoga, or a home workout 🏋️."
        else:
            return "🤸 Choose a fitness routine that suits your preferences and energy levels ⚡."

    elif category == 'travel':
        if temperature >= 25 and humidity < 60:
            return "🏖️ Explore outdoor destinations like parks 🌳, beaches 🏝️, or nature reserves 🌄."
        elif 20 <= temperature < 25 and humidity < 70:
            return "🗺️ Consider a day trip to scenic spots 🌲, hiking trails ⛰️, or nearby attractions 🏞️."
        elif temperature < 10:
            return "🏛️ Plan a cozy indoor getaway to museums 🖼️, art galleries 🎨, or historical sites 🏰."
        else:
            return "🚂 Explore local attractions or plan a short trip based on your interests 🌍."

    elif category == 'holiday':
        if temperature >= 25 and humidity < 60:
            return "🎉 Plan a picnic 🧺, beach day 🏖️, or outdoor barbecue 🍔 with friends and family 👨‍👩‍👧‍👦."
        elif 20 <= temperature < 25 and humidity < 70:
            return "🥳 Enjoy the pleasant weather with a holiday picnic 🧺 or outdoor games ⚽."
        elif temperature < 10:
            return "🎬 For colder days, celebrate indoors with a cozy movie night 🍿 or festive gathering 🎄."
        else:
            return "✨ Plan a holiday celebration that suits the weather conditions 🌦️."

    else:
        return "🤷 No recommendation available for this category."


# --- Toggle units ---
def toggle_units():
    global is_metric
    is_metric = not is_metric


# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def display_weather():
    city = request.form.get("city")
    if not city:
        return render_template("error.html", message="Please enter a city name.")

    weather_info, error = get_weather(city)
    if error:
        return render_template("error.html", message=error)

    unit_symbol = "°C" if is_metric else "°F"

    recommendations = {
        "food": get_recommendation("food", weather_info),
        "clothing": get_recommendation("clothing", weather_info),
        "fitness": get_recommendation("fitness", weather_info),
        "travel": get_recommendation("travel", weather_info),
        "holiday": get_recommendation("holiday", weather_info),
    }

    return render_template(
        "result.html",
        city=city,
        weather=weather_info,
        recommendations=recommendations,
        unit_symbol=unit_symbol,
        is_metric=is_metric
    )


@app.route("/toggle_units", methods=["POST"])
def toggle_units_route():
    toggle_units()
    city = request.form.get("city") or "London"  # fallback

    weather_info, error = get_weather(city)
    if error:
        return jsonify({"success": False, "error": error})

    unit_symbol = "°C" if is_metric else "°F"

    return jsonify({
        "success": True,
        "weather": weather_info,
        "unit_symbol": unit_symbol
    })


if __name__ == "__main__":
    app.run(debug=True)

