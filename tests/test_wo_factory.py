import json
import os
import sys
from datetime import datetime

import pytest
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.model import Base, Client, Parking, ClientParking
from config import logger

@pytest.mark.parametrize("route", ["/clients/1",
                                   "/clients"])
def test_route_status(app_client, route):
    rv = app_client.get(route)
    assert rv.status_code == 200

def test_create_client(app_client) -> None:
    client_data = {"name": "Pirjo", "surname": "Myryläinen",
                 "credit_card": "1234567891", "car_number": "FC123KL"}
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/clients/add_client", json=client_data, headers=headers)

    assert resp.status_code == 201

def test_create_parking(app_client) -> None:
    parking_data = {"address": "123 Aleksanderkatu, Helsinki", "opened": True,
                 "count_places": 20, "count_available_places": 18,
                   "opening_time": "07:00", "closing_time": "21:00"}
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/parking/add_parking", json=parking_data, headers=headers)
    assert resp.status_code == 201


def test_check_in_parking(app_client, db) -> None:
    check_in_data = {"client_id": 1,
                     "parking_id": 1,
                     "time_in": "08:00"}
    parking= db.session.get(Parking, 1)
    before = parking.count_available_places
    headers = {"Content-Type": "application/json"}
    resp = app_client.post("/client_parkings", json=check_in_data, headers=headers)
    assert resp.status_code == 201
    after = parking.count_available_places
    assert before - after == 1
    assert parking.opened == True

def test_check_in_parking_full(app_client, db):
    client = Client(id=4, name="Lena", surname="Piranen", credit_card="1234-5678-9012-3456", car_number="FC123KL")
    parking = Parking(id=4, address="Test Address",
                      count_places=20, count_available_places=0,
                      opened=True, opening_time="07:00", closing_time="21:00")
    db.session.add(client)
    db.session.add(parking)
    db.session.commit()

    check_in_data = {
        "client_id": 3,
        "parking_id": 4
    }

    resp = app_client.post("/client_parkings", json=check_in_data)


    assert resp.status_code == 400
    assert resp.json["error"] == "No available parking spaces"

    updated_parking = db.session.query(Parking).get(4)
    assert updated_parking.count_available_places == 0

    client_parking = db.session.query(ClientParking).filter_by(client_id=3, parking_id=4).first()
    assert client_parking is None

def test_check_out_parking(app_client, db) -> None:
    # db.session.rollback()
    # db.session.query(ClientParking).filter_by(client_id=5).delete()
    # db.session.query(Client).filter_by(id=5).delete()
    # db.session.query(Parking).filter_by(id=5).delete()
    # db.session.commit()

    logger.info("Käynnistetään test_check_out_parking")
    client = Client(id=5, name="Ahti", surname="Virtanen",
                    credit_card="1234-5678-1234-3456", car_number="AM456BC")
    db.session.add(client)
    logger.info(f'asiakkas on {client}')

    parking = Parking(id=5, address="Test Address5",
                      count_places=20, count_available_places=18,
                      opened=True, opening_time="07:00", closing_time="21:00")
    db.session.add(parking)
    logger.info(f'Pysäköinti on {parking}')
    db.session.commit()
    logger.info("Sitoutunut asiakas ja pysäköinti")

    check_in_time = datetime.now()
    check_in = ClientParking(
        client_id=5,
        parking_id=5,
        time_in=check_in_time ,
        time_out=None
    )
    logger.info(f'Creating check-in with data: {check_in.__dict__}')
    db.session.add(check_in)
    db.session.commit()

    assert client.credit_card is not None
    before = parking.count_available_places
    logger.info(f'Pysäköintipaikkojen määrä ennen on {before} ')

    check_in.time_out = db.session.query(func.now()).scalar()
    parking.count_available_places += 1
    after = parking.count_available_places
    logger.info(f'pysäköintipaikkojen määrä check-out jälkeen on {after} ')

    assert after - before == 1


