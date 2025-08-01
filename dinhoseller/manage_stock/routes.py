from datetime import datetime
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_stock.model import Stock, StockMigration
from dinhoseller.manage_suppliers.model import ProductSupplied, Supplier
import json


stock_bp = Blueprint('stock_bp', __name__)

# Chemin absolu vers application.setting.json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SETTINGS_FILE = os.path.join(BASE_DIR, 'application.settings', 'application.setting.json')

# Create Stock
@stock_bp.route('/add', methods=['POST'])
@jwt_required()
def create_stock():
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['code', 'name', 'reference', 'category', 'quantity', 'minimum_stock', 'suppliers']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        existing_stock = Stock.query.filter(
            (Stock.name == data.get('name')) |
            (Stock.reference == data.get('reference')) |
            (Stock.code == data.get('code'))
        ).first()

        if existing_stock:
            return jsonify({'error': 'Ce produit existe déjà'}), 400
        
        # Find all supplier prices for the given product
        product_name = data.get('name').strip()
        products_supplied = ProductSupplied.query.filter_by(productName=product_name).all()

        if not products_supplied:
            return jsonify({'error': 'Pas de fournisseur existant pour ce produit'}), 404

        # Get the highest supplier price
        highest_price = max(product.supplierPrice for product in products_supplied)

        print(os.path.exists(SETTINGS_FILE))

        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            app_settings = json.load(f)

        benef = app_settings.get('BENEF')

        price_with_benef = highest_price + highest_price * benef

        decodeToken = get_jwt()

        stock = Stock(
            code=data.get('code'),
            name=data.get('name').strip(),
            reference=data.get('reference'),
            description=data.get('description'),
            category=data['category']['name'],
            quantity=data.get('quantity'),
            weight=data.get('weight'),
            brand=data.get('brand'),
            added_date=datetime.utcnow(),
            minimum_stock=data.get('minimum_stock'),
            supplierlist=str(data['suppliers']),
            price=price_with_benef,
            user_id=int(decodeToken.get("sub"))
        )

        db.session.add(stock)
        db.session.commit()

        return jsonify(stock.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get All Stocks
@stock_bp.route('/all', methods=['GET'])
@jwt_required()
def get_stocks():
    try:
        stocks = Stock.query.all()
        if not stocks:
            return jsonify({'error': 'Aucun produit trouvé'}), 404
        return jsonify([stock.to_dict() for stock in stocks]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get Stock by ID
@stock_bp.route('/getProductById/<int:stock_id>', methods=['GET'])
@jwt_required()
def get_stock(stock_id):
    try:
        stock = Stock.query.get(stock_id)
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        return jsonify(stock.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500
    
# Get all suppliers for a given product
@stock_bp.route('/suppliers_by_product/<string:product_name>', methods=['GET'])
@jwt_required()
def get_products_supplied_by_product(product_name):
    try:
        products_supplied = ProductSupplied.query.filter_by(productName=product_name.strip()).all()
        if not products_supplied:
            return jsonify({'error': 'Aucun fournisseur trouvé pour ce produit'}), 404
        
        suppliers_list = [supplier.to_dict() for supplier in products_supplied]

        return jsonify(suppliers_list), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500


# Update Stock
@stock_bp.route('/update/<user_id>', methods=['PUT'])
@jwt_required()
def update_stock(user_id):
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
 
        stock = Stock.query.get(user_id)
        if not stock:
            return jsonify({'error': 'Produit introuvable'}), 404

        required_fields = ['name','reference', 'category', 'price', 'quantity', 'minimum_stock', 'suppliers']
        missing_fields = [field for field in required_fields if field not in data and getattr(stock, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields'}), 400

        stock.name = data["name"]
        stock.code = data["code"]
        stock.category = data["category"]["name"]
        stock.reference = data["reference"]
        stock.quantity = data["quantity"]
        stock.weight = data["weight"]
        stock.brand = data["brand"]
        stock.minimum_stock = data["minimum_stock"]
        stock.supplierlist = str(data["suppliers"]),

        db.session.commit()
        return jsonify(stock.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Delete Stock
@stock_bp.route('/delete/<int:stock_id>', methods=['DELETE'])
@jwt_required()
def delete_stock(stock_id):
    try:
        stock = Stock.query.get(stock_id)
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        
        db.session.delete(stock)
        db.session.commit()
        return jsonify({'message': 'Stock deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500
    
# Create Stock Migration
@stock_bp.route('/stock_migrations', methods=['POST'])
@jwt_required()
def create_stock_migration():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['type_migration', 'user_id', 'quantite']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        stock_migration = StockMigration(
            type_migration=data.get('type_migration'),
            user_id=data.get('user_id'),
            quantite=data.get('quantite'),
        )

        db.session.add(stock_migration)
        db.session.commit()
        return jsonify(stock_migration.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get All Stock Migrations
@stock_bp.route('/stock_migrations', methods=['GET'])
@jwt_required()
def get_stock_migrations():
    try:
        stock_migrations = StockMigration.query.all()
        if not stock_migrations:
            return jsonify({'message': 'No stock migrations found'}), 404
        return jsonify([migration.to_dict() for migration in stock_migrations]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get Stock Migration by ID
@stock_bp.route('/stock_migrations/<int:migration_id>', methods=['GET'])
@jwt_required()
def get_stock_migration(migration_id):
    try:
        stock_migration = StockMigration.query.get(migration_id)
        if not stock_migration:
            return jsonify({'error': 'Stock migration not found'}), 404
        return jsonify(stock_migration.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Update Stock Migration
@stock_bp.route('/stock_migrations/<int:migration_id>', methods=['PUT'])
@jwt_required()
def update_stock_migration(migration_id):
    try:
        stock_migration = StockMigration.query.get(migration_id)
        if not stock_migration:
            return jsonify({'error': 'Stock migration not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        stock_migration.type_migration = data.get('type_migration', stock_migration.type_migration)
        stock_migration.user_id = data.get('user_id', stock_migration.user_id)
        stock_migration.quantite = data.get('quantite', stock_migration.quantite)

        db.session.commit()
        return jsonify(stock_migration.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Delete Stock Migration
@stock_bp.route('/stock_migrations/<int:migration_id>', methods=['DELETE'])
@jwt_required()
def delete_stock_migration(migration_id):
    try:
        stock_migration = StockMigration.query.get(migration_id)
        if not stock_migration:
            return jsonify({'error': 'Stock migration not found'}), 404
        
        db.session.delete(stock_migration)
        db.session.commit()
        return jsonify({'message': 'Stock migration deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500
