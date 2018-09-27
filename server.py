#! python
import flask

app=flask.Flask(__name__)

@app.route('/')
def home():
	print('home')
	return flask.render_template('home.html', session=None)

@app.route('/login')
def login():
	print('login')
	return flask.render_template('login.html', session=None)

if __name__=='__main__':
	app.run()
