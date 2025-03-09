from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_stock.model import Stock, StockMigration


stock_bp = Blueprint('stock_bp', __name__)

# Create Stock
@stock_bp.route('/stocks', methods=['POST'])
def create_stock():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'category', 'price', 'quantity', 'added_date', 'minimum_stock', 'supplier']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        stock = Stock(
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            price=data.get('price'),
            quantity=data.get('quantity'),
            weight=data.get('weight'),
            brand=data.get('brand'),
            added_date=data.get('added_date'),
            minimum_stock=data.get('minimum_stock'),
            supplier=data.get('supplier'),
            user_id=data.get('user_id')  # Assuming this comes in the request
        )

        db.session.add(stock)
        db.session.commit()
        return jsonify(stock.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get All Stocks
@stock_bp.route('/stocks', methods=['GET'])
def get_stocks():
    try:
        stocks = Stock.query.all()
        if not stocks:
            return jsonify({'message': 'No stocks found'}), 404
        return jsonify([stock.to_dict() for stock in stocks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Stock by ID
@stock_bp.route('/stocks/<int:stock_id>', methods=['GET'])
def get_stock(stock_id):
    try:
        stock = Stock.query.get(stock_id)
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        return jsonify(stock.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update Stock
@stock_bp.route('/stocks/<int:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    try:
        stock = Stock.query.get(stock_id)
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['name', 'category', 'price', 'quantity', 'added_date', 'minimum_stock', 'supplier']
        missing_fields = [field for field in required_fields if field not in data and getattr(stock, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        stock.name = data.get('name', stock.name)
        stock.description = data.get('description', stock.description)
        stock.category = data.get('category', stock.category)
        stock.price = data.get('price', stock.price)
        stock.quantity = data.get('quantity', stock.quantity)
        stock.weight = data.get('weight', stock.weight)
        stock.brand = data.get('brand', stock.brand)
        stock.added_date = data.get('added_date', stock.added_date)
        stock.minimum_stock = data.get('minimum_stock', stock.minimum_stock)
        stock.supplier = data.get('supplier', stock.supplier)

        db.session.commit()
        return jsonify(stock.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete Stock
@stock_bp.route('/stocks/<int:stock_id>', methods=['DELETE'])
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
        return jsonify({'error': str(e)}), 500
    

# Create Stock Migration
@stock_bp.route('/stock_migrations', methods=['POST'])
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
        return jsonify({'error': str(e)}), 500

# Get All Stock Migrations
@stock_bp.route('/stock_migrations', methods=['GET'])
def get_stock_migrations():
    try:
        stock_migrations = StockMigration.query.all()
        if not stock_migrations:
            return jsonify({'message': 'No stock migrations found'}), 404
        return jsonify([migration.to_dict() for migration in stock_migrations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get Stock Migration by ID
@stock_bp.route('/stock_migrations/<int:migration_id>', methods=['GET'])
def get_stock_migration(migration_id):
    try:
        stock_migration = StockMigration.query.get(migration_id)
        if not stock_migration:
            return jsonify({'error': 'Stock migration not found'}), 404
        return jsonify(stock_migration.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update Stock Migration
@stock_bp.route('/stock_migrations/<int:migration_id>', methods=['PUT'])
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
        return jsonify({'error': str(e)}), 500

# Delete Stock Migration
@stock_bp.route('/stock_migrations/<int:migration_id>', methods=['DELETE'])
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
        return jsonify({'error': str(e)}), 500
