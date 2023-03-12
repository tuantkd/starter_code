from distutils.util import strtobool
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
from models import *

#==============================================================
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
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

  for result_venue in result_venues.all():
    upcoming_shows = []
    for show in result_venue.shows:
      temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_time >= datetime.now():
        upcoming_shows.append(temp_show)
    venues.append(Search(result_venue.id, result_venue.name, len(upcoming_shows)))
      
  response = {
    "count": result_venues.count(),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)

  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
    temp_show = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(venue)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        address = form.address.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(venue)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()
      
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  db.session.delete(venue)
  return None

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_data = Venue.query.get_or_404(venue_id)
  form = VenueForm()
  form.name.data = venue_data.name
  form.city.data = venue_data.city
  form.state.data = venue_data.state
  form.address.data = venue_data.address
  form.phone.data = venue_data.phone
  form.genres.data = venue_data.genres
  form.image_link.data = venue_data.image_link
  form.website_link.data = venue_data.website_link
  form.facebook_link.data = venue_data.facebook_link
  form.seeking_talent.data = venue_data.seeking_talent,
  form.seeking_description.data = venue_data.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.image_link = form.image_link.data
      venue.website_link = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.add(venue)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()
      
    flash('Venue ' + request.form['name'] + ' edit successfully!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/edit_venue.html', form=form)
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
  for result_artist in result_artists.all():
    upcoming_shows = []
    for show in result_artist.shows:
      temp_show = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
      }
      if show.start_time >= datetime.now():
        upcoming_shows.append(temp_show)
    artists.append(Search(result_artist.id, result_artist.name, len(upcoming_shows)))
  response = {
    "count": result_artists.count(),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)

  past_shows = []
  upcoming_shows = []
  for show in artist.shows:
    temp_show = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
      past_shows.append(temp_show)
    else:
      upcoming_shows.append(temp_show)

  data = vars(artist)
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_data = Artist.query.get_or_404(artist_id)
  form = ArtistForm()
  form.name.data = artist_data.name
  form.city.data = artist_data.city
  form.state.data = artist_data.state
  form.phone.data = artist_data.phone
  form.genres.data = artist_data.genres
  form.image_link.data = artist_data.image_link
  form.website_link.data = artist_data.website_link
  form.facebook_link.data = artist_data.facebook_link
  form.seeking_venue.data = artist_data.seeking_venue,
  form.seeking_description.data = artist_data.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.image_link = form.image_link.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.add(artist)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()
      print(sys.exc_info())
      
    flash('Artist ' + request.form['name'] + ' edit successfully!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ArtistForm()
    return render_template('forms/edit_artist.html', form=form)

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=form.genres.data,
        image_link=form.image_link.data,
        website_link=form.website_link.data,
        facebook_link=form.facebook_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()
    finally:
      db.session.close()
      
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)
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
  form = ShowForm(request.form, meta={"csrf": False})
  if form.validate():
    try: 
      show = Shows(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      
      check_show = Shows.query.filter(db.and_(
        Shows.artist_id == form['artist_id'].data, 
        Shows.venue_id == form['venue_id'].data)
      ).first()

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
  
  else:

    message = []
    for field, errors in form.errors.items():
      for error in errors:
        message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
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