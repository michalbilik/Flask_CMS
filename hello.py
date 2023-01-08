from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired #later add validator for email etc
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a Flask Instance
app = Flask(__name__)

#Secret Key
app.config['SECRET_KEY'] = "secret key for CRF"

#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#Initialize The Database
db = SQLAlchemy(app)

#Create db Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True) #primary_key - this makes a uniqe ID
    name = db.Column(db.String(50), nullable=False) #nullabe=False this feeld cannot be empty
    email = db.Column(db.String(200), nullable=False, unique=True) #checks if this email was used before
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    #Create a string
    def __repr__(self):
        return '<Name %r>' % self.name 
    
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	submit = SubmitField("Submit")
    

#Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")




#def index():
#	return "<h1>Hello World!</h1>"

# FILTERS!!!
#safe
#capitalize
#lower
#upper
#title
#trim
#striptags

# Create a route decorator
@app.route('/')
def index():
	first_name = "John"
	stuff = "This is bold text"

	favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 41]
	return render_template("index.html", 
		first_name=first_name,
		stuff=stuff,
		favorite_pizza = favorite_pizza)

# localhost:5000/AboutMe
@app.route('/aboutMe')
def aboutMe():
	return render_template("aboutMe.html")

@app.route('/user/<name>')

def user(name):
	return render_template("user.html", user_name=name)

# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500


@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()
	# Validate Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''

	return render_template("name.html", 
		name = name,
		form = form)
 
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit(): #if the form is submited and it is valid then
        user = Users.query.filter_by(email=form.email.data).first() #we check if the new user exists with this email
        if user is None: #if user doesn't eixsts
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
        form = form,
        name = name,
        our_users = our_users)
 