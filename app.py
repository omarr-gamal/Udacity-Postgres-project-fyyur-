#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (Flask, render_template, request,
                   Response, flash, redirect, url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_migrate import Migrate
from logging import Formatter, FileHandler, log
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    lists = db.session.query(
        Venue_list.id, Venue_list.city, Venue_list.state).all()
    for i in lists:
        data.append({"city": i[1],
                     "state": i[2],
                     "venues": []})
    for i in range(0, len(lists)):
        c = db.session.query(Venue.id, Venue.name).filter(
            Venue.venue_list_id == lists[i][0]).all()
        for j in c:
            data[i]["venues"].append(
                {"id": j[0],
                 "name": j[1],
                 "num_upcoming_shows": db.session.query(Show).filter(Show.venue == j[0], Show.date > datetime.today()).count()
                 })

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form['search_term'].lower()
    venues = Venue.query.filter(
        Venue.name.ilike('%' + search_term + '%')).all()

    response = {
        "count": len(venues),
        "data": []
    }

    for i in venues:
        response['data'].append({"id": i.id,
                                 "name": i.name,
                                 "num_upcoming_shows": db.session.query(Show).filter(Show.venue == i.id, Show.date > datetime.today()).count()})

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    v = Venue.query.get(venue_id)

    genre_ids = db.session.query(Genre_Venue.genre_id).filter(
        Genre_Venue.venue_id == v.id).all()
    genres = []
    for i in genre_ids:
        genre_name = Genre.query.get(i[0]).name
        genres.append(genre_name)

    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue == venue_id,
        Show.artist == Artist.id,
        Show.date < datetime.now()
    ).all()

    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue == venue_id,
        Show.artist == Artist.id,
        Show.date > datetime.now()
    ).all()

    data = {
        "id": v.id,
        "name": v.name,
        "genres": genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link,
        "past_shows": [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.date.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        "upcoming_shows": [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.date.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    form = VenueForm(request.form, csrf_enabled=True)

    if form.validate():
        try:
            venue_list = Venue_list(
                city=form.city.data,
                state=form.state.data
            )

            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                venue_list_id=venue_list.id,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data
            )

            venue_list_query = db.session.query(Venue_list.id).filter(Venue_list.city == venue_list.city,
                                                                      Venue_list.state == venue_list.state).all()
            if len(venue_list_query) == 0:
                db.session.add(venue_list)
                db.session.commit()
                venue.venue_list_id = venue_list.id
            else:
                venue.venue_list_id = venue_list_query[0][0]

            db.session.add(venue)

            for genre_name in form.genres.data:
                genre = Genre.query.filter(
                    Genre.name.ilike('%' + genre_name + '%')).first()
                if not genre:
                    genre = Genre(name=genre_name)
                    db.session.add(genre)
                gen_venue = Genre_Venue(venue_id=venue.id, genre_id=genre.id)
                db.session.add(gen_venue)

                # Commit all things
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')

        except ValueError as e:
            print(e)
            db.session.rollback()
            flash('An error occurred. Venue ' +
                  form.name.data + ' could not be listed.')
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    # TODO: modify data to be the data object returned from db insertion

    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        db.session.query(Venue).filter(Venue.id == venue_id).delete()
        db.commit()
        flash('Venue was deleted successfully!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted.')
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = list(Artist.query.all())
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }]
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.

    search_term = request.form['search_term'].lower()
    artists = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()

    response = {
        "count": len(artists),
        "data": []
    }

    for i in artists:
        response['data'].append({"id": i.id,
                                 "name": i.name,
                                 "num_upcoming_shows": 1})

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    d = Artist.query.get(artist_id)
    genre_ids = db.session.query(Genre_Artist.genre_id).filter(
        Genre_Artist.artist_id == d.id).all()
    genres = []
    for i in genre_ids:
        genre_name = Genre.query.get(i[0]).name
        genres.append(genre_name)

    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(
        Show.venue == Venue.id,
        Show.artist == artist_id,
        Show.date < datetime.now()
    ).all()

    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).filter(
        Show.venue == Venue.id,
        Show.artist == artist_id,
        Show.date > datetime.now()
    ).all()

    data = {
        "id": d.id,
        "name": d.name,
        "genres": genres,
        "city": d.city,
        "state": d.state,
        "phone": d.phone,
        "website": d.website,
        "facebook_link": d.facebook_link,
        "seeking_venue": d.seeking_venues,
        "seeking_description": d.seeking_description,
        "image_link": d.image_link,
        "past_shows": [{
            'venue_id': venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.date.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
        "upcoming_shows": [{
            'venue_id': venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.date.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    a = Artist.query.get(artist_id)

    genre_ids = db.session.query(Genre_Artist.genre_id).filter(
        Genre_Artist.artist_id == a.id).all()
    genres = []
    for i in genre_ids:
        genre_name = Genre.query.get(i[0]).name
        genres.append(genre_name)

    artist = {
        "id": artist_id,
        "name": a.name,
        "genres": genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venues,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link
    }
    form = ArtistForm(obj=artist)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    a = Artist.query.get(artist_id)

    a.name = request.form['name']
    a.city = request.form['city']
    a.state = request.form['state']
    a.phone = request.form['phone']
    genres = request.form.getlist('genres')
    a.image_link = request.form['image_link']
    a.facebook_link = request.form['facebook_link']
    a.website = request.form['website']
    a.seeking_description = request.form['seeking_description']

    if 'seeking_venues' in request.form:
        a.seeking_venues = True
    else:
        a.seeking_venues = False

    db.session.add(a)
    db.session.commit()

    db.session.query(Genre_Artist).filter(
        Genre_Artist.artist_id == artist_id).delete()
    db.session.commit()

    genre_id = 1
    for g in genres:
        genre_id = db.session.query(
            Genre.id).filter(Genre.name == g)[0][0]
        db.session.add(Genre_Artist(artist_id=artist_id, genre_id=genre_id))
        db.session.commit()

    db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    v = Venue.query.get(venue_id)

    genre_ids = db.session.query(Genre_Venue.genre_id).filter(
        Genre_Venue.venue_id == v.id).all()
    genres = []

    for i in genre_ids:
        genre_name = Genre.query.get(i[0]).name
        genres.append(genre_name)

    venue = {
        "id": venue_id,
        "name": v.name,
        "genres": genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link
    }
    form = VenueForm(obj=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    v = Venue.query.get(venue_id)

    v.name = request.form['name']
    v.city = request.form['city']
    v.state = request.form['state']
    v.address = request.form['address']
    v.phone = request.form['phone']
    genres = request.form.getlist('genres')
    old_venue_list_id = v.venue_list_id
    v.image_link = request.form['image_link']
    v.facebook_link = request.form['facebook_link']
    v.website = request.form['website']
    v.seeking_description = request.form['seeking_description']

    if 'seeking_talent' in request.form:
        v.seeking_talent = True
    else:
        v.seeking_talent = False

    db.session.add(v)
    db.session.commit()

    # updating the venue's relationship with the genres
    db.session.query(Genre_Venue).filter(
        Genre_Venue.venue_id == venue_id).delete()
    db.session.commit()

    genre_id = 1
    for g in genres:
        genre_id = db.session.query(
            Genre.id).filter(Genre.name == g)[0][0]
        db.session.add(Genre_Venue(venue_id=venue_id, genre_id=genre_id))
        db.session.commit()

    db.session.refresh(v)

    if len(db.session.query(Venue_list.city).filter(Venue_list.city == v.city, Venue_list.state == v.state).all()) == 0:
        vl = Venue_list(city=v.city, state=v.state)
        db.session.add(vl)
        db.session.commit()

    q = db.session.query(Venue_list.id).filter(
        Venue_list.city == v.city, Venue_list.state == v.state).all()

    v.venue_list_id = q[0][0]
    db.session.add(v)
    db.session.commit()
    db.session.close()

    try:
        db.session.query(Venue_list).filter(
            Venue_list.id == old_venue_list_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form, csrf_enabled=True)
    if form.validate():
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website=form.website.data,
                seeking_venues=form.seeking_venues.data,
                seeking_description=form.seeking_description.data
            )

            db.session.add(artist)
            db.session.commit()

            genre_id = 1
            for g in form.genres.data:
                genre_id = db.session.query(
                    Genre.id).filter(Genre.name == g)[0][0]
                db.session.add(Genre_Artist(
                    artist_id=artist.id, genre_id=genre_id))

            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')

        except ValueError as e:
            print(e)
            db.session.rollback()
            flash('An error occurred. Artist ' +
                  form.name.data + ' could not be listed.')
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = []

    f = db.session.query(Show.venue, Show.artist, Show.date).all()
    for i in f:
        data.append({"venue_id": i[0],
                     "venue_name": Venue.query.get(i[0]).name,
                     "artist_id": i[1],
                     "artist_name": Artist.query.get(i[1]).name,
                     "artist_image_link": Artist.query.get(i[1]).image_link,
                     "start_time": str(i[2])})
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form, csrf_enabled=True)
    if form.validate():
        try:
            show = Show(
                artist=form.artist_id.data,
                venue=form.venue_id.data,
                date=form.start_time.data,
            )
            db.session.add(show)
            db.session.commit()

            flash('Show successfully listed!')

        except ValueError as e:
            print(e)
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')

        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
