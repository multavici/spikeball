## Imports

# standard library
from time import time
from hashlib import md5
from datetime import datetime

# flask
import jwt  # jason web token
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# relative
from . import db, login

## load logged in user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


## Many-to-many connection tables
participants = db.Table(
    "participants",
    db.Column("participant_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("event_id", db.Integer, db.ForeignKey("event.id")),
)

# connection between teams and players
team_player = db.Table(
    "team_player",
    db.Column("team_id", db.Integer, db.ForeignKey("team.id")),
    db.Column("player_id", db.Integer, db.ForeignKey("user.id")),
)

# connection between matches and teams
match_team = db.Table(
    "match_team",
    db.Column("match_id", db.Integer, db.ForeignKey("match.id")),
    db.Column("team_id", db.Integer, db.ForeignKey("team.id")),
)

## Tables

# user table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # events created by user:
    events_created = db.relationship("Event", backref="creator", lazy="dynamic")

    # teams this user is part of:
    teams = db.relationship("Team", secondary=team_player, back_populates="players")

    def __init__(self, username=None, email=None, password=None, about_me=None):
        super(User, self).__init__(
            username=username.lower(),
            email=email.lower(),
            password_hash=generate_password_hash(password),
            about_me=about_me,
        )

    def __repr__(self):
        return "<User: {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algoritms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(30))

    # players in this team
    # NOTE: this should be limited to two; this can be achieved in a custom __init__ function
    players = db.relationship("User", secondary=team_player, back_populates="teams")

    # matches played by this team
    matches = db.relationship("Match", secondary=match_team, back_populates="teams")

    def __init__(self, teamname=None, player1=None, player2=None):
        if teamname is None:
            raise ValueError("Cannot create team: no team name specified!")
        if player1 is None and player2 is None:
            raise ValueError("Cannot create team: no players specified!")
        elif player1 is None:
            raise ValueError("Cannot create team: player1 not specified!")
        elif player2 is None:
            raise ValueError("Cannot create team: player2 not specified!")
        super(Team, self).__init__(
            teamname=teamname.lower(), players=[player1, player2]
        )

    def __repr__(self):
        return f"<Team {self.teamname}>"


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    score1 = db.Column(db.Integer)
    score2 = db.Column(db.Integer)

    # teams playing this match:
    # NOTE: this should be limited to two; this can be achieved in a custom __init__ function
    teams = db.relationship("Team", secondary=match_team, back_populates="matches")

    @property
    def team1(self):
        return self.teams[0]

    @property
    def team2(self):
        return self.teams[1]

    def __init__(self, team1=None, team2=None, score1=None, score2=None, date=None):
        if team1 is None and team2 is None:
            raise ValueError("Cannot create team: no teams specified!")
        elif team1 is None:
            raise ValueError("Cannot create team: team1 not specified!")
        elif team2 is None:
            raise ValueError("Cannot create team: team2 not specified!")
        if date is None:
            date = datetime.utcnow()
        if score1 is None or score2 is None:
            raise ValueError("No valid score supplied for the match")
        super(Match, self).__init__(
            teams=[team1, team2], date=date, score1=int(score1), score2=int(score2)
        )

    def __repr__(self):
        t1, t2 = self.teams
        return f"<Match {t1.teamname} v {t2.teamname}>"


# event table
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    datetime = db.Column(db.DateTime, index=True)
    info = db.Column(db.String(500))

    participants = db.relationship(
        "User",
        secondary=participants,
        lazy="subquery",
        backref=db.backref("events_joined", lazy=True),
    )

    def __repr__(self):
        return "<Event: {} {}>".format(
            self.location.name, self.datetime.strftime("%A %d %B %Y, %H:%M")
        )

    def add_participant(self, user):
        self.participants.append(user)

    def remove_participant(self, user):
        self.participants.remove(user)


# location table
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    events = db.relationship("Event", backref="location", lazy=True)

    def __init__(self, name=None, latitude=None, longitude=None):
        super(Location, self).__init__(
            name=name.lower(), latitude=latitude, longitude=longitude
        )

    def __repr__(self):
        return "<Location: {}>".format(self.name)
