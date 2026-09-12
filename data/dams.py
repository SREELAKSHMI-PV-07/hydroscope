# data/dams.py

DAM_DATABASE = {
    "Idukki Dam": {
        "district": "Idukki",
        "lat": 9.8494,
        "lon": 76.9726,

        # Prototype values — replace with official/live feed
        "water_level": 88.0,
        "inflow": 1800.0,
        "outflow": 600.0,
        "rainfall": 72.0,

        "total_shutters": 8,
        "open_shutters": 2,
        "opening_percent": 20,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / KSEB reference"
    },

    "Idamalayar Dam": {
        "district": "Ernakulam",
        "lat": 10.2068,
        "lon": 76.7032,

        "water_level": 72.0,
        "inflow": 920.0,
        "outflow": 310.0,
        "rainfall": 48.0,

        "total_shutters": 4,
        "open_shutters": 1,
        "opening_percent": 15,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / KSEB reference"
    },

    "Malankara Dam": {
        "district": "Idukki",
        "lat": 9.7804,
        "lon": 76.8787,

        "water_level": 67.0,
        "inflow": 210.0,
        "outflow": 95.0,
        "rainfall": 41.0,

        "total_shutters": 6,
        "open_shutters": 1,
        "opening_percent": 10,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / Irrigation reference"
    },

    "Bhoothathankettu": {
        "district": "Ernakulam",
        "lat": 10.1457,
        "lon": 76.6788,

        "water_level": 61.0,
        "inflow": 160.0,
        "outflow": 80.0,
        "rainfall": 36.0,

        "total_shutters": 5,
        "open_shutters": 1,
        "opening_percent": 10,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / Irrigation reference"
    },

    "Pamba Dam": {
        "district": "Pathanamthitta",
        "lat": 9.3805,
        "lon": 76.9275,

        "water_level": 64.0,
        "inflow": 450.0,
        "outflow": 170.0,
        "rainfall": 39.0,

        "total_shutters": 6,
        "open_shutters": 1,
        "opening_percent": 12,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / KSEB reference"
    },

    "Kakki Dam": {
        "district": "Pathanamthitta",
        "lat": 9.3500,
        "lon": 77.0000,

        "water_level": 70.0,
        "inflow": 520.0,
        "outflow": 190.0,
        "rainfall": 44.0,

        "total_shutters": 4,
        "open_shutters": 1,
        "opening_percent": 15,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / KSEB reference"
    },

    "Neyyar Dam": {
        "district": "Thiruvananthapuram",
        "lat": 8.5350,
        "lon": 77.1450,

        "water_level": 58.0,
        "inflow": 190.0,
        "outflow": 75.0,
        "rainfall": 31.0,

        "total_shutters": 4,
        "open_shutters": 0,
        "opening_percent": 0,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / Irrigation reference"
    },

    "Banasura Sagar Dam": {
        "district": "Wayanad",
        "lat": 11.7000,
        "lon": 75.9500,

        "water_level": 63.0,
        "inflow": 330.0,
        "outflow": 120.0,
        "rainfall": 52.0,

        "total_shutters": 4,
        "open_shutters": 1,
        "opening_percent": 10,

        "data_status": "PROTOTYPE",
        "source": "KSDMA / Irrigation reference"
    }
}


def get_dam(name):
    return DAM_DATABASE.get(name)


def get_all_dams():
    return DAM_DATABASE


def get_dam_names():
    return list(DAM_DATABASE.keys())
