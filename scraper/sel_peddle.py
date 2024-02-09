import json
import time
import os

import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selectolax.parser import HTMLParser


from peddle_app.extensions import db
from peddle_app.models import MakeYear, Car, CarModel


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://sell.peddle.com/",
    "Origin": "https://sell.peddle.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-GPC": "1",
}


def get_access_token():
    driver = uc.Chrome(headless=True, use_subprocess=False)
    print("----------- Launching Browser ------------")
    driver.get(
        "https://auth.peddle.com/identity-provider/login?ReturnUrl=%2Fidentity-provider%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3D82a5ac47-6cc9-4f63-98ba-8b7ceb77566e%26scope%3Dopenid%2520profile%2520email%2520uni%253Alocations%253Aread%2520uni%253Avehicles%253Aread%2520sel%253Amiscellaneous%253Aread%2520sel%253Ainstant-offers%253Awrite%2520sel%253Ainstant-offers%253Aread%2520sel%253Aoffers%253Aread%2520sel%253Aoffers%253Awrite%2520sel%253Aoffers%253Aadjust%2520sel%253Aaccounts%253Aread%2520sel%253Aaccounts%253Awrite%2520car%253Acompanies%253Aread%2520car%253Ascheduling-windows%253Aread%2520car%253Aoperation-hours%253Aread%2520buy%253Acompanies%253Aread%2520buy%253Aoperation-hours%253Aread%2520auc%253Afacilities%253Aread%2520auc%253Aoperation-hours%253Aread%2520offline_access%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fsell.peddle.com%252Fapi%252Fauth%252Fcallback%252Fidentity-server%26code_challenge%3D2NwC1VqViOqHsBMx4lD54V30lq4z_KDvnSFP5xHmPqo%26code_challenge_method%3DS256"
    )
    print("----------- Logggin in ------------")
    driver.find_element(By.NAME, "email-input").send_keys(os.getenv("PEDDLE_USER"))
    driver.find_element(By.NAME, "password-input").send_keys(
        os.getenv("PEDDLE_PASSWORD")
    )
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print("----------- Login Successfull ------------")

    time.sleep(30)
    html = HTMLParser(driver.page_source)
    json_str = html.css_first('script[id="__NEXT_DATA__"]').text()
    json_data = json.loads(json_str)
    bearer_token = json_data["props"]["pageProps"]["token"]["access_token"]

    headers.update({"Authorization": "Bearer {}".format(bearer_token)})
    driver.close()


def collect_parameters():
    years_endpoint = requests.get(
        "https://service.peddle.com/universal/v1/years", headers=headers
    )

    for years in years_endpoint.json():
        make_year = MakeYear(year_id=years["id"], year=years["name"])
        db.session.add(make_year)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        params = {
            "year": years["name"],
        }
        print(params)
        make_endpoint = requests.get(
            "https://service.peddle.com/universal/v2/makes",
            params=params,
            headers=headers,
        )
        for make in make_endpoint.json():
            car_make = Car(
                make_id=make["id"],
                make=make["name"],
                make_year_id=make_year.id,
            )
            db.session.add(car_make)

            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise
            model_params = {
                "year": years["name"],
                "make": make["name"],
            }
            model_endpoint = requests.get(
                "https://service.peddle.com/universal/v1/models",
                params=model_params,
                headers=headers,
            )
            for m in model_endpoint.json():
                door_count = m["door_count"]
                body_type_id = None
                cab_type_id = None
                if "body_type" in m:
                    body_type_id = m["body_type"]["id"]
                if "cab_type" in m:
                    cab_type_id = m["cab_type"]["id"]
                car_model = CarModel(
                    model_id=m["id"],
                    model=m["name"],
                    body_type_id=body_type_id,
                    cab_type_id=cab_type_id,
                    door_count=door_count,
                    car_id=car_make.id,
                )

                db.session.add(car_model)

                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise

    db.session.close()


def get_calculated_price(
    year_id, make_id, model_id, body_type_id, cab_type_id, door_count
):
    json_data = {
        "vehicle": {
            "year_id": year_id,
            "make_id": make_id,
            "model_id": model_id,
            "body_type_id": body_type_id,
            "cab_type_id": cab_type_id,
            "door_count": door_count,
            "trim_id": "",
            "body_style_id": "",
            "fuel_type_id": "",
            "usage": "unknown",
            "location": {
                "zip_code": "10001",
            },
            "ownership": {
                "type": "owned",
                "title_type": "clean",
            },
            "condition": {
                "mileage": 6000,
                "drivetrain_condition": "drives",
                "key_and_keyfob_available": "yes",
                "all_tires_inflated": "yes",
                "flat_tires_location": {
                    "driver_side_view": {
                        "front": False,
                        "rear": False,
                    },
                    "passenger_side_view": {
                        "front": False,
                        "rear": False,
                    },
                },
                "wheels_removed": "no",
                "wheels_removed_location": {
                    "driver_side_view": {
                        "front": False,
                        "rear": False,
                    },
                    "passenger_side_view": {
                        "front": False,
                        "rear": False,
                    },
                },
                "body_panels_intact": "yes",
                "body_panels_damage_location": {
                    "driver_side_view": {
                        "front_top": False,
                        "front_bottom": False,
                        "front_door_top": False,
                        "front_door_bottom": False,
                        "rear_door_top": False,
                        "rear_door_bottom": False,
                        "rear_top": False,
                        "rear_bottom": False,
                    },
                    "passenger_side_view": {
                        "front_top": False,
                        "front_bottom": False,
                        "front_door_top": False,
                        "front_door_bottom": False,
                        "rear_door_top": False,
                        "rear_door_bottom": False,
                        "rear_top": False,
                        "rear_bottom": False,
                    },
                    "front_view": {
                        "driver_side_top": False,
                        "driver_side_bottom": False,
                        "passenger_side_top": False,
                        "passenger_side_bottom": False,
                    },
                    "rear_view": {
                        "driver_side_top": False,
                        "driver_side_bottom": False,
                        "passenger_side_top": False,
                        "passenger_side_bottom": False,
                    },
                    "top_view": {
                        "driver_side_front": False,
                        "passenger_side_front": False,
                        "driver_side_front_roof": False,
                        "passenger_side_front_roof": False,
                        "driver_side_rear_roof": False,
                        "passenger_side_rear_roof": False,
                        "driver_side_rear": False,
                        "passenger_side_rear": False,
                    },
                },
                "body_damage_free": "yes",
                "body_damage_location": {
                    "driver_side_view": {
                        "front_top": False,
                        "front_bottom": False,
                        "front_door_top": False,
                        "front_door_bottom": False,
                        "rear_door_top": False,
                        "rear_door_bottom": False,
                        "rear_top": False,
                        "rear_bottom": False,
                    },
                    "passenger_side_view": {
                        "front_top": False,
                        "front_bottom": False,
                        "front_door_top": False,
                        "front_door_bottom": False,
                        "rear_door_top": False,
                        "rear_door_bottom": False,
                        "rear_top": False,
                        "rear_bottom": False,
                    },
                    "front_view": {
                        "driver_side_top": False,
                        "driver_side_bottom": False,
                        "passenger_side_top": False,
                        "passenger_side_bottom": False,
                    },
                    "rear_view": {
                        "driver_side_top": False,
                        "driver_side_bottom": False,
                        "passenger_side_top": False,
                        "passenger_side_bottom": False,
                    },
                    "top_view": {
                        "driver_side_front": False,
                        "passenger_side_front": False,
                        "driver_side_front_roof": False,
                        "passenger_side_front_roof": False,
                        "driver_side_rear_roof": False,
                        "passenger_side_rear_roof": False,
                        "driver_side_rear": False,
                        "passenger_side_rear": False,
                    },
                },
                "mirrors_lights_glass_intact": "yes",
                "mirrors_lights_glass_damage_location": {
                    "driver_side_view": {
                        "front_top": False,
                        "front_bottom": False,
                        "front_door_top": False,
                        "front_door_bottom": False,
                        "rear_door_top": False,
                        "rear_door_bottom": False,
                        "rear_top": False,
                        "rear_bottom": False,
                    },
                    "passenger_side_view": {
                        "front_top": False,
                        "front_bottom": False,
                        "front_door_top": False,
                        "front_door_bottom": False,
                        "rear_door_top": False,
                        "rear_door_bottom": False,
                        "rear_top": False,
                        "rear_bottom": False,
                    },
                    "front_view": {
                        "driver_side_top": False,
                        "driver_side_bottom": False,
                        "passenger_side_top": False,
                        "passenger_side_bottom": False,
                    },
                    "rear_view": {
                        "driver_side_top": False,
                        "driver_side_bottom": False,
                        "passenger_side_top": False,
                        "passenger_side_bottom": False,
                    },
                    "top_view": {
                        "driver_side_front": False,
                        "passenger_side_front": False,
                        "driver_side_front_roof": False,
                        "passenger_side_front_roof": False,
                        "driver_side_rear_roof": False,
                        "passenger_side_rear_roof": False,
                        "driver_side_rear": False,
                        "passenger_side_rear": False,
                    },
                },
                "interior_intact": "yes",
                "flood_fire_damage_free": "yes",
                "engine_transmission_condition": "intact",
                "catalytic_converter_intact": "yes",
            },
        },
        "publisher": {},
    }

    get_access_token()
    response = requests.post(
        "https://service.peddle.com/seller/v4/instant-offers",
        headers=headers,
        json=json_data,
    )

    return response.json()["presented_offer_amount"]


def run():
    collect_parameters()


if __name__ == "__main__":
    get_access_token()
    run()
