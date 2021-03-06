from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, TextField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField
from wtforms.validators import DataRequired, ValidationError, Length
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data.lower() != self.original_username.lower():
            user = User.query.filter_by(username=self.username.data.lower()).first()
            if user is not None:
                raise ValidationError("Please use different username.")


class CreateEventForm(FlaskForm):
    location = TextField("Where?", validators=[DataRequired(), Length(min=2, max=50)])
    date = DateField("When?", validators=[DataRequired()])
    time = TimeField("What time?", validators=[DataRequired()])
    info = TextAreaField("Extra info")
    submit = SubmitField("Submit")


class AddCoordinatesForm(FlaskForm):
    latitude = DecimalField("Latitude")
    longitude = DecimalField("Longitude")
    submit = SubmitField("Submit")
