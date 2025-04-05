from datetime import date, datetime
import random
from faker import Faker
from flask import Blueprint, json, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_suppliers.model import ProductSupplied, Supplier
import random
from collections import defaultdict

faker = Faker()
supplier_bp = Blueprint('supplier_bp', __name__)



@supplier_bp.route('/generate_suppliers', methods=['POST'])
def generate_suppliers():
    supplier_names = [
        "OSERVICES INTERNATIONAL", "HORIZON COMMODITIES", "ETS NSANGOU", "L2D TRADING INTERNATIONAL",
        "CENTRALE AGRO-ALIMENTAIRE DU CAMEROUN", "SOCIÉTÉ DE PRODUCTION ET DE DISTRIBUTION", 
        "NETS HOLDING", "ETABLISSEMENT SYSY", "SOCIÉTÉ SUCRIÈRE DU CAMEROUN", 
        "LES BRASSERIES DU CAMEROUN", "CHOCOLATERIE DU CAMEROUN (CHOCOCAM)", "SOCIÉTÉ CAMEROUNAISE DE SUCRERIE (SOCAS)", 
        "SOCIÉTÉ DE PRODUCTION DE CÉRÉALES (SPC)", "SOCIÉTÉ INDUSTRIELLE DE CACAO (SIC-CACAOS)", 
        "SOCIÉTÉ ANONYME DES BOISSONS DU CAMEROUN (SABC)", "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DES MÉTAUX (SCTM)", 
        "SOCIÉTÉ AFRICAINE DE RAFFINAGE (SAR)", "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DE BOIS (SCTB)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DU RIZ (SCTR)", "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DU SUCRE (SCTS)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DU CAFÉ (SCTC)", "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DES CÉRÉALES (SCTC)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSPORT ET SERVICES (SCTS)", "SOCIÉTÉ CAMEROUNAISE DE TRANSPORT ET SERVICES LOGISTIQUES (SCTL)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DU PÉTROLE (SCTP)", "SOCIÉTÉ CAMEROUNAISE DE GESTION DES TRANSPORTS (SCTG)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DES GRAINES OLEAGINEUSES (SCTO)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSPORTS TERRESTRES (SCTT)", "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION LAITIÈRE (SCTL)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DES MÉTAUX (SCTM)", "SOCIÉTÉ CAMEROUNAISE DE TRANSPORT ROUTIER (SCTR)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DU SOJA (SCTS)", "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DES PRODUITS AGRICOLES (SCTP)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DES CÉRÉALES (SCTC)", "SOCIÉTÉ CAMEROUNAISE DE TRANSPORT ET LOGISTIQUE (SCTL)", 
        "SOCIÉTÉ CAMEROUNAISE DE TRANSFORMATION DU CACAO (SCTC)"
    ]

    payment_methods = ['Orange Money', 'MTN Money', 'Virement', 'Espèce', 'Chèque']
    statuses = ['Active', 'Inactive', 'Pending']
    products = [
        "Riz blanc", "Pâtes alimentaires", "Lentilles sèches", "Haricots secs", "Pois chiches", 
        "Farine de blé", "Sucre en poudre", "Sel de table", "Huile végétale", "Concentré de tomate", 
        "Maïs en conserve", "Petits pois en conserve", "Sardines à l'huile", "Thon en conserve", 
        "Lait en poudre", "Café soluble", "Thé en sachets", "Chocolat en poudre", "Biscuits secs", 
        "Miel", "Confiture", "Céréales pour petit-déjeuner", "Pain de mie", "Craquelins", 
        "Noix de cajou", "Amandes", "Raisins secs", "Dattes séchées", "Fruits confits", "Soupes en sachet", 
        "Bouillon en cubes", "Purée de pommes de terre", "Sauce soja", "Vinaigre blanc", "Moutarde", 
        "Ketchup", "Mayonnaise", "Cornichons en bocal", "Olives vertes en bocal", "Poivre noir moulu", 
        "Paprika en poudre", "Cannelle en poudre", "Curcuma en poudre", "Origan séché", "Basilic séché", 
        "Lait concentré sucré", "Crème de marrons", "Beurre de cacahuète", "Sirop d'érable", "Levure chimique"
    ]

    suppliers = []
    used_names = set()  

    # Utilisation d'un dictionnaire pour stocker les prix des produits sans gestion des doublons
    product_price_map = {}

    for _ in range(30):
        name = random.choice(supplier_names)
        while name in used_names:
            name = random.choice(supplier_names)
        used_names.add(name)

        supplier = Supplier(
            name=name,
            status=random.choice(statuses),
            address=faker.address(),
            city=faker.city(),
            postalCode=faker.zipcode(),
            country=faker.country(),
            phone=faker.unique.phone_number(),
            email=faker.unique.email(),
            website=faker.unique.url(),
            preferredPaymentMethod=random.choice(payment_methods),
            addedAt=date.today(),
            user_id=1
        )
        db.session.add(supplier)
        suppliers.append(supplier)

        # Enregistrement des produits fournis par chaque fournisseur
        for product in products:
            price = round(random.uniform(1000, 4000), 2)  # Prix flottant entre 1000 et 4000

            # Ajout du prix à la liste associée au produit
            if product not in product_price_map:
                product_price_map[product] = []
            product_price_map[product].append(price)

            product_supplied = ProductSupplied(
                supplierName=name,
                productName=product,
                supplierPrice=price
            )

            db.session.add(product_supplied)

    db.session.commit()
    return jsonify({"message": "40 suppliers and products generated successfully!"})

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
        user_id=int(decodeToken.get("sub"))
    )

    # Enregistrer le fournisseur
    # try:
    db.session.add(supplier)
    db.session.commit()

    # Enregistrer les produits fournis dans ProductSupplied
    for product in products_supplied:
        supplierName = supplier.name
        productName = product.get('productName')
        supplierPrice = product.get('price')

        # Vérifier si les informations de produit sont valides
        if not productName or not supplierPrice:
            continue  # Skip invalid product data

        # Créer un enregistrement pour chaque produit fourni
        product_supplied = ProductSupplied(
            supplierName=supplierName,
            productName=productName,
            supplierPrice=supplierPrice
        )
        db.session.add(product_supplied)

    db.session.commit()
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

        # Mise à jour des informations du fournisseur
        supplier.name = name
        supplier.status = status['name']
        supplier.address = data.get('address')
        supplier.city = data.get('city')
        supplier.postal_code = data.get('postal_code')
        supplier.country = data.get('country')
        supplier.phone = phone
        supplier.email = data.get('email')
        supplier.website = data.get('website')
        supplier.preferred_payment_method = preferredPaymentMethod['name']
        supplier.addedAt = datetime.utcnow()  

        # Récupérer les produits fournis envoyés dans la demande
        products_supplied = data.get('productsSupplied')

        if products_supplied:

            # Ajouter les nouveaux produits fournis
            for product in products_supplied:
                productName = product.get('productName')
                supplierPrice = product.get('price')

                existing_product_supplied = ProductSupplied.query.filter_by(productName=productName, supplierName=supplier.name).first()
                if existing_product_supplied:
                    continue

                # Ajouter l'enregistrement dans ProductSupplied
                product_supplied = ProductSupplied(
                    supplierName=supplier.name,
                    productName=productName,
                    supplierPrice=supplierPrice
                )
                db.session.add(product_supplied)

            # Commit des changements
            db.session.commit()

        # Commit des changements du fournisseur
        db.session.commit()

        return jsonify(supplier.to_dict()), 200
    # except Exception as e:
    #     db.session.rollback()
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
