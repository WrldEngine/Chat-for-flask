from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import session
from flask_socketio import SocketIO, send

from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '77e3448fbce2f4a2f5e6e98fc78d00706bbc7b9d17f1b1702ea5c58578e09f98'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins='*')

class Messages(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	msg_content = db.Column(db.Text)
	msg_author = db.Column(db.Text)

@socketio.on('message')
def handleMessage(data):
	print(f"Message: {data}")
	send(data, broadcast=True)

	save_message = Messages(msg_content=data['message'], msg_author=data['author'])
	db.session.add(save_message)
	db.session.commit()

@app.route('/')
def main_page():
	if 'name' in session:
		outp = Messages.query.all()
		author = session['name']
		return render_template('index.html', outp=outp, author=author)
	
	return redirect('/reg')

@app.route('/reg', methods=['GET', 'POST'])
def regist():
	if request.method == 'POST':
		session['name'] = request.form['name']
		return redirect('/')

	return render_template('reg.html')

if __name__ == '__main__':
	db.create_all()
	socketio.run(app)