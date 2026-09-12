# services/dam_data.py

from data.dams import get_dam


def get_dam_data(dam_name):

    dam = get_dam(dam_name)

    if dam is None:
        return None

    return {
        "name": dam_name,
        "district": dam["district"],

        "lat": dam["lat"],
        "lon": dam["lon"],

        "water_level": dam["water_level"],
        "inflow": dam["inflow"],
        "outflow": dam["outflow"],
        "rainfall": dam["rainfall"],

        "total_shutters": dam["total_shutters"],
        "open_shutters": dam["open_shutters"],
        "opening_percent": dam["opening_percent"],

        "data_status": dam["data_status"],
        "source": dam["source"]
    }


def calculate_water_balance(dam_data):

    if dam_data is None:
        return 0

    return dam_data["inflow"] - dam_data["outflow"]


def get_release_status(dam_data):

    if dam_data is None:
        return "UNKNOWN"

    opening = dam_data["opening_percent"]

    if opening == 0:
        return "CLOSED"

    if opening < 20:
        return "LOW RELEASE"

    if opening < 50:
        return "MODERATE RELEASE"

    return "HIGH RELEASE"
