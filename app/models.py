from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt

participants = db.Table('participants',
    db.Column('participant_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    events_created = db.relationship('Event', backref='creator', lazy='dynamic')

    def __repr__(self):
        return '<User: {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        ).decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algoritms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
       

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post: {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    datetime = db.Column(db.DateTime, index=True)
    info = db.Column(db.String(500))

    participants = db.relationship('User', secondary=participants, lazy='subquery', backref=db.backref('events_joined', lazy=True))

    def __repr__(self):
        return '<Event: {} {}>'.format(self.location.name, self.datetime.strftime("%A %d %B %Y, %H:%M"))

    def add_participant(self, user):
        self.participants.append(user)
    
    def remove_participant(self, user):
        self.participants.remove(user)
    
    #def has_participant(self, user):
    #    return self.participants.filter(participants.user_id == user.id).count() > 0

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    events = db.relationship('Event', backref='location', lazy=True)

    def __repr__(self):
        return '<Location: {}>'.format(self.name)

