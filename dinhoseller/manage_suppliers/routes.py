from datetime import date, datetime
import random
from faker import Faker
from flask import Blueprint, json, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_stock.model import Stock
from dinhoseller.manage_suppliers.model import ProductSupplied, Supplier
import random
from collections import defaultdict

faker = Faker()
supplier_bp = Blueprint('supplier_bp', __name__)

@supplier_bp.route('/add', methods=['POST'])
@jwt_required()
def create_supplier():
    # try:
        data = request.get_json()

        # Vérification des champs requis
        name = data.get('name')
        nc = data.get('nc')
        status = data.get('status')
        phone = data.get('phone')
        preferredPaymentMethod = data.get('preferredPaymentMethod')

        if not name or not status or not phone or not preferredPaymentMethod:
            return jsonify({'error': 'Champs requis manquants'}), 400

        # Vérifier si un fournisseur avec les mêmes valeurs uniques existe déjà
        existing_supplier = Supplier.query.filter(
            (Supplier.name == name) |
            (Supplier.nc == nc) |
            (Supplier.phone == phone) |
            (Supplier.email == data.get('email')) |
            (Supplier.website == data.get('website'))
        ).first()

        if existing_supplier:
            message = "Ce fournisseur existe déjà"
            return jsonify({'error': message}), 409

        decodeToken = get_jwt()

        # Récupérer les autres champs du JSON
        address = data.get('address') if 'address' in data else None
        city = data.get('city') if 'city' in data else None
        postalCode = data.get('postalCode') if 'postalCode' in data else None
        country = data['country']['name'] if 'country' in data else None
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
            nc=nc,
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
            user_id=int(decodeToken.get("sub"))
        )

        # Enregistrer le fournisseur
        db.session.add(supplier)
        db.session.flush()

        # Enregistrer les produits fournis dans ProductSupplied
        for product in products_supplied:
            supplierName = supplier.name
            productName = product.get('productName')
            existingProduct = Stock.query.filter(name == productName).first()
            
            if(existingProduct):
                with open('dinhoseller\\application.settings\\application.setting.json', "r", encoding="utf-8") as f:
                    app_settings = json.load(f)
                
                if(product.price >= (existingProduct.price - existingProduct.price*app_settings.get('BENEF'))):
                    existingProduct.price = product.price + product.price*app_settings.get('BENEF')
            supplierPrice = product.get('price')

            # Vérifier si les informations de produit sont valides
            if not productName or not supplierPrice:
                continue  

            # Créer un enregistrement pour chaque produit fourni
            product_supplied = ProductSupplied(
                supplierName=supplierName,
                productName=productName.strip(),
                supplierPrice=supplierPrice
            )
            db.session.add(product_supplied)

        db.session.commit()
        print('le fournisseur :', supplier)
        return jsonify(supplier.to_dict()), 201
    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({'error': f"Erreur lors de l'ajout du fournisseur : {str(e)}"}), 500

# Get All Suppliers
@supplier_bp.route('/all', methods=['GET'])
@jwt_required()
def get_suppliers():
    try:
        suppliers = Supplier.query.all()
        if not suppliers:
            return jsonify({'error': 'Aucun fournisseur trouvé'}), 404
        return jsonify([supplier.to_dict() for supplier in suppliers]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get all products supplied by a given supplier
@supplier_bp.route('/products_supplied/<string:supplier_name>', methods=['GET'])
@jwt_required()
def get_products_supplied_by_supplier(supplier_name):
    try:
        # Récupérer tous les produits fournis pour le fournisseur spécifié
        products_supplied = ProductSupplied.query.filter_by(supplierName=supplier_name).all()

        if not products_supplied:
            return jsonify({'error': 'Aucun produit fourni trouvé pour ce fournisseur'}), 404

        # Retourner les produits fournis sous forme de dictionnaire
        products_list = [product.to_dict() for product in products_supplied]

        return jsonify(products_list), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get Supplier by ID
@supplier_bp.route('/getSupplierById/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'error': 'Fournisseur introuvable'}), 404
        return jsonify(supplier.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Update Supplier
@supplier_bp.route('/update/<int:supplier_id>', methods=['PUT'])
@jwt_required()
def update_supplier(supplier_id):
    # try:
        data = request.json

        name = data.get('name')
        status = data.get('status')
        phone = data.get('phone')
        preferredPaymentMethod = data.get('preferredPaymentMethod')

        if not name or not status or not phone or not preferredPaymentMethod:
            return jsonify({'error': 'Champs requis manquants'}), 400

        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'error': 'Fournisseur introuvable'}), 404

        # Mise à jour des infos fournisseur
        supplier.nc = data.get('nc')
        supplier.name = name
        supplier.status = status['name']
        supplier.address = data.get('address')
        supplier.city = data.get('city')
        supplier.postal_code = data.get('postal_code')
        supplier.country = data['country']['name'] if 'country' in data else None
        supplier.phone = phone
        supplier.email = data.get('email')
        supplier.website = data.get('website')
        supplier.preferred_payment_method = preferredPaymentMethod['name']
        supplier.addedAt = datetime.utcnow()

        # Traitement des produits fournis
        new_products = data.get('productsSupplied', [])

        # Récupérer tous les produits actuels de ce fournisseur
        existing_products = ProductSupplied.query.filter_by(supplierName=supplier.name).all()
        existing_products_dict = {p.productName: p for p in existing_products}

        # Récupérer les noms des nouveaux produits
        new_product_names = set()
        for product in new_products:
            product_name = product.get('productName')
            supplier_price = product.get('price')
            existingProduct = Stock.query.filter(name == product_name).first()
            
            if(existingProduct):
                with open('dinhoseller\\application.settings\\application.setting.json', "r", encoding="utf-8") as f:
                    app_settings = json.load(f)
                
                if(product.price >= (existingProduct.price - existingProduct.price*app_settings.get('BENEF'))):
                    existingProduct.price = product.price + product.price*app_settings.get('BENEF')

            new_product_names.add(product_name)

            if product_name in existing_products_dict:
                # Mise à jour du prix
                existing_products_dict[product_name].supplierPrice = supplier_price
            else:
                # Ajout d'un nouveau produit
                new_product = ProductSupplied(
                    supplierName=supplier.name,
                    productName=product_name.strip(),
                    supplierPrice=supplier_price
                )
                db.session.add(new_product)

        # Supprimer les produits qui ne sont plus dans la liste
        for product_name, product_obj in existing_products_dict.items():
            if product_name not in new_product_names:
                db.session.delete(product_obj)

        # Commit global
        db.session.commit()

        return jsonify(supplier.to_dict()), 200

    # except Exception as e:
    #     db.session.rollback()
    #     print(str(e))
    #     return jsonify({'error': 'Erreur dans la mise à jour'}), 500

# Delete Supplier
@supplier_bp.route('/delete/<int:supplier_id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(supplier_id):
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'error': 'Fournisseur Introuvable'}), 404
        
        db.session.delete(supplier)
        db.session.commit()

        ProductSupplied.query.filter_by(supplierName=supplier.name).delete()
        db.session.commit()

        return jsonify({'message': 'Suppression reussite'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500
