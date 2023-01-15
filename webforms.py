from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

#Flask Forms file

# Create Login Form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Login")
 
 
# Create a Posts Form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	#content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	content = CKEditorField('Content', validators=[DataRequired()]) #CKEditor added
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	post_pic = FileField("Post Pic")
	submit = SubmitField("Submit")
 
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	about_author = TextAreaField("About Author")
	password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
	password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
	profile_pic = FileField("Profile Pic")
	profile_background = StringField("Background")
	submit = SubmitField("Submit")
 
class ContactForm(FlaskForm):
	contact_name = StringField("Your name", validators=[DataRequired()])
	contact_lastname = StringField("Your last name", validators=[DataRequired()])
	contact_email = StringField("Your email", validators=[DataRequired()])
	contact_message = StringField("Message", validators=[DataRequired()])
	submit = SubmitField("Send")
 
# Create a Form Class
class NamerForm(FlaskForm):
	name = StringField("", validators=[DataRequired()])
	submit = SubmitField("Submit")
 
 
class PasswordForm(FlaskForm):
	email = StringField("What's Your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")
 