#! python
import flask
from flask import request, session
import sqlalchemy

import db

app=flask.Flask(__name__)
app.secret_key = "this is a secret key whatever i'll change it later"

@app.route('/')
def home():
	return flask.render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return flask.render_template('login.html')
	else:
		user = db.User.login(request.form['email'], request.form['password'])
		if user:
			session['username'] = user.username
			session['user_id'] = user.id		
			return flask.redirect(flask.url_for('home'))
		else:
			flask.flash('Invalid username/password combination.')
			return flask.redirect(flask.url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
	if request.method == 'GET':
		return flask.render_template('account.html')



@app.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('user_id', None)
	return flask.redirect(flask.url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return flask.render_template('register.html')
	
	else:
		username = request.form.get('username')
		password = request.form.get('password')
		email = request.form.get('email')
		if not username or not password or not email:
			flask.flash('you must enter a display name, an email, and a password to register')
		
	password, salt = db.User.hash_pw(password)
	user = db.User(username=username, password=password, salt=salt, email=email)
	db.session.add(user)
	try:
		db.session.commit()
	except sqlalchemy.exc.DBAPIError as e:
		flask.flash('An account already exists for this email')
		return flask.redirect(flask.url_for('register'))
	
	session.permanent = True
	session['user_id'] = user.id
	return flask.redirect(flask.url_for('home'))

if __name__=='__main__':
	app.run()
