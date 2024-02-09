from .extensions import db


class MakeYear(db.Model):
    __tablename__ = "make_year"
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column("year_id", db.Integer)
    year = db.Column("year", db.Integer)
    car_make_year = db.relationship("Car", backref="car_make_year")


class Car(db.Model):
    __tablename__ = "car"
    id = db.Column(db.Integer, primary_key=True)
    make_id = db.Column("make_id", db.Integer)
    make = db.Column("make", db.String)
    make_year_id = db.Column(db.Integer, db.ForeignKey("make_year.id"))


class CarModel(db.Model):
    __tablename__ = "car_model"
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column("model_id", db.Integer)
    model = db.Column("model", db.String)
    body_type_id = db.Column("body_type_id", db.Integer)
    cab_type_id = db.Column("cab_type_id", db.Integer)
    door_count = db.Column("door_count", db.Integer)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"))
    car_make = db.relationship("Car", backref="car_make")
