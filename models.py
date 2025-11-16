from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venue_list(db.Model):
    __tablename__ = 'Venue_list'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))

    venues = db.relationship('Venue', backref='list')


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    venue_list_id = db.Column(db.Integer, db.ForeignKey('Venue_list.id'))

    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='venues', cascade="all, delete")
    genres = db.relationship(
        'Genre_Venue', backref='mygenres', cascade="all, delete")


# intermediate table for the artist genre many-to-many relationship
class Genre_Artist(db.Model):
    __tablename__ = 'Genre_Artist'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('Genre.id'))


# intermediate table for the venue genre many-to-many relationship
class Genre_Venue(db.Model):
    __tablename__ = 'Genre_Venue'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('Genre.id'))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venues = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', cascade="all, delete")
    genres = db.relationship(
        'Genre_Artist', backref='mygenres', cascade="all, delete")

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)

    artist = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue = db.Column(db.Integer, db.ForeignKey('Venue.id'))
