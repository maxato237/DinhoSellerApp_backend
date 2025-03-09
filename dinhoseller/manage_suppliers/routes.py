from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_suppliers.model import Supplier

supplier_bp = Blueprint('supplier_bp', __name__)

# Create Supplier
@supplier_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'type', 'status', 'phone', 'preferred_payment_method']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        supplier = Supplier(
            name=data.get('name'),
            type=data.get('type'),
            status=data.get('status'),
            address=data.get('address'),
            city=data.get('city'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website'),
            preferred_payment_method=data.get('preferred_payment_method'),
            added_at=data.get('added_at')
        )

        db.session.add(supplier)
        db.session.commit()
        return jsonify(supplier.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get All Suppliers
@supplier_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    try:
        suppliers = Supplier.query.all()
        if not suppliers:
            return jsonify({'message': 'No suppliers found'}), 404
        return jsonify([supplier.to_dict() for supplier in suppliers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Supplier by ID
@supplier_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'error': 'Supplier not found'}), 404
        return jsonify(supplier.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update Supplier
@supplier_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'error': 'Supplier not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'type', 'status', 'phone', 'preferred_payment_method']
        missing_fields = [field for field in required_fields if field not in data and getattr(supplier, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        supplier.name = data.get('name', supplier.name)
        supplier.type = data.get('type', supplier.type)
        supplier.status = data.get('status', supplier.status)
        supplier.address = data.get('address', supplier.address)
        supplier.city = data.get('city', supplier.city)
        supplier.postal_code = data.get('postal_code', supplier.postal_code)
        supplier.country = data.get('country', supplier.country)
        supplier.phone = data.get('phone', supplier.phone)
        supplier.email = data.get('email', supplier.email)
        supplier.website = data.get('website', supplier.website)
        supplier.preferred_payment_method = data.get('preferred_payment_method', supplier.preferred_payment_method)
        supplier.added_at = data.get('added_at', supplier.added_at)

        db.session.commit()
        return jsonify(supplier.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Supplier
@supplier_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'error': 'Supplier not found'}), 404
        
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({'message': 'Supplier deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
