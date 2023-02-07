from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import session
from flask_socketio import SocketIO, send

from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = '77e3448fbce2f4a2f5e6e98fc78'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ADM_CONF_USERNAME = 'admin'
ADM_CONF_FULLNAME = 'admin adminovich'
ADM_CONF_PASSWORD = 'somehash'

db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.Text(), unique=True, nullable=False)
    user_name = db.Column(db.Text(), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return '<Client %r>' % self.id

class Messages(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg_author = db.Column(db.String())
    msg_content = db.Column(db.Text())
    chat_room = db.Column(db.String())

class Chat_rooms(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    msg_author = db.Column(db.String())

@app.route("/")
@app.route("/main")
def home():
    if 'name' in session:
        this_account_session = session['name']
        clients_list = Client.query.all()
        return render_template("main_page.html", clients_list=clients_list, this_acc=this_account_session)
    
    return redirect("/reg")

@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        fname = request.form['name_holder']
        uname = request.form['username_holder']
        password = request.form['password_holder']

        session['name'] = uname

        add_to_db = Client(
            full_name=fname,
            user_name=uname,
            password=password
        )

        db.session.add(add_to_db)
        db.session.commit()
        return redirect('/')

    return render_template('reg.html')

@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':
        uname = request.form['username_holder']
        passw = request.form['password_holder']

        cli_uname = Client.query.filter(Client.user_name == uname).all()
        cli_passw = Client.query.filter(Client.password == passw).all()

        if cli_uname and cli_passw:
            session['name'] = uname

            return redirect('/')
        else:
            unsuccess = 'Auth error'
            return render_template('auth.html', a_err=unsuccess)

    return render_template('auth.html')

@app.route('/chats')
def chats():
    if session['name'] == 'admin':
        chats = Chat_rooms.query.all()
        return render_template('chats.html', rooms=chats)

    return redirect('/')

@app.route('/chat/<username>', methods=['POST', 'GET'])
def chat(username):
    isAuthor = session['name'] == username
    isAdmin = session['name'] == ADM_CONF_USERNAME

    if isAuthor or isAdmin:
        if request.method == 'POST':

            room_checker = Chat_rooms.query.filter(Chat_rooms.msg_author == username).all()
            if not room_checker:
                set_chat_room = Chat_rooms(msg_author=username)
                db.session.add(set_chat_room)
                db.session.commit()

            message = request.form['message_content']
            message_author = session['name']

            post_message = Messages(
                msg_content=message,
                msg_author=message_author,
                chat_room=username
            )

            db.session.add(post_message)
            db.session.commit()
            return redirect(f'/chat/{username}')
        
        chat = Messages.query.filter(Messages.chat_room == username)
        return render_template('chat.html', msg_chat=chat)

if __name__ == "__main__":
    db.create_all()
    app.run(host='localhost')