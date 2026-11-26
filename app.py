import os
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm
from werkzeug.security import generate_password_hash
from apis import genai_fitness_plan, get_recipes
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (LoginManager, UserMixin, login_user, logout_user, login_required, current_user)
from flask_migrate import Migrate

import requests

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY", "dev-only-change-me")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)


  def __repr__(self):
    return f"User('{self.username}', '{self.email}')"

with app.app_context():
  db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            password = form.password.data
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('workouts'))
            else:
                raise ValueError("Invalid Email/Password")
        except Exception as e:
            return render_template('login.html', form=form, message=e)
    return render_template('login.html', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user_exists = User.query.filter_by(username=form.username.data).first()
            email_exists = User.query.filter_by(email=form.email.data).first()
            if user_exists:
                raise ValueError("User already exsists")
            if email_exists:
                raise ValueError("Email already in use")
            user = User(username=form.username.data, email=form.email.data, password=generate_password_hash(form.password.data))
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            message = f'An error has occured: {e}'
            return render_template("register.html", form=form, message=message)
    return render_template("register.html", form=form)

@app.route('/workouts', methods=['GET', 'POST'])
@login_required
def workouts():
    workout_plan = None
    image_link = []        
    if request.method == "POST":

        height = request.form['height']
        weight = request.form['weight']
        goal   = request.form['goal']
        age    = request.form.get('age')
        gender = request.form.get('gender')

        result = genai_fitness_plan(height, weight, goal, age, gender)
        workout_plan = result["plan"]
        image_link = result["images"]

    return render_template("workouts.html", workout_plan=workout_plan,image_link=image_link, status="Logout", page="/logout")

@app.route('/recipes', methods=["GET", "POST"])
@login_required
def recipes():
    diets = ["Gluten Free", "Ketogenic", "Vegetarian", "Lacto-Vegetarian", "Ovo-Vegetarian", "Vegan", "Pescetarian"]
    intolreances = ["Dairy", "Egg", "Gluten", "Grain", "Peanut", "Seafood", "Sesame", "Shellfish", "Soy", "Sulfite", "Tree Nut", "Wheat"]
    if request.method == "POST":
        params = {"apiKey": os.getenv("SPOONACULAR_KEY"), "query" : request.form["food"] ,"diet" : request.form.get("diet", "Whole30"), "intolerances":request.form.getlist('intolerances')}
        recipes = get_recipes("https://api.spoonacular.com/recipes/complexSearch", params)
        return render_template("recipes.html", diets=diets, intolerances=intolreances, recipes=recipes)
    return render_template("recipes.html", diets=diets, intolerances=intolreances)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/recipeurl", methods=["POST"])
@login_required
def recipeurl():
    recipe_id = request.form.get("recipe_id", "")
    if not recipe_id.isdigit():
        flash("Could not open that recipe.", "danger")
        return redirect(url_for("recipes"))
    params = {"apiKey": os.getenv("SPOONACULAR_KEY")}
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        source_url = response.json().get("sourceUrl")
    except (requests.RequestException, ValueError):
        source_url = None
    if not source_url:
        flash("Could not open that recipe right now. Please try again.", "danger")
        return redirect(url_for("recipes"))
    return redirect(source_url)


if __name__ == '__main__':
    # Debug mode exposes the Werkzeug debugger, so it is opt-in and local-only.
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5001")))
