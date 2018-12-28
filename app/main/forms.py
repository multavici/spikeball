from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, TextField, DecimalField, SelectField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use different username.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class CreateEventForm(FlaskForm):
    location = TextField('Where?', validators=[DataRequired(), Length(min=2, max=50)])
    date = DateField('When?', validators=[DataRequired()])
    time = TimeField('What time?', validators=[DataRequired()])
    info = TextAreaField('Extra info')
    submit = SubmitField('Submit')

class AddCoordinatesForm(FlaskForm):
    latitude = DecimalField('Latitude')
    longitude = DecimalField('Longitude')
    submit = SubmitField('Submit')

class RegisterGameForm(FlaskForm):
    team1_player1 = SelectField('Player 1', coerce=int)
    team1_player2 = SelectField('Player 2', coerce=int)
    team2_player1 = SelectField('Player 1', coerce=int)
    team2_player2 = SelectField('Player 2', coerce=int)

    points_set1_team1 = IntegerField()
    points_set1_team2 = IntegerField()
    points_set2_team1 = IntegerField()
    points_set2_team2 = IntegerField()
    points_set3_team1 = IntegerField()
    points_set3_team2 = IntegerField()

    submit = SubmitField('Submit')
