import select
import sys
import json
import dateutil.parser
import babel
import logging
from flask import (
    Flask, 
    render_template, 
    request,
    flash, 
    redirect,
    session, 
    url_for
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from logging import Formatter, FileHandler
from sqlalchemy.orm import joinedload
from sqlalchemy import create_engine
from forms import ArtistForm, ShowForm, VenueForm

#==============================================================
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#==============================================================


#==============================================================
# Object
class Venue(db.Model):
  __tablename__ = 'venue'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120), nullable=True)
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120), nullable=True)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  website_link = db.Column(db.String(120), nullable=True)
  seeking_talent = db.Column(db.String(5), nullable=True)
  seeking_description = db.Column(db.String(800), nullable=True)
  num_upcoming_shows = db.Column(db.Integer, nullable=True)
  created_on = db.Column(db.DateTime, default=datetime.utcnow)

  shows = db.relationship('Shows')
  def __repr__(self):
    return f'<Venue {self.id} {self.name} ...>'
    
class Artist(db.Model):
  __tablename__ = 'artist'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120), nullable=True)
  image_link = db.Column(db.String(500), nullable=True)
  facebook_link = db.Column(db.String(120), nullable=True)
  website_link = db.Column(db.String(120), nullable=True)
  seeking_venue = db.Column(db.String(5), nullable=True)
  seeking_description = db.Column(db.String(800), nullable=True)
  created_on = db.Column(db.DateTime, default=datetime.utcnow)

  shows = db.relationship('Shows')
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
#==============================================================


#==============================================================
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

@app.route('/')
def index():
  return render_template('pages/home.html')
#==============================================================


#==============================================================
@app.route('/venues')
def venues():
  venues = Venue.query.all()
  states = []
  for venue in venues:
    check_exist = next((obj for obj in states if obj.state == venue.state), False)
    if check_exist == False:
      states.append(StateCity(venue.state, venue.city))

  return render_template('pages/venues.html', venues=venues, areas=states)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  result_venues = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term', '') + '%'))
  venues = []

  for venue in result_venues.all():
    artist_upcoming_ids = []

    upcoming_show_ids = Shows.query.filter(db.and_(Shows.start_time >= date.today().strftime("%Y-%m-%d"), Shows.venue_id == venue.id))
    for show in upcoming_show_ids.all():
      artist_upcoming_ids.append(show.venue_id)

    upcoming_shows = Artist.query.filter(db.and_(Venue.id.in_(artist_upcoming_ids)))
    venues.append(Search(venue.id, venue.name, upcoming_shows.count()))

  response = {
    "count": result_venues.count(),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_data = Venue.query.filter_by(id=venue_id).first()

  artist_upcoming_ids = []
  upcoming_show_ids = Shows.query.filter(db.and_(Shows.start_time >= date.today().strftime("%Y-%m-%d"), Shows.venue_id == venue_id))
  for show in upcoming_show_ids.all():
    artist_upcoming_ids.append(show.artist_id)
  upcoming_shows = Artist.query.filter(db.and_(Artist.id.in_(artist_upcoming_ids)))

  artist_past_ids = []
  past_show_ids = Shows.query.filter(db.and_(Shows.start_time < date.today().strftime("%Y-%m-%d"), Shows.venue_id == venue_id))
  for show in past_show_ids.all():
    artist_past_ids.append(show.artist_id)
  past_shows = Artist.query.filter(db.and_(Artist.id.in_(artist_past_ids)))

  venue = {
    "id": venue_id,
    "name": venue_data.name,
    "genres": json.loads(venue_data.genres),
    "address": venue_data.address,
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website": venue_data.website_link,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": json.loads(venue_data.seeking_talent.lower()),
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link,
    "past_shows": past_shows.all(),
    "past_shows_count": past_shows.count(),
    "upcoming_shows": upcoming_shows.all(),
    "upcoming_shows_count": upcoming_shows.count(),
  }
  data = list(filter(lambda d: d['id'] == venue_id, [venue]))[0]
  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form_venue = VenueForm()
    try: 
      venue = Venue(
        name = form_venue['name'].data,
        city = form_venue['city'].data,
        state = form_venue['state'].data,
        phone = form_venue['phone'].data,
        address = form_venue['address'].data,
        genres = json.dumps(form_venue['genres'].data),
        image_link = form_venue['image_link'].data,
        facebook_link = form_venue['facebook_link'].data,
        website_link = form_venue['website_link'].data,
        seeking_talent = form_venue['seeking_talent'].data,
        seeking_description = form_venue['seeking_description'].data
      )
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
    except Exception as e:
        db.session.rollback()
        print(sys.exc_info())
        print(e)
    finally:
        db.session.close()
  
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  db.session.delete(venue)
  return None

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_data = Venue.query.filter_by(id=venue_id).first()

  form = VenueForm()
  form['name'].data = venue_data.name
  form['city'].data = venue_data.city
  form['state'].data = venue_data.state
  form['address'].data = venue_data.address
  form['phone'].data = venue_data.phone
  form['genres'].data = json.loads(venue_data.genres)
  form['image_link'].data = venue_data.image_link
  form['website_link'].data = venue_data.website_link
  form['facebook_link'].data = venue_data.facebook_link
  form['seeking_talent'].data = json.loads(venue_data.seeking_talent.lower()),
  form['seeking_description'].data = venue_data.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form_venue = VenueForm()
  
  venue.name = form_venue['name'].data,
  venue.city = form_venue['city'].data,
  venue.state = form_venue['state'].data,
  venue.address = form_venue['address'].data,
  venue.phone = form_venue['phone'].data,
  venue.genres = json.dumps(form_venue['genres'].data),
  venue.image_link = form_venue['image_link'].data,
  venue.website_link = form_venue['website_link'].data,
  venue.facebook_link = form_venue['facebook_link'].data,
  venue.seeking_talent = json.dumps(form_venue['seeking_talent'].data),
  venue.seeking_description = form_venue['seeking_description'].data

  db.session.add(venue)
  db.session.commit()
  flash('Artist ' + form_venue['name'].data + ' edit successfully!')
  return redirect(url_for('show_venue', venue_id=venue_id))
#==============================================================



#==============================================================
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  result_artists = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term', '') + '%'))
  artists = []

  for artist in result_artists.all():
    venue_upcoming_ids = []
    upcoming_show_ids = Shows.query.filter(db.and_(Shows.start_time >= date.today().strftime("%Y-%m-%d"), Shows.artist_id == artist.id))
    for show in upcoming_show_ids.all():
      venue_upcoming_ids.append(show.venue_id)
    upcoming_shows = Venue.query.filter(db.and_(Venue.id.in_(venue_upcoming_ids)))
    artists.append(Search(artist.id, artist.name, upcoming_shows.count()))

  response = {
    "count": result_artists.count(),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_data = Artist.query.filter_by(id=artist_id).first()

  venue_upcoming_ids = []
  upcoming_show_ids = Shows.query.filter(db.and_(Shows.start_time >= date.today().strftime("%Y-%m-%d"), Shows.artist_id == artist_id))
  for show in upcoming_show_ids.all():
    venue_upcoming_ids.append(show.venue_id)
  upcoming_shows = Venue.query.filter(db.and_(Venue.id.in_(venue_upcoming_ids)))

  venue_past_ids = []
  past_show_ids = Shows.query.filter(db.and_(Shows.start_time < date.today().strftime("%Y-%m-%d"), Shows.artist_id == artist_id))
  for show in past_show_ids.all():
    venue_past_ids.append(show.venue_id)
  past_shows = Venue.query.filter(db.and_(Venue.id.in_(venue_past_ids)))

  artist = {
    "id": artist_id,
    "name": artist_data.name,
    "genres": json.loads(artist_data.genres),
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website_link,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": json.loads(artist_data.seeking_venue.lower()),
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link,
    "past_shows": past_shows.all(),
    "past_shows_count": past_shows.count(),
    "upcoming_shows": upcoming_shows.all(),
    "upcoming_shows_count": upcoming_shows.count(),
  }
  data = list(filter(lambda d: d['id'] == artist_id, [artist]))[0]
  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_data = Artist.query.filter_by(id=artist_id).first()
  
  form = ArtistForm()
  form['name'].data = artist_data.name
  form['city'].data = artist_data.city
  form['state'].data = artist_data.state
  form['phone'].data = artist_data.phone
  form['genres'].data = json.loads(artist_data.genres)
  form['image_link'].data = artist_data.image_link
  form['website_link'].data = artist_data.website_link
  form['facebook_link'].data = artist_data.facebook_link
  form['seeking_venue'].data = json.loads(artist_data.seeking_venue.lower()),
  form['seeking_description'].data = artist_data.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form_artist = ArtistForm()
  
  artist.name = form_artist['name'].data,
  artist.city = form_artist['city'].data,
  artist.state = form_artist['state'].data,
  artist.phone = form_artist['phone'].data,
  artist.genres = json.dumps(form_artist['genres'].data),
  artist.image_link = form_artist['image_link'].data,
  artist.website_link = form_artist['website_link'].data,
  artist.facebook_link = form_artist['facebook_link'].data,
  artist.seeking_venue = json.dumps(form_artist['seeking_venue'].data),
  artist.seeking_description = form_artist['seeking_description'].data

  db.session.add(artist)
  db.session.commit()
  flash('Artist ' + form_artist['name'].data + ' edit successfully!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try: 
    form_artist = ArtistForm()

    artist = Artist(
      name=form_artist['name'].data,
      city=form_artist['city'].data,
      state=form_artist['state'].data,
      phone=form_artist['phone'].data,
      genres=json.dumps(form_artist['genres'].data),
      image_link=form_artist['image_link'].data,
      website_link=form_artist['website_link'].data,
      facebook_link=form_artist['facebook_link'].data,
      seeking_venue=form_artist['seeking_venue'].data,
      seeking_description=form_artist['seeking_description'].data
    )

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + form_artist['name'].data + ' successfully listed!')
    return render_template('pages/home.html')
  except Exception as e:
      db.session.rollback()
      print(sys.exc_info())
      print(e)
  finally:
      db.session.close()
#==============================================================



#==============================================================
@app.route('/shows')
def shows():
  data_all = []
  shows = Shows.query.all()
  for show in shows:
    venue_data = Venue.query.filter_by(id=show.venue_id).first()
    artist_data = Artist.query.filter_by(id=show.artist_id).first()
    data_all.append(ShowVenueArtist(
      show.id, 
      venue_data.id, 
      venue_data.name, 
      artist_data.id, 
      artist_data.name, 
      artist_data.image_link,
      show.start_time
    ))
  return render_template('pages/shows.html', shows=data_all)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try: 
    form = ShowForm()
    show = Shows(
      artist_id = form['artist_id'].data,
      venue_id = form['venue_id'].data,
      start_time = form['start_time'].data)
    
    check_show = Shows.query.filter(db.and_(Shows.artist_id == form['artist_id'].data, Shows.venue_id == form['venue_id'].data)).first()
    if check_show:
      flash(u'Show existed! Please try again', 'error')
      return render_template('forms/new_show.html', form=form)
    else:
      db.session.add(show)
      db.session.commit()
      flash('Show successfully listed!')
      return render_template('pages/home.html')
  except Exception as e:
      db.session.rollback()
      print(e)
  finally:
      db.session.close()
#==============================================================



#==============================================================
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
#==============================================================


#==============================================================
if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

if __name__ == '__main__':
    app.run()
#==============================================================