import json
import os
from datetime import datetime, timedelta
from shutil import rmtree

from jinja2 import Template

script_dir = os.path.dirname(os.path.abspath(__file__))

template_dir = f"{script_dir}/templates"
data_dir = f"{script_dir}/../data"
out_dir = f"{script_dir}/../out"
price_overview_endpoint_name = "price_overview.json"


def create_empty_output_folder():
    if os.path.exists(out_dir):
        rmtree(out_dir)
    os.makedirs(out_dir)


def generate_index_endpoint(endpoints):
    with open(f"{template_dir}/index.html") as index_file:
        index_template = Template(index_file.read())
        with open(f"{out_dir}/index.html", "w") as file:
            file.write(index_template.render(endpoints=endpoints))


def get_average_consumption(sorted_properties):
    total_distance = (
        sorted_properties[-1]["distance"] - sorted_properties[0]["distance"]
    )

    total_amount = sum(property["amount"] for property in sorted_properties)
    return round(100 * total_amount / total_distance, 2)


def get_properties_and_days_within_last(days, sorted_properties):
    last_date = datetime.strptime(sorted_properties[-1]["date"], "%d.%m.%Y")
    earliest_date = last_date - timedelta(days=days)
    properties_within_days = list(
        filter(
            lambda x: datetime.strptime(x["date"], "%d.%m.%Y") > earliest_date,
            sorted_properties,
        )
    )
    return (
        properties_within_days,
        (
            last_date - datetime.strptime(properties_within_days[0]["date"], "%d.%m.%Y")
        ).days,
    )


def get_distance_per_year(sorted_properties):
    properties, days = get_properties_and_days_within_last(365, sorted_properties)
    total_distance = properties[-1]["distance"] - properties[0]["distance"]
    return int(365 * total_distance / days)


def get_costs_per_month(sorted_properties):
    properties, days = get_properties_and_days_within_last(90, sorted_properties)
    total_price = sum(map(lambda e: e["price"] * e["amount"], properties[1:]))
    return round(30 * total_price / days, 2)


def get_costs_per_100(sorted_properties):
    total_distance = (
        sorted_properties[-1]["distance"] - sorted_properties[0]["distance"]
    )
    total_price = sum(map(lambda e: e["price"] * e["amount"], sorted_properties[1:]))
    return round(100 * total_price / total_distance, 2)


def generate_car_endpoint(endpoint_name):
    with open(f"{data_dir}/{endpoint_name}") as properties_file:
        properties = json.load(properties_file)
        sorted_properties = sorted(
            properties, key=lambda e: datetime.strptime(e["date"], "%d.%m.%Y")
        )

        properties = {
            "average_consumption": get_average_consumption(sorted_properties),
            "total_distance": sorted_properties[-1]["distance"],
            "first_total_distance": sorted_properties[0]["distance"],
            "distance_per_year": get_distance_per_year(sorted_properties),
            "previous_costs_per_month": get_costs_per_month(sorted_properties),
            "costs_per_100": get_costs_per_100(sorted_properties),
        }

        entries = []
        for previous, current in zip(sorted_properties, sorted_properties[1:]):
            entries.append(
                {
                    "date": current["date"],
                    "distance": current["distance"] - previous["distance"],
                    "total_distance": current["distance"],
                    "amount": current["amount"],
                    "consumption": round(
                        100
                        * current["amount"]
                        / (current["distance"] - previous["distance"]),
                        2,
                    ),
                    "price": current["price"],
                    "total_price": round(current["price"] * current["amount"], 2),
                    "costs_per_100": round(
                        100
                        * (current["price"] * current["amount"])
                        / (current["distance"] - previous["distance"]),
                        2,
                    ),
                }
            )

        data = {"properties": properties, "entries": entries}
        with open(f"{out_dir}/{endpoint_name}", "w") as file:
            file.write(json.dumps(data, indent=4))


def generate_price_overview_endpoint(car_endpoints):
    all_entries = []
    for car_endpoint in car_endpoints:
        with open(f"{data_dir}/{car_endpoint}") as properties_file:
            all_entries += json.load(properties_file)
    valid_date_and_prices = list(
        filter(
            lambda e: e["price"] > 0,
            map(lambda e: {"date": e["date"], "price": e["price"]}, all_entries),
        )
    )
    sorted_date_and_prices = sorted(
        valid_date_and_prices, key=lambda e: datetime.strptime(e["date"], "%d.%m.%Y")
    )
    with open(f"{out_dir}/{price_overview_endpoint_name}", "w") as file:
        file.write(json.dumps(sorted_date_and_prices, indent=4))


if __name__ == "__main__":
    print("Start generating the files for pages")

    create_empty_output_folder()

    car_endpoints = sorted([e.name for e in os.scandir(data_dir) if e.is_file()])
    generate_index_endpoint(car_endpoints + [price_overview_endpoint_name])
    for car_endpoint in car_endpoints:
        generate_car_endpoint(car_endpoint)
    generate_price_overview_endpoint(car_endpoints)

    print("Finish generating the files")
