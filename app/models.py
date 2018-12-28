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

    events_created = db.relationship('Event', backref='creator', lazy='dynamic')
    games_registered = db.relationship('Game', backref='creator', lazy='dynamic')

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
    
    def teams(self):
        return self.teams_as_player1 + self.teams_as_player2
       

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

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    player1 = db.relationship('User', foreign_keys=[player1_id], backref='teams_as_player1', lazy='subquery')
    player2 = db.relationship('User', foreign_keys=[player2_id], backref='teams_as_player2', lazy='subquery')

    def games(self):
        return self.games_as_team1 + self.games_as_team2

    @classmethod
    def get_or_create(cls, player1_id, player2_id):
        try:
            return Team.query.filter_by(player1_id=player1_id, player2_id=player2_id).one()
        except:
            try:
                return Team.query.filter_by(player1_id=player2_id, player2_id=player1_id).one()
            except:
                t = Team(player1_id=player1_id, player2_id=player2_id)
                db.session.add(t)
                db.session.commit()
                return t


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team1_wins = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    points_set1_team1 = db.Column(db.Integer)
    points_set1_team2 = db.Column(db.Integer)
    points_set2_team1 = db.Column(db.Integer)
    points_set2_team2 = db.Column(db.Integer)
    points_set3_team1 = db.Column(db.Integer)
    points_set3_team2 = db.Column(db.Integer)

    team1 = db.relationship('Team', foreign_keys=[team1_id], backref='games_as_team1', lazy='subquery')
    team2 = db.relationship('Team', foreign_keys=[team2_id], backref='games_as_team2', lazy='subquery')

    def __init__(self, user_id, team1_id, team2_id, 
            points_set1_team1, points_set1_team2, 
            points_set2_team1, points_set2_team2, 
            points_set3_team1, points_set3_team2):
        self.user_id = user_id
        self.team1_id = team1_id
        self.team2_id = team2_id
        self.points_set1_team1 = points_set1_team1
        self.points_set1_team2 = points_set1_team2
        self.points_set2_team1 = points_set2_team1
        self.points_set2_team2 = points_set2_team2
        self.points_set3_team1 = points_set3_team1
        self.points_set3_team2 = points_set3_team2

        sets_team1, sets_team2 = 0, 0
        if points_set1_team1 > points_set1_team2:
            sets_team1 += 1
        else:
            sets_team2 += 1
        if points_set2_team1 > points_set2_team2:
            sets_team1 += 1
        else:
            sets_team2 += 1
        if points_set3_team1 > points_set3_team2:
            sets_team1 += 1
        else:
            sets_team2 += 1

        self.team1_wins = True if sets_team1 > sets_team2 else False