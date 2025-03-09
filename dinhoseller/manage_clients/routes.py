from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_clients.model import Client

client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/clients', methods=['POST'])
def create_client():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'type', 'phone', 'payment_method']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        client = Client(
            name=data.get('name'),
            type=data.get('type'),
            group=data.get('group'),
            principal_address=data.get('principal_address'),
            facturation_address=data.get('facturation_address'),
            email=data.get('email'),
            phone=data.get('phone'),
            specific_price=data.get('specific_price'),
            payment_requirement=data.get('payment_requirement'),
            payment_method=data.get('payment_method'),
            notes=data.get('notes')
        )

        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients', methods=['GET'])
def get_clients():
    try:
        clients = Client.query.all()
        if not clients:
            return jsonify({'message': 'No clients found'}), 404
        return jsonify([client.to_dict() for client in clients]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        return jsonify(client.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'type', 'phone', 'payment_method']
        missing_fields = [field for field in required_fields if field not in data and getattr(client, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        client.name = data.get('name', client.name)
        client.type = data.get('type', client.type)
        client.group = data.get('group', client.group)
        client.principal_address = data.get('principal_address', client.principal_address)
        client.facturation_address = data.get('facturation_address', client.facturation_address)
        client.email = data.get('email', client.email)
        client.phone = data.get('phone', client.phone)
        client.specific_price = data.get('specific_price', client.specific_price)
        client.payment_requirement = data.get('payment_requirement', client.payment_requirement)
        client.payment_method = data.get('payment_method', client.payment_method)
        client.notes = data.get('notes', client.notes)

        db.session.commit()
        return jsonify(client.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/<int:client_id>', methods=['DELETE'])
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
        return jsonify({'error': str(e)}), 500
