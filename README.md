
# Weather Forecast App 

A full-stack web application built for the **AI Engineer Intern Assessment** at PM Accelerator. This app retrieves real-time weather data, forecasts, and visual maps using external APIs. It supports data persistence and CRUD operations using a database, and allows users to export weather data in multiple formats.


## Features Overview

### Core Functionality
- Accepts flexible location input: **City**, **ZIP Code**, or **GPS Coordinates**
- Fetches **current weather** and **5-day forecast** from OpenWeatherMap API
- Displays weather details: temperature, humidity, wind speed, description, and icons
- Embeds **Google Maps** to show the location visually
- Stores weather queries in **SQLite database**

### CRUD Operations (Assessment 2)
- **Create**: Save queries with location and date range
- **Read**: View all previous weather queries
- **Update**: Modify saved queries
- **Delete**: Remove saved records

### Additional Functionalities
- Export weather data in **JSON**, **CSV**, and **Markdown**
- Responsive UI using custom CSS
- Input validation for both location and date ranges

---

##  Tech Stack

| Layer      | Tools Used                         |
|------------|------------------------------------|
| Frontend   | HTML, CSS, Jinja2 (Flask templates)|
| Backend    | Python, Flask                      |
| Database   | SQLite, SQLAlchemy ORM             |
| APIs       | OpenWeatherMap, Google Maps Embed  |

---

## Getting Started

### Setup Instructions

1. **Clone the Repository**
```bash
git clone https://github.com/pranavsethi01/Weather-App.git
cd Weather-App
````

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Add API Key**
   Create a `.env` file:

```
WEATHER_API_KEY=your_openweathermap_api_key
```

4. **Run the App**

```bash
python app.py
```

Then open your browser at: [Weather APP Link]([http://127.0.0.1:5000](https://weather-app-vmrd.onrender.com/))

---

## Project Structure

```
├── app.py               # Main Flask app
├── models.py            # DB model for saved weather queries
├── templates/           # HTML templates (index, records and update)
├── static/              # CSS styling
├── weather.db           # SQLite DB (auto-created)
├── .env                 # API keys (user-provided)
├── requirements.txt
└── README.md
```

---

## Demo Video

[Link to Demo Video](#) *(url)*

---

## About the Project

This project was developed as part of the PM Accelerator internship assessment.
The app includes:

* Full API integration
* Basic to advanced CRUD features
* Export and visual mapping tools
* A link to [PM Accelerator on LinkedIn]([https://www.linkedin.com/company/product-manager-accelerator/](https://www.linkedin.com/school/pmaccelerator/posts/?feedView=all)) included on the home page

---
### Created by Pranav Sethi

