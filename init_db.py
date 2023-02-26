from datetime import date

from sqlalchemy import String
from app import Shows, Venue, db
from flask import jsonify


db.drop_all()
db.create_all()

venues = [
    Venue(
        name='The Musical Hop 01',
        city='San Francisco',
        state='CA',
        phone='123-123-1234',
        address='1015 Folsom Street',
        genres= "Classical",
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop',
        website_link = 'https://www.themusicalhop.com',
        seeking_talent='y',
        seeking_description='Seeking description',
        num_upcoming_shows = 0
    ),
    Venue(
        name='The Musical Hop 02',
        city='San Francisco',
        state='CA',
        phone='123-123-1234',
        address='1015 Folsom Street',
        genres= "Classical",
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop',
        website_link = 'https://www.themusicalhop.com',
        seeking_talent='y',
        seeking_description='Seeking description',
        num_upcoming_shows = 0
    ),
    Venue(
        name='The Musical Hop 03',
        city='San Francisco',
        state='CA',
        phone='123-123-1234',
        address='1015 Folsom Street',
        genres= "Classical",
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop',
        website_link = 'https://www.themusicalhop.com',
        seeking_talent='y',
        seeking_description='Seeking description',
        num_upcoming_shows = 0
    ),
    Venue(
        name='The Musical Hop 04',
        city='San Francisco',
        state='CA',
        phone='123-123-1234',
        address='1015 Folsom Street',
        genres= "Classical",
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop',
        website_link = 'https://www.themusicalhop.com',
        seeking_talent='y',
        seeking_description='Seeking description',
        num_upcoming_shows = 0
    ),
    Venue(
        name='The Musical Hop 05',
        city='San Francisco',
        state='CA',
        phone='123-123-1234',
        address='1015 Folsom Street',
        genres= "Classical",
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop',
        website_link = 'https://www.themusicalhop.com',
        seeking_talent='y',
        seeking_description='Seeking description',
        num_upcoming_shows = 0
    ),
]

db.session.add_all(venues)

db.session.commit()