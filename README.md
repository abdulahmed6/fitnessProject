# 💪 Fit4U


Fit4U is a personalized fitness and nutrition web app that helps users stay consistent with their health goals. Whether you want to lose weight, build muscle, or simply live healthier, Fit4U generates tailored weekly workout plans and recipe recommendations based on your body metrics and dietary needs.

### 🚀 Features

🔐 User Authentication (Register/Login)

📊 Personalized Workout Plan using Gemini API

🍽️ Custom Recipe Recommendations using Spoonacular API

🧠 Body metric storage (height, weight, age, goal, gender)

🖼️ Exercise illustrations and YouTube tutorial links

🧼 Clean and responsive Bootstrap-based UI

🛠️ Tech Stack
Backend: Flask, SQLAlchemy, Flask-Login, Flask-Migrate


Frontend: HTML, CSS (Bootstrap), Jinja2

APIs: Google Gemini (for workouts), Spoonacular (for recipes)

Database: SQLite

Authentication: Flask-Login, Werkzeug Security

## Run it locally

Requires Python 3.11+.

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then fill in your API keys
python app.py
```

Open http://127.0.0.1:5001, register an account, and log in. The SQLite database (`instance/site.db`) is created automatically on first run.

| Variable | What it's for |
| --- | --- |
| `FLASK_KEY` | Flask session secret. Any long random string. |
| `GENAI_KEY` | Google AI Studio key for workout plans. |
| `GENAI_MODEL` | Gemini model name (default `gemini-2.5-flash`). |
| `SPOONACULAR_KEY` | Spoonacular key for recipe search. |
| `FLASK_DEBUG` | Set to `1` for the Flask debugger locally. Leave at `0` anywhere else. |

## Run the tests

```bash
python tests/test_basic.py
python tests/test_users.py
python tests/test_apis.py
```

The API tests mock Gemini and Spoonacular, so no keys are needed.

## Deploy (Render free tier)

`render.yaml` deploys the app as a free Render web service using gunicorn. On Render, choose **New + → Blueprint**, select this repo, and enter `GENAI_KEY` and `SPOONACULAR_KEY` when prompted. The free tier's disk is wiped on each deploy or restart, so registered accounts don't persist there.

