from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_charge.model import Charge

charge_bp = Blueprint('charge_bp', __name__)

# Create Charge
@charge_bp.route('/charges', methods=['POST'])
def create_charge():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'amount']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        charge = Charge(
            name=data.get('name'),
            amount=data.get('amount'),
            description=data.get('description')
        )

        db.session.add(charge)
        db.session.commit()
        return jsonify(charge.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get All Charges
@charge_bp.route('/charges', methods=['GET'])
def get_charges():
    try:
        charges = Charge.query.all()
        if not charges:
            return jsonify({'message': 'No charges found'}), 404
        return jsonify([charge.to_dict() for charge in charges]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Charge by ID
@charge_bp.route('/charges/<int:charge_id>', methods=['GET'])
def get_charge(charge_id):
    try:
        charge = Charge.query.get(charge_id)
        if not charge:
            return jsonify({'error': 'Charge not found'}), 404
        return jsonify(charge.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update Charge
@charge_bp.route('/charges/<int:charge_id>', methods=['PUT'])
def update_charge(charge_id):
    try:
        charge = Charge.query.get(charge_id)
        if not charge:
            return jsonify({'error': 'Charge not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'amount']
        missing_fields = [field for field in required_fields if field not in data and getattr(charge, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        charge.name = data.get('name', charge.name)
        charge.amount = data.get('amount', charge.amount)
        charge.description = data.get('description', charge.description)

        db.session.commit()
        return jsonify(charge.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Charge
@charge_bp.route('/charges/<int:charge_id>', methods=['DELETE'])
def delete_charge(charge_id):
    try:
        charge = Charge.query.get(charge_id)
        if not charge:
            return jsonify({'error': 'Charge not found'}), 404
        
        db.session.delete(charge)
        db.session.commit()
        return jsonify({'message': 'Charge deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500