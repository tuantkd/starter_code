from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
db = SQLAlchemy()

class Venue(db.Model):
  __tablename__ = 'venue'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120), nullable=True)
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  website_link = db.Column(db.String(120), nullable=True)
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(800), nullable=True)
  created_on = db.Column(db.DateTime, default=datetime.utcnow)
  shows = db.relationship('Shows', backref='venue', lazy='joined', cascade="all, delete")

  def __repr__(self):
    return f'<Venue {self.id} {self.name} ...>'
    
class Artist(db.Model):
  __tablename__ = 'artist'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String), nullable=False)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  website_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(800), nullable=True)
  created_on = db.Column(db.DateTime, default=datetime.utcnow)
  shows = db.relationship('Shows', backref='artist', lazy='joined', cascade="all, delete")

  def __repr__(self):
    return f'<Artist {self.id} {self.name} ...>'
  

class Shows(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id))
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id))
  start_time = db.Column(db.DateTime, default=datetime.utcnow)
  def __repr__(self):
    return f'<Artist {self.id} {self.name} ...>'
  
class Search:
  def __init__(self, id, name, num_upcoming_shows):
    self.id = id
    self.name = name
    self.num_upcoming_shows = num_upcoming_shows

class StateCity:
  def __init__(self, state, city):
    self.state = state
    self.city = city

class ShowVenueArtist:
  def __init__(self, show_id, venue_id, venue_name, artist_id, artist_name, artist_image_link, start_time):
    self.show_id = show_id
    self.venue_id = venue_id
    self.venue_name = venue_name
    self.artist_id = artist_id
    self.artist_name = artist_name
    self.artist_image_link = artist_image_link
    self.start_time = start_time