from flask import Blueprint, render_template, request

from .forms import CarForm

from .models import Car, CarModel

from scraper.sel_peddle import get_calculated_price

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    form = CarForm()

    if form.make_year.data:
        form.car.query = Car.query.filter_by(make_year_id=form.make_year.data.id).all()
        form.car_model.query = CarModel.query.filter_by(car_id=form.car.data.id).all()
    else:
        form.car.query = Car.query.filter(None).all()
        form.car_model.query = CarModel.query.filter(None).all()

    if form.validate_on_submit():
        car_make_year_id = form.make_year.data.year_id
        car_make_id = form.car.data.make_id
        car_model_id = form.car_model.data.model_id
        body_type_id = form.car_model.data.body_type_id
        cab_type_id = form.car_model.data.cab_type_id
        door_count = form.car_model.data.door_count
        print(f"car_make_year_id: {car_make_year_id}")
        print(f"car_make_id: {car_make_id}")
        print(f"car_model_id: {car_model_id}")
        print(f"body_type_id: {body_type_id}")
        print(f"cab_type_id: {cab_type_id}")
        print(f"door_count: {door_count}")

        price = get_calculated_price(
            car_make_year_id,
            car_make_id,
            car_model_id,
            body_type_id,
            cab_type_id,
            door_count,
        )

        print(price)
        return f"Calculated Price: {price}"
    return render_template("index.html", form=form)


@main.route("/get_cars")
def get_cars():
    make_id = request.args.get("make_year", type=int)
    cars = Car.query.filter_by(make_year_id=make_id).all()
    return render_template("car_options.html", cars=cars)


@main.route("/get_car_models")
def get_models():
    car_id = request.args.get("car", type=int)
    models = CarModel.query.filter_by(car_id=car_id).all()
    return render_template("car_models.html", models=models)
