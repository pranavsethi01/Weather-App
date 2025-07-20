# Import SQLAlchemy 
from flask_sqlalchemy import SQLAlchemy

# Creating a SQLAlchemy instance to be used with the Flask app
db = SQLAlchemy()

# Defining class the WeatherRecord model to represent saved weather data
class WeatherRecord(db.Model):

    # Primary key for the record
    id = db.Column(db.Integer, primary_key=True)

    # Location entered by user (e.g., city name, zip code, or coordinates)
    location = db.Column(db.String(100), nullable=False)

    # Start date of the weather forecast query
    start_date = db.Column(db.String(10), nullable=False)

    # End date of the weather forecast query
    end_date = db.Column(db.String(10), nullable=False)

    # Storing full weather and forecast data as JSON/text format
    data = db.Column(db.Text, nullable=False) 
