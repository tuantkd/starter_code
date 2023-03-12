from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import (
    StringField, 
    SelectField, 
    SelectMultipleField, 
    DateTimeField, 
    BooleanField
)
from wtforms.validators import DataRequired, URL
import re

state_choices = [
    ('AL', 'AL'),
    ('AK', 'AK'),
    ('AZ', 'AZ'),
    ('AR', 'AR'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DE', 'DE'),
    ('DC', 'DC'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('IA', 'IA'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('ME', 'ME'),
    ('MT', 'MT'),
    ('NE', 'NE'),
    ('NV', 'NV'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NY', 'NY'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('MD', 'MD'),
    ('MA', 'MA'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MS', 'MS'),
    ('MO', 'MO'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VT', 'VT'),
    ('VA', 'VA'),
    ('WA', 'WA'),
    ('WV', 'WV'),
    ('WI', 'WI'),
    ('WY', 'WY'),
]

genres_choices = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]


def is_valid_phone(number):
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)


class ShowForm(Form):
    artist_id = StringField('artist_id')
    venue_id = StringField('venue_id')
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today(),
        format='%Y-%m-%d %H:%M:%S'
    )

    def validate(self, **kwargs):
        if not super().validate():
            return False

        existing_show = Shows.query.filter_by(
            artist_id=self.artist_id.data,
            venue_id=self.venue_id.data,
            start_time=self.start_time.data
        ).first()

        if existing_show:
            self.artist_id.errors.append('A show with the same artist_id, venue_id, and start_time already exists.')
            self.venue_id.errors.append('A show with the same artist_id, venue_id, and start_time already exists.')
            self.start_time.errors.append('A show with the same artist_id, venue_id, and start_time already exists.')
            return False

        return True


class VenueForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=state_choices)
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=genres_choices)
    facebook_link = StringField('facebook_link', validators=[URL()])
    website_link = StringField('website_link')
    seeking_talent = BooleanField('seeking_talent', default=False)
    seeking_description = StringField('seeking_description')



class ArtistForm(Form):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=state_choices)
    phone = StringField('phone')
    image_link = StringField('image_link')
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=genres_choices)
    facebook_link = StringField('facebook_link', validators=[URL()])
    website_link = StringField('website_link')
    seeking_venue = BooleanField('seeking_venue', default=False)
    seeking_description = StringField('seeking_description')

