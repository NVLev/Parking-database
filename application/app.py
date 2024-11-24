import os
import random
import sys
from datetime import datetime
from typing import List
from flasgger import Swagger, swag_from
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from sqlalchemy import func, MetaData

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.model import engine
from config import logger
load_dotenv()

db_initialized = False

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    app.config['SWAGGER'] = {
        'title': 'Pysäköintisovellus API',
        'uiversion': 3,
        'specs_route': '/docs/',
        'openapi': '3.0.0',
        'specs': [{
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }]
    }
    swagger = Swagger(app)

    from models.model import db
    db.init_app(app)
    from models.model import Base, Client, Parking, ClientParking, is_parking_open

    sample_clients = [
        {"name": "John", "surname": "Doe", "credit_card": "1234567890123456", "car_number": "ABC-123"},
        {"name": "Jane", "surname": "Doe", "credit_card": "9876543210123456", "car_number": "DEF-456"}
    ]
    sample_parkings = [
        {"address": "Main Street 1", "count_places": 10, "count_available_places": 10, "opening_time": "08:00",
         "closing_time": "20:00"},
        {"address": "Oak Avenue 2", "count_places": 5, "count_available_places": 5, "opening_time": "09:00",
         "closing_time": "18:00"}
    ]

    @app.before_request
    def initialize_database():
        global db_initialized
        if not db_initialized:
            metadata = MetaData()
            metadata.reflect(bind=engine)
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            for client_data in sample_clients:
                new_client = Client(
                    name=client_data["name"],
                    surname=client_data["surname"],
                    credit_card=client_data["credit_card"],
                    car_number=client_data["car_number"],
                )
                db.session.add(new_client)
                logger.info(f'Uusi käyttäjä {new_client} on lisätty')
            for parking_data in sample_parkings:
                new_parking = Parking(
                    address=parking_data["address"],
                    opened=is_parking_open(
                        datetime.strptime(parking_data["opening_time"], "%H:%M").time(),
                        datetime.strptime(parking_data["closing_time"], "%H:%M").time(),
                    ),
                    count_places=parking_data["count_places"],
                    count_available_places=parking_data["count_available_places"],
                    opening_time=datetime.strptime(parking_data["opening_time"], "%H:%M").time(),
                    closing_time=datetime.strptime(parking_data["closing_time"], "%H:%M").time(),
                )
                db.session.add(new_parking)
                logger.info(f'Uusi pysäköinti {new_parking} on lisätty')
            db.session.commit()
            db_initialized = True

    @app.route("/clients", methods=['GET'])
    @swag_from('docs/clients_get.yml')
    def get_users_handler():
        """API-päätepiste - hakeminen asiakkaita"""
        clients: List[Client] = db.session.query(Client).all()
        clients_list = [c.to_json() for c in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=['GET'])
    @swag_from('docs/clients_client_id_get.yml')
    def get_user_handler(client_id: int):
        """API-päätepiste - hakeminen asiakasta sen ID:n perusteella."""
        client: Client = db.session.query(Client).get(client_id)
        return jsonify(client.to_json()), 200

    @app.route("/clients/add_client", methods=['POST'])
    @swag_from('docs/clients_add_client_post.yml')
    def add_client():
        """ API-päätepiste - lisää uusia asiakasta"""
        data = request.json
        name = data.get('name')
        surname = data.get('surname')
        credit_card = data.get('credit_card')
        car_number = data.get('car_number')

        new_client = Client(name=name,
                            surname=surname,
                            credit_card=credit_card,
                            car_number=car_number)

        db.session.add(new_client)
        db.session.commit()
        return 'Uusi asiakas lisätty tietokantaan', 201


    @app.route("/parking/add_parking", methods=['POST'])
    @swag_from('docs/parking_add_parking_post.yml')
    def add_parking():
        """API-päätepiste - lisää uusia pysäköintiä"""
        try:
            data = request.json
            address = data.get('address')
            #
            count_places = data.get('count_places')
            count_available_places = data.get('count_available_places')
            opening_time = datetime.strptime(data.get('opening_time'), '%H:%M').time()
            closing_time = datetime.strptime(data.get('closing_time'), '%H:%M').time()

            new_parking = Parking(address=address,
                                  opened = is_parking_open(opening_time, closing_time),
                                  count_places = count_places,
                                  count_available_places=count_available_places,
                                  opening_time=opening_time,
                                  closing_time=closing_time
                                  )

            db.session.add(new_parking)
            db.session.commit()
            return 'Uusi parkkipaika  lisätty tietokantaan', 201
        except Exception as e:
            logger.info(f"Error:, {str(e)}")
            return jsonify({"error": str(e)}), 400

    @app.route("/client_parkings", methods=['POST'])
    @swag_from('docs/client_parkings_post.yml')
    def check_in_parking():
        """
        API-päätepiste käsittelee asiakkaan pysäköintipaikan sisäänkirjautumisen
        :return:    JSON-muotoinen vastaus, jossa on seuraavat tiedot:
                    "message": "Check-in successful" (Sisäänkirjautuminen onnistui)
                    "check_in_time": Tarkka sisäänkirjautumisaika tietokannasta.
                    "parking_address": Pysäköintipaikan osoite.
                    "available_places": Pysäköintipaikalla jäljellä olevien vapaiden
                    paikkojen määrä sisäänkirjautumisen jälkeen.
        """
        data = request.json
        client_id = data.get('client_id')
        parking_id = data.get('parking_id')

        # Validoi syöttö (seka asiakasta että parkkipaikkaa
        if not client_id or not parking_id:
            return jsonify({"error": "Sekä client_id että parking_id vaaditaan"}), 400

        # Tarkista asiakasta
        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({"error": "Asiakasta ei löydy"}), 404

        # Tarkista parkkipaikkaa (on ja auki)
        parking = db.session.query(Parking).get(parking_id)
        if not parking:
            return jsonify({"error": "Pysäköintiä ei löydy"}), 404
        if not parking.opened:
            return jsonify({"error": "Pysäköinti on suljettu"}), 400

        # Tarkista vapaita paikkoja pysäköintilla
        if parking.count_available_places <= 0:
            return jsonify({"error": "Ei käytettävissä olevia pysäköintipaikkoja"}), 400

        new_client_parking = ClientParking(
            client_id=client_id,
            parking_id=parking_id,
            time_in=datetime.utcnow()
        )
        # Päivitä paikat
        parking.count_available_places -= 1

        db.session.add(new_client_parking)
        db.session.commit()

        # Hae todellinen sisäänkirjautumisaika tietokannasta
        check_in_time = db.session.query(func.now()).scalar()

        return jsonify({
            "message": "Check-in successful",
            "check_in_time": new_client_parking.time_in,
            "parking_address": parking.address,
            "available_places": parking.count_available_places
        }), 201

    @app.route("/check_out_parkings", methods=['DELETE'])
    @swag_from('docs/check_out_parkings_delete.yml')
    def delete_client_parking():
        logger.info("Aloitetaan delete_client_parking")
        data = request.json
        client_id = data.get('client_id')
        parking_id = data.get('parking_id')

        if not client_id or not parking_id:
            return jsonify({"error": "Sekä client_id että parking_id vaaditaan."}), 400

        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({"error": "Asiakasta ei löydy"}), 404

        parking = db.session.query(Parking).get(parking_id)
        if not parking:
            return jsonify({"error": "Pysäköintiä ei löydy"}), 404
        if not parking.opened:
            return jsonify({"error": "Pysäköintiä ei löydy"}), 400

        check_in = db.session.query(ClientParking).filter_by(
                client_id=client_id,
                parking_id=parking_id,
                time_out=None
            ).first()
        logger.info(f'check-in on {check_in}')
        if not check_in:
            return jsonify(
                {"error": "Tälle asiakkaalle ja pysäköintipaikalle ei löytynyt aktiivista sisäänkirjautumista"}), 404

        check_in.time_out = db.session.query(func.now()).scalar()
        logger.info(f'time_out - {check_in.time_out}')

        parking.count_available_places += 1

        db.session.commit()
        return jsonify({"message": "Uloskirjautuminen suoritettu onnistuneesti"}), 200
    return app