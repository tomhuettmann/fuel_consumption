import json
import os
from datetime import datetime, timedelta
from shutil import rmtree, copytree

from jinja2 import Template

script_dir = os.path.dirname(os.path.abspath(__file__))

template_dir = f"{script_dir}/templates"
data_dir = f"{script_dir}/../data"
out_dir = f"{script_dir}/../out"


def create_empty_output_folder():
    if os.path.exists(out_dir):
        rmtree(out_dir)
    os.makedirs(out_dir)


def copy_static_files():
    from_directory = f"{script_dir}/static"
    to_directory = f"{out_dir}/static"
    copytree(from_directory, to_directory)


def generate_index():
    with open(f"{template_dir}/index.html") as index_file:
        index_template = Template(index_file.read())
        file = open(f"{out_dir}/index.html", "w")
        chart_data = get_chart_data(car_ids)
        file.write(
            index_template.render(
                car_ids=sorted(car_ids),
                labels=list(map(lambda e: e.strftime("%d.%m.%Y"), chart_data.keys())),
                data=list(chart_data.values()),
            )
        )


def get_chart_data(cars):
    data = []
    for car_id in cars:
        data.append(get_chronological_fuel_consumptions_from(car_id))
    all_car_data = {}
    for car_data in data:
        all_car_data.update(
            dict(
                map(
                    lambda cd: (
                        datetime.strptime(cd.get("date"), "%d.%m.%Y"),
                        cd.get("price"),
                    ),
                    car_data,
                )
            )
        )
    return dict(sorted(all_car_data.items()))


def generate_car(car_id):
    car_properties = get_car_properties_from(car_id)
    fuel_consumptions = add_total_price_to(
        add_average_consumption_to(get_chronological_fuel_consumptions_from(car_id))
    )
    total_amount = sum(map(lambda x: x["amount"], fuel_consumptions))
    total_distance = sum(map(lambda x: x["distance"], fuel_consumptions))
    total_average_consumption = round(100 * total_amount / total_distance, 2)
    fuel_consumptions_last_year, last_year_days = (
        get_all_fuel_consumptions_and_days_within_last(365, fuel_consumptions)
    )
    distance_per_year = (
        365
        * sum(map(lambda x: x["distance"], list(fuel_consumptions_last_year)[:-1]))
        / last_year_days
    )
    fuel_consumptions_last_three_months, last_three_months_days = (
        get_all_fuel_consumptions_and_days_within_last(90, fuel_consumptions)
    )
    costs_per_month = (
        30
        * sum(
            map(
                lambda x: x["total_price"],
                list(fuel_consumptions_last_three_months)[:-1],
            )
        )
        / last_three_months_days
    )

    with open(f"{template_dir}/car.html") as car_file:
        car_template = Template(car_file.read())
        file = open(f"{out_dir}/{car_id}.html", "w")
        file.write(
            car_template.render(
                car_name=car_properties["name"],
                fuel_consumptions=get_two_digits_formatted_fuel_consumptions(
                    fuel_consumptions
                ),
                total_average_consumption=total_average_consumption,
                distance_per_year=get_rounded_thousand_dots_string_from(
                    distance_per_year
                ),
                overall_distance=get_rounded_thousand_dots_string_from(
                    total_distance + car_properties["base_distance"]
                ),
                costs_per_month=round(costs_per_month, 2),
                car_ids=sorted(car_ids),
                current_car_id=car_id,
            )
        )


def get_chronological_fuel_consumptions_from(car_id):
    with open(f"{data_dir}/{car_id}/fuel_consumptions.json") as file:
        fuel_consumptions = json.load(file)
        return sorted(
            fuel_consumptions,
            key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"),
            reverse=True,
        )


def get_car_properties_from(car_id):
    with open(f"{data_dir}/{car_id}/car_properties.json") as file:
        car_properties = json.load(file)
        return car_properties


def add_average_consumption_to(fuel_consumptions):
    for fuel_consumption in fuel_consumptions:
        fuel_consumption["average"] = round(
            100 * fuel_consumption["amount"] / fuel_consumption["distance"], 2
        )
    return fuel_consumptions


def add_total_price_to(fuel_consumptions):
    for fuel_consumption in fuel_consumptions:
        fuel_consumption["total_price"] = round(
            fuel_consumption["amount"] * (fuel_consumption["price"] + 0.009), 2
        )
    return fuel_consumptions


def get_all_fuel_consumptions_and_days_within_last(
    days, all_chronological_fuel_consumptions
):
    last_date = datetime.strptime(
        all_chronological_fuel_consumptions[0]["date"], "%d.%m.%Y"
    )
    earliest_date = last_date - timedelta(days=days)
    fuel_consumptions_within_days = list(
        filter(
            lambda x: datetime.strptime(x["date"], "%d.%m.%Y") > earliest_date,
            all_chronological_fuel_consumptions,
        )
    )
    return (
        fuel_consumptions_within_days,
        (
            last_date
            - datetime.strptime(fuel_consumptions_within_days[-1]["date"], "%d.%m.%Y")
        ).days,
    )


def get_rounded_thousand_dots_string_from(number):
    return f"{round(number):,}".replace(",", ".")


def get_two_digits_formatted_fuel_consumptions(fuel_consumptions):
    for fuel_consumption in fuel_consumptions:
        fuel_consumption["amount"] = "{:.2f}".format(fuel_consumption["amount"])
        fuel_consumption["average"] = "{:.2f}".format(fuel_consumption["average"])
        fuel_consumption["total_price"] = "{:.2f}".format(
            fuel_consumption["total_price"]
        )
    return fuel_consumptions


if __name__ == "__main__":
    print("Start generating the files for pages")

    create_empty_output_folder()
    copy_static_files()

    car_ids = os.listdir(data_dir)
    generate_index()
    for car in car_ids:
        generate_car(car)

    print("Finish generating the files")
