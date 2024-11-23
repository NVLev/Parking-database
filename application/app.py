import os
import random
import sys
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.model import engine

load_dotenv()

db_initialized = False

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL')
    # app.config.from_object(config)
    # config.init_app(app)

    # app.config.from_pyfile('/home/user/PycharmProjects/python_advanced/module_29_testing/hw/config.py')
    # Config.init_app
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.model import db
    db.init_app(app)
    from models.model import Base, Client, Parking, ClientParking, is_parking_open



    @app.before_request
    def initialize_database():
        global db_initialized
        if not db_initialized:
            Base.metadata.create_all(engine)

    @app.route("/clients", methods=['GET'])
    def get_users_handler():
        """API-päätepiste - hakeminen asiakkaita"""
        clients: List[Client] = db.session.query(Client).all()
        clients_list = [c.to_json() for c in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=['GET'])
    def get_user_handler(client_id: int):
        """API-päätepiste - hakeminen asiakasta sen ID:n perusteella."""
        client: Client = db.session.query(Client).get(client_id)
        return jsonify(client.to_json()), 200

    @app.route("/clients/add_client", methods=['POST'])
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
    def add_parking():
        """API-päätepiste - lisää uusia pysäköintiä"""
        try:
            print("Received data:", request.json)
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
            print("Error:", str(e))
            return jsonify({"error": str(e)}), 400

    @app.route("/client_parkings", methods=['POST'])
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
            return jsonify({"error": "Both client_id and parking_id are required"}), 400

        # Tarkista asiakasta
        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        # Tarkista parkkipaikkaa (on ja auki)
        parking = db.session.query(Parking).get(parking_id)
        if not parking:
            return jsonify({"error": "Parking not found"}), 404
        if not parking.opened:
            return jsonify({"error": "Parking is closed"}), 400

        # Tarkista vapaita paikkoja pysäköintilla
        if parking.count_available_places <= 0:
            return jsonify({"error": "No available parking spaces"}), 400

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
    def delete_client_parking():
        data = request.json
        client_id = data.get('client_id')
        parking_id = data.get('parking_id')

        if not client_id or not parking_id:
            return jsonify({"error": "Both client_id and parking_id are required"}), 400

        client = db.session.query(Client).get(client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        parking = db.session.query(Parking).get(parking_id)
        if not parking:
            return jsonify({"error": "Parking not found"}), 404
        if not parking.opened:
            return jsonify({"error": "Parking is closed"}), 400
        parking.count_available_places += 1

        check_in = db.session.query(ClientParking).filter_by(
                client_id=client_id,
                parking_id=parking_id,
                time_out=None
            ).first()

        if not check_in:
            return jsonify({"error": "No active check-in found for this client and parking"}), 404

        check_in.time_out = db.session.query(func.now()).scalar()

        parking.count_available_places += 1

        db.session.commit()
        return jsonify({"message": "Check-out completed successfully"}), 200
    return app