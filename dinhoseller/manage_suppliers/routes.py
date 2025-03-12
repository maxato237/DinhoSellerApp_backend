from datetime import datetime
from flask import Blueprint, json, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_suppliers.model import Supplier

supplier_bp = Blueprint('supplier_bp', __name__)

# Create Supplier
@supplier_bp.route('/add', methods=['POST'])
@jwt_required()
def create_supplier():

    data = request.get_json()

    # Vérification des champs requis
    name = data.get('name')
    status = data.get('status')
    phone = data.get('phone')
    preferredPaymentMethod = data.get('preferredPaymentMethod')

    if not name or not status or not phone or not preferredPaymentMethod:
        return jsonify({'error': 'Champs requis manquants'}), 400

    # Vérifier si un fournisseur avec les mêmes valeurs uniques existe déjà
    existing_supplier = Supplier.query.filter(
        (Supplier.name == name) |
        (Supplier.phone == phone) |
        (Supplier.email == data.get('email')) |
        (Supplier.website == data.get('website'))
    ).first()

    if existing_supplier:
        message = "Ce fournisseur existe déjà"

        return jsonify({'error': message}), 400

    decodeToken = get_jwt()

    # Récupérer les autres champs du JSON
    address = data.get('address')
    city = data.get('city')
    postalCode = data.get('postalCode')
    country = data.get('country')
    email = data.get('email')
    website = data.get('website')

    # Convertir productsSupplied de string à JSON si nécessaire
    products_supplied = data.get('productsSupplied')
    if products_supplied:
        try:
            # Si productsSupplied est déjà un tableau, pas besoin de json.loads
            if isinstance(products_supplied, str):
                products_supplied = json.loads(products_supplied)
        except Exception as e:
            return jsonify({'error': f"Données 'productsSupplied' invalides"}), 400

    # Créer le fournisseur
    supplier = Supplier(
        name=name,
        status=status,
        phone=phone,
        preferredPaymentMethod=preferredPaymentMethod,
        address=address,
        city=city,
        postalCode=postalCode,
        country=country,
        email=email,
        website=website,
        addedAt=datetime.utcnow(),
        productsSupplied=products_supplied,  # Enregistrer en tant que JSON
        user_id=int(decodeToken.get("sub"))
    )

    try:
        db.session.add(supplier)
        db.session.commit()
        return jsonify(supplier.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': "Erreur lors de l'ajout du fournisseur"}), 500

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
        supplier.addedAt = data.get('addedAt', supplier.addedAt)

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
