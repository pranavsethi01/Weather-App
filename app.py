# Import necessary libraries and modules
from flask import Flask, render_template, request, redirect, url_for, make_response
import requests
import os
import json
import csv
import io
from datetime import datetime
from dotenv import load_dotenv
from models import db, WeatherRecord

# Load environment variables (like API key) from .env file
load_dotenv()

# Initialize Flask app and configure database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables 
with app.app_context():
    db.create_all()

# Set API base and API key
API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Convert temperature from Kelvin to Fahrenheit
def kelvin_to_fahrenheit(k):
    return round((k - 273.15) * 9/5 + 32, 2)

# Checking if input is a valid US zip code (5 digits)
def is_zipcode(text):
    return text.strip().isdigit() and len(text.strip()) == 5

# Checking if input is in "latitude,longitude" coordinate format
def is_coordinates(text):
    try:
        parts = text.split(',')
        if len(parts) != 2:
            return False
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except:
        return False

# Main route, it will form input + show weather and forecast
@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    error = None

    # Retrieve form data
    if request.method == "POST":
        location = request.form.get("location")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        # Validate date inputs
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            error = "Invalid date format."
            return render_template("index.html", error=error)

        if not location or not start_date or not end_date:
            error = "Please fill all fields."
        elif start_date_obj > end_date_obj:
            error = "Start date must be before end date."
        else:

            # Figuring API endpoint based on input type
            if is_coordinates(location):
                lat, lon = location.split(',')
                weather_url = f"{BASE_URL}/weather?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}"
                forecast_url = f"{BASE_URL}/forecast?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}"
            elif is_zipcode(location):
                weather_url = f"{BASE_URL}/weather?zip={location.strip()},us&appid={API_KEY}"
                forecast_url = f"{BASE_URL}/forecast?zip={location.strip()},us&appid={API_KEY}"
            else:
                weather_url = f"{BASE_URL}/weather?q={location.strip()}&appid={API_KEY}"
                forecast_url = f"{BASE_URL}/forecast?q={location.strip()}&appid={API_KEY}"

            # Calling API
            weather_res = requests.get(weather_url).json()
            forecast_res = requests.get(forecast_url).json()

            if weather_res.get("cod") != 200:
                error = weather_res.get("message", "Error fetching weather.")
            else:

                # Extract current weather data
                weather_data = {
                    "location": f"{weather_res['name']}, {weather_res['sys']['country']}",
                    "lat": weather_res["coord"]["lat"],
                    "lon": weather_res["coord"]["lon"],
                    "temp": kelvin_to_fahrenheit(weather_res["main"]["temp"]),
                    "description": weather_res["weather"][0]["description"].title(),
                    "humidity": weather_res["main"]["humidity"],
                    "wind": weather_res["wind"]["speed"],
                    "icon": weather_res["weather"][0]["icon"]
                }

                forecast_data = []

                # Extracting forecast data for the noon time only, 12PM
                for entry in forecast_res.get("list", []):
                    if "12:00:00" in entry["dt_txt"]:
                        date_str = entry["dt_txt"].split(" ")[0]
                        forecast_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        if start_date_obj <= forecast_date <= end_date_obj:
                            forecast_data.append({
                                "date": date_str,
                                "temp": kelvin_to_fahrenheit(entry["main"]["temp"]),
                                "description": entry["weather"][0]["description"].title(),
                                "icon": entry["weather"][0]["icon"]
                            })

                # Saving records to DB  
                record = WeatherRecord(
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                    data=json.dumps({"weather": weather_data, "forecast": forecast_data})
                )
                db.session.add(record)
                db.session.commit()

                # Staying on same page
                return render_template("index.html", weather=weather_data, forecast=forecast_data)

    return render_template("index.html", weather=weather_data, forecast=forecast_data, error=error)

# View all stored weather records
@app.route("/records")
def records():
    all_records = WeatherRecord.query.all()
    for rec in all_records:
        rec.parsed_data = json.loads(rec.data)
    return render_template("records.html", records=all_records)

# Updating an existing record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    record = WeatherRecord.query.get_or_404(id)
    if request.method == "POST":
        location = request.form.get("location")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Determine which URL to call
        if is_coordinates(location):
            lat, lon = location.split(',')
            weather_url = f"{BASE_URL}/weather?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}"
            forecast_url = f"{BASE_URL}/forecast?lat={lat.strip()}&lon={lon.strip()}&appid={API_KEY}"
        elif is_zipcode(location):
            weather_url = f"{BASE_URL}/weather?zip={location.strip()},us&appid={API_KEY}"
            forecast_url = f"{BASE_URL}/forecast?zip={location.strip()},us&appid={API_KEY}"
        else:
            weather_url = f"{BASE_URL}/weather?q={location.strip()}&appid={API_KEY}"
            forecast_url = f"{BASE_URL}/forecast?q={location.strip()}&appid={API_KEY}"

        weather_res = requests.get(weather_url).json()
        forecast_res = requests.get(forecast_url).json()

        if weather_res.get("cod") == 200:
            weather_data = {
                "location": f"{weather_res['name']}, {weather_res['sys']['country']}",
                "lat": weather_res["coord"]["lat"],
                "lon": weather_res["coord"]["lon"],
                "temp": kelvin_to_fahrenheit(weather_res["main"]["temp"]),
                "description": weather_res["weather"][0]["description"].title(),
                "humidity": weather_res["main"]["humidity"],
                "wind": weather_res["wind"]["speed"],
                "icon": weather_res["weather"][0]["icon"]
            }

            forecast_data = []
            for entry in forecast_res.get("list", []):
                if "12:00:00" in entry["dt_txt"]:
                    date_str = entry["dt_txt"].split(" ")[0]
                    forecast_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if start_date_obj <= forecast_date <= end_date_obj:
                        forecast_data.append({
                            "date": date_str,
                            "temp": kelvin_to_fahrenheit(entry["main"]["temp"]),
                            "description": entry["weather"][0]["description"].title(),
                            "icon": entry["weather"][0]["icon"]
                        })

            # Update fields and weather data
            record.location = location
            record.start_date = start_date
            record.end_date = end_date
            record.data = json.dumps({"weather": weather_data, "forecast": forecast_data})
            db.session.commit()

        return redirect(url_for('records'))

    return render_template("update.html", record=record)


# Deleting a saved record
@app.route("/delete/<int:id>")
def delete(id):
    record = WeatherRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('records'))


# Export records to JSON, CSV, or Markdown
@app.route("/export/<format>")
def export_data(format):
    records = WeatherRecord.query.all()
    export_list = []

    for rec in records:
        data = json.loads(rec.data)
        export_list.append({
            "Location": rec.location,
            "Start Date": rec.start_date,
            "End Date": rec.end_date,
            "Temp": data["weather"]["temp"],
            "Humidity": data["weather"]["humidity"],
            "Description": data["weather"]["description"]
        })

    # Logic for JSON
    if format == "json":
        response = make_response(json.dumps(export_list, indent=2))
        response.headers["Content-Disposition"] = "attachment; filename=weather_data.json"
        response.headers["Content-Type"] = "application/json"
        return response
    
    # Logic for CSV
    elif format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=export_list[0].keys())
        writer.writeheader()
        writer.writerows(export_list)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=weather_data.csv"
        response.headers["Content-Type"] = "text/csv"
        return response

    # Logic for Markdown
    elif format == "md":
        output = "# Weather Records\n\n"
        for row in export_list:
            output += f"### {row['Location']}\n"
            output += f"- Dates: {row['Start Date']} -> {row['End Date']}\n"
            output += f"- Temp: {row['Temp']}°F\n"
            output += f"- Humidity: {row['Humidity']}%\n"
            output += f"- Condition: {row['Description']}\n\n"
        response = make_response(output)
        response.headers["Content-Disposition"] = "attachment; filename=weather_data.md"
        response.headers["Content-Type"] = "text/markdown"
        return response

    return "Invalid export format", 400

if __name__ == "__main__":
    app.run(debug=True)
