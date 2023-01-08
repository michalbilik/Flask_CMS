from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from wtforms.widgets import TextArea


# Create a Flask Instance
app = Flask(__name__)

#Secret Key
app.config['SECRET_KEY'] = "secret key for CRF"

#Add Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#Connecting to MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'

#Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255)) #url for a specific post

# Create a Posts Form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")
    
@app.route('/posts')
def posts():
    # Quering the posts from the dataase
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

#Page for 1 individual post / project
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)
    
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        #Update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated.")
        return redirect(url_for('post', id=post.id)) #redirects to the edited post
    form.title.data = post.title
    form.author.data = post.author
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template('edit_post.html', form=form)

@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        
        #Return a message
        flash("Blog post was deleted!")
        #Redirect to quered posts
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
    
    except:
        flash("There was a problem with deleting the  project")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
        
    
        
    
    
#html website to add posts
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
		# Clear The Form
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''

		# Add post data to database
		db.session.add(post)
		db.session.commit()

		# Return a Message
		flash("Blog Post Submitted Successfully!")

	# Redirect to the webpage
	return render_template("add_post.html", form=form)    

#Json test
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


#Create db Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True) #primary_key - this makes a uniqe ID
    name = db.Column(db.String(50), nullable=False) #nullabe=False this feeld cannot be empty
    email = db.Column(db.String(200), nullable=False, unique=True) #checks if this email was used before
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    #passwords
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    #changing password to hash
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    #Create a string
    def __repr__(self):
        return '<Name %r>' % self.name 
    
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField("Submit")
    
    
@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User Deleted Successfully!")

		our_users = Users.query.order_by(Users.date_added)
		return render_template("add_user.html", 
		form=form,
		name=name,
		our_users=our_users)

	except:
		flash("Whoops! There was a problem deleting user, try again...")
		return render_template("add_user.html", 
		form=form, name=name,our_users=our_users)
 
 
#Update Database Record Page
@app.route('/update/<int:id>', methods=['GET', 'POST']) 
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("update.html", 
				form=form,
				name_to_update = name_to_update)
		except:
			flash("Error!  Looks like there was a problem...try again!")
			return render_template("update.html", 
				form=form,
				name_to_update = name_to_update)
	else:
		return render_template("update.html", 
				form=form,
				name_to_update = name_to_update,
				id = id)
      
# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")
 
class PasswordForm(FlaskForm):
	email = StringField("What's Your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

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



 
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit(): #if the form is submited and it is valid then
        user = Users.query.filter_by(email=form.email.data).first() #we check if the new user exists with this email
        if user is None: #if user doesn't eixsts
            #hashing the passowrd
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)            
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
        form = form,
        name = name,
        our_users = our_users)
    
    
#Create Password Test Page
# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()


	# Validate Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear the form
		form.email.data = ''
		form.password_hash.data = ''

		# Lookup User By Email Address
		pw_to_check = Users.query.filter_by(email=email).first()

		# Check Hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("test_pw.html", 
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)   



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
 
 
 