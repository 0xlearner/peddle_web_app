from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectField

from .models import MakeYear


class CarForm(FlaskForm):
    make_year = QuerySelectField(
        "MakeYear",
        query_factory=lambda: MakeYear.query.all(),
        allow_blank=True,
        get_label="year",
    )
    car = QuerySelectField("Car", get_label="make", allow_blank=True)
    car_model = QuerySelectField("CarModel", get_label="model", allow_blank=True)
