from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_clients.model import Client

client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/add', methods=['POST'])
@jwt_required()
def create_client():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'phone', 'payment_method']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        existing_client = Client.query.filter(
            (Client.phone == data.get('phone')) |
            (Client.email == data.get('email'))
        ).first()

        if existing_client:
            return jsonify({'error': 'Un client avec le même phone ou email existe déjà'}), 400
        
        decodeToken = get_jwt()

        client = Client(
            name=data.get('name'),
            principal_address=data.get('principal_address'),
            facturation_address=data.get('facturation_address'),
            email=data.get('email'),
            phone=data.get('phone'),
            specific_price= float(data.get('specific_price'))/100,
            payment_requirement=data['payment_requirement']['name'],
            payment_method=data['payment_method']['name'],
            notes=data.get('notes'),
            representant=data['representant']['id'],
            assujetti_tva=data.get('assujetti_tva', False),
            concern_ecomp=data.get('concern_ecomp', False),
            user_id=int(decodeToken.get("sub"))
        )

        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500
        
@client_bp.route('/all', methods=['GET'])
def get_clients():
    try:
        clients = Client.query.all()
        if not clients:
            return jsonify({'error': 'No clients found'}), 404
        return jsonify([client.to_dict() for client in clients]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

@client_bp.route('/getById/<int:client_id>', methods=['GET'])
def get_client(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        return jsonify(client.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

@client_bp.route('/update/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    # try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'phone', 'payment_method']
        missing_fields = [field for field in required_fields if field not in data and getattr(client, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        client.name = data.get('name')
        client.principal_address = data.get('principal_address')
        client.facturation_address = data.get('facturation_address')
        client.email = data.get('email')
        client.phone = data.get('phone')
        client.specific_price = float(data.get('specific_price'))/100
        client.payment_requirement = data['payment_requirement']['name']
        client.payment_method = data['payment_method']['name']
        client.notes = data.get('notes')
        client.representant = data['representant']['id']
        client.assujetti_tva = data.get('tva', False) 
        client.concern_ecomp = data.get('ecomp', False)

        db.session.commit()
        return jsonify(client.to_dict()), 200
    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({'error': 'Erreur inatendu lors de la mise à jour'}), 500

@client_bp.route('/delete/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': 'Client deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500
