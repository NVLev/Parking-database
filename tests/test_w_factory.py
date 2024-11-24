import os
import sys

from module_29_testing.hw.tests.factory_generation import ClientFactory, ParkingFactory

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.model import db, Base, Client, Parking, ClientParking, is_parking_open

def test_create_client(app_client, db) -> None:
    client = ClientFactory()
    db.session.commit()
    client_data = {
        "name": client.name,
        "surname": client.surname,
        "credit_card": client.credit_card,
        "car_number": client.car_number
    }

    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/clients/add_client", json=client_data, headers=headers)

    assert resp.status_code == 201

def test_create_parking(app_client, db) -> None:
    parking = ParkingFactory
    db.session.commit()
    parking_data = {"address": parking.address, "opened": parking.opened,
                 "count_places": parking.count_places, "count_available_places": parking.count_available_places,
                   "opening_time": parking.opening_time, "closing_time": parking.closing_time}
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/parking/add_parking", json=parking_data, headers=headers)
    assert resp.status_code == 201