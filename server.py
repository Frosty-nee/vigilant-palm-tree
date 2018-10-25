#! python
import flask
from flask import request, session
import sqlalchemy
import binascii

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

@app.route('/game')
def game():
	if request.method == 'GET':
		return flask.render_template('game.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
	if request.method == 'GET':
		return flask.render_template('account.html')
	if request.method == 'POST':
		if request.form['new_password'] != request.form['confirm_new_password']:
			flask.flash('Passwords do not match')
			return flask.redirect(flask.url_for('account'))
		user = db.session.query(db.User).filter(db.User.id == session['user_id']).first()
		print(user.password)
		print(db.User.hash_pw(request.form['current_password'], binascii.unhexlify(user.salt)))
		if db.User.hash_pw(request.form['current_password'], binascii.unhexlify(user.salt))[0] == user.password:
			new_pw = db.User.hash_pw(request.form['new_password'], binascii.unhexlify(user.salt))
			user.password = new_pw
			db.session.commit()
			flask.flash('password updated successfully')
		else:
			flask.flash('current password incorrect')
		return flask.redirect(flask.url_for('account'))
	
		

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
