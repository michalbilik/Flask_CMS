from flask import Flask, render_template, flash, request, redirect, url_for, session
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, ContactForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid #unique user ID
import os #neede to save the profile pic
from flask_mail import Mail, Message


# Create a Flask Instance
app = Flask(__name__)
ckeditor = CKEditor(app)

#Secret Key
app.config['SECRET_KEY'] = "secret key for CRF"

#Add Database - connecting to MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgressql://kskiwdwpfzhxze:025f288af468d547bd7671b4f3424b0e92ff9f207283124f69f9de1c34e8dec7@ec2-34-197-84-74.compute-1.amazonaws.com:5432/decl7avrh3j6qd'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/our_users'

#Folder to save the images
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Initialize and migrate (after changes) the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '0b55e4b963635c'
app.config['MAIL_PASSWORD'] = '33c8c6626fa3d0'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)


#################################### ROUTES ####################################

# localhost:5000/AboutMe
@app.route('/aboutMe')
def aboutMe():
    #Three latest projects
    #projects = Posts.query.order_by(Posts.date_posted.desc()).limit(5).all()
    projects = Posts.query.filter_by(category='Projects').order_by(Posts.date_posted.desc()).limit(5).all()
    info_posts = Posts.query.filter_by(category='Information').order_by(Posts.date_posted.asc())

    #Test to get the profile picture
    user = Users.query.filter_by(id=1).first()
    profile_image = user.profile_pic
    profile_name = user.name
    profile_about_author = user.about_author
    profile_background=user.profile_background
    
    #Get info_post info
    
    
    return render_template("aboutMe.html", projects=projects, info_posts=info_posts, id=id,profile_image=profile_image,profile_name=profile_name, profile_about_author=profile_about_author, profile_background=profile_background)
 	

# Contact form
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    admin = Users.query.filter_by(id=1).first()
    admin_email=admin.email
    admin_image = admin.profile_pic
    admin_name = admin.name
    if form.validate_on_submit():
        name = form.contact_name.data
        lastname = form.contact_lastname.data
        email = form.contact_email.data
        message = form.contact_message.data
        topic=name+" "+lastname
        
        try:
            msg = Message(subject = topic , sender = email, recipients = [admin_email])
            msg.body = message
            mail.send(msg)
            session['flash_message'] = "Thanks! I will contact with you as soon as I can."
            return redirect(url_for('contact'))

        except:
            session['flash_message'] = "There was a problem sending this email! Try again."
            return redirect(url_for('contact'))
    else:
        flash_message = session.pop('flash_message', None)
        return render_template('contact.html', form=form, flash_message=flash_message, admin_email=admin_email, admin_name=admin_name, admin_image=admin_image)



    


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check the hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Succesfull.")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong password or user - Try Again!")
		else:
			flash("Wrong password or user - Try Again!")


	return render_template('login.html', form=form)

#Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Been Logged Out!")
	return redirect(url_for('login'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
	# Check logged in id vs. id to delete
	if id != 1:
		user_to_delete = Users.query.get_or_404(id)
		name = None
		form = UserForm()

		try:
			db.session.delete(user_to_delete)
			db.session.commit()
			flash("User Deleted Successfully!!")

			our_users = Users.query.order_by(Users.date_added)
			return render_template("add_user.html", 
			form=form,
			name=name,
			our_users=our_users)

		except:
			flash("Whoops! There was a problem deleting user, try again...")
			return render_template("add_user.html", 
			form=form, name=name,our_users=our_users)
	else:
		flash("Sorry, you can't delete that user! ")
		return redirect(url_for('dashboard'))
 
 
#Update Database Record Page
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required 
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.about_author = request.form['about_author']
		name_to_update.username = request.form['username']
		name_to_update.profile_background = request.form['profile_background']
		#Profile pic:
		#Check for profile picture
		if request.files['profile_pic']:
			name_to_update.profile_pic = request.files['profile_pic']
		
			#grab image name
			pic_filename = secure_filename(name_to_update.profile_pic.filename)
			#set unique ID, uuid1 - takes the date and time and randomises 
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			#Save the image
			saver = request.files['profile_pic']
			#change it to a string to save to db
			name_to_update.profile_pic = pic_name
			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("User Updated Successfully!")
				return render_template("dashboard.html", 
					form=form,
					name_to_update = name_to_update)
			except:
				flash("Error!  Looks like there was a problem...try again!")
				return render_template("update.html", 
					form=form,
					name_to_update = name_to_update)
		else:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update)
	else:
		return render_template("update.html", 
            form=form, 
            name_to_update = name_to_update, 
            id = id)

#Create dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard(): #copied data (below) from Update function so our dashboard has access to it 
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.username = request.form['username']
		name_to_update.profile_background = request.form['profile_background']
		try:
			db.session.commit()
			flash("User Updated Successfully!")
			return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update)
		except:
			flash("Error!  Looks like there was a problem...try again!")
			return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update)
	else:
		return render_template("dashboard.html", 
				form=form,
				name_to_update = name_to_update,
				id = id)


    
@app.route('/posts')
def posts():
    # Quering the posts from the dataase
    #posts = Posts.query.order_by(Posts.date_posted.desc())
    posts = Posts.query.filter_by(category='Projects').order_by(Posts.date_posted.desc())
    return render_template("posts.html", posts=posts)

#Page for 1 individual post / project
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    post_pic_name = post.post_pic
    return render_template('post.html', post=post, post_pic_name=post_pic_name)
    
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.category = form.category.data
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        if request.files['post_pic']:
            post_pic = request.files['post_pic']
            filename = secure_filename(post_pic.filename)
            post_pic_name = str(uuid.uuid1()) + "_" + filename
            saver_pic = request.files['post_pic']
            post_pic = post_pic_name
            post.post_pic = post_pic_name
            try:
                db.session.add(post)
                db.session.commit()
                saver_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_name))
                return redirect(url_for('post', id=post.id))
            except:
                flash("Error!  Looks like there was a problem...try again!")
                return redirect(url_for('post', id=post.id))
        else:
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('post', id=post.id)) #redirects to the edited post
    else:
     form.title.data = post.title
     form.author.data = post.author
     form.slug.data = post.slug
     form.content.data = post.content
     post.category = form.category.data
     return render_template('edit_post.html', form=form)
        

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        
        #Return a message
        flash("Blog post was deleted!")
        #Redirect to quered posts
        posts = Posts.query.order_by(Posts.date_posted.desc())
        return render_template("posts.html", posts=posts)
    
    except:
        flash("There was a problem with deleting the  project")
        posts = Posts.query.order_by(Posts.date_posted.desc())
        return render_template("posts.html", posts=posts)
        
#html website to add posts
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data, category=form.category.data)
		# Clear The Form
		form.category.data = ''
		form.title.data = ''  
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''
		post_pic = request.files['post_pic']
		#grab image name and make sure it is safe
		filename = secure_filename(post_pic.filename)
		#set unique ID, uuid1 - takes the date and time and randomises
		post_pic_name = str(uuid.uuid1()) + "_" + filename
		#save the image
		saver_pic = request.files['post_pic']
		#we change it to string to save to the db
		post_pic = post_pic_name
		# Add post data to database
		post.post_pic = post_pic_name
		db.session.add(post)
		db.session.commit()
		saver_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], post_pic_name))

		# Return a Message
		flash("Submitted Successfully!")

	# Redirect to the webpage
	return render_template("add_post.html", form=form)    



      
# Create a route decorator
@app.route('/')
def index():

	return render_template("index.html")
 
@app.route('/add', methods=['GET', 'POST'])
#@login_required - Turned off for production reasons
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit(): #if the form is submited and it is valid then
        user = Users.query.filter_by(email=form.email.data).first() #we check if the new user exists with this email
        if user is None: #if user doesn't eixsts
            #hashing the passowrd
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, username=form.username.data, email=form.email.data, password_hash=hashed_pw)            
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", 
        form = form,
        name = name,
        our_users = our_users)
    
    
#Create Password Test Page
# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
@login_required 
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



 
########################			JSON TEST 		########################################################


#Json test
@app.route('/date')
@login_required
def get_current_date():
    return {"Date": date.today()}

########################			Create Custom Error Pages 		########################################################

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500
 

 ########################			DATABASE MODELS 		########################################################

#Create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255)) #url for a specific post
    post_pic = db.Column(db.String(150), nullable=True)
 

#Create db Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #primary_key - this makes a uniqe ID
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False) #nullabe=False this feeld cannot be empty
    email = db.Column(db.String(200), nullable=False, unique=True) #checks if this email was used before
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(128))
    profile_background = db.Column(db.String(300), nullable=True)
    
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
 