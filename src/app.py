import json
import os
from datetime import datetime

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def base():
    # noinspection PyUnresolvedReferences
    return render_template(
        'base.html',
        car_ids=car_ids
    )


@app.route('/car/<car_id>')
def car(car_id):
    if car_id in car_ids:
        car_properties = get_car_properties_from(car_id)
        fuel_consumptions = add_total_price_to(
            add_average_consumption_to(get_chronological_fuel_consumptions_from(car_id)))
        total_amount = sum(map(lambda x: x['amount'], fuel_consumptions))
        total_distance = sum(map(lambda x: x['distance'], fuel_consumptions))
        total_average_consumption = round(100 * total_amount / total_distance, 2)
        # noinspection PyUnresolvedReferences
        return render_template(
            'car.html',
            car_name=car_properties["name"],
            fuel_consumptions=fuel_consumptions,
            total_average_consumption=total_average_consumption,
            overall_distance=f"{round(total_distance + car_properties['base_distance']):,}".replace(",", ".")
        )
    else:
        return "car not found"


def get_chronological_fuel_consumptions_from(car_id):
    file = open('data/' + car_id + '/fuel_consumptions.json')
    fuel_consumptions = json.load(file)
    file.close()
    return sorted(fuel_consumptions, key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)


def get_car_properties_from(car_id):
    file = open('data/' + car_id + '/car_properties.json')
    car_properties = json.load(file)
    file.close()
    return car_properties


def add_average_consumption_to(fuel_consumptions):
    for fuel_consumption in fuel_consumptions:
        fuel_consumption['average'] = round(100 * fuel_consumption['amount'] / fuel_consumption['distance'], 2)
    return fuel_consumptions


def add_total_price_to(fuel_consumptions):
    for fuel_consumption in fuel_consumptions:
        fuel_consumption['total_price'] = round(fuel_consumption['amount'] * (fuel_consumption['price'] + 0.009), 2)
    return fuel_consumptions


if __name__ == '__main__':
    car_ids = os.listdir("data")
    app.run(host='0.0.0.0', port=5000)
