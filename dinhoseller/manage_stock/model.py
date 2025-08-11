from dinhoseller import db
from dinhoseller.manage_invoices.model import invoice_products

class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    reference = db.Column(db.String(255), unique=True)
    code = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    brand = db.Column(db.String(100))
    added_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)
    minimum_stock = db.Column(db.Integer, nullable=False)

    stock_migration_id = db.Column(db.Integer, db.ForeignKey('stock_migration.id'), unique=True)
    invoices = db.relationship('Invoice', secondary=invoice_products, back_populates='products')
    group_prices = db.relationship('GroupPrice', back_populates='stocks', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self):
        return f"<Stock {self.id} (TYPE: {self.name})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'reference': self.reference,
            'category': self.category,
            'price': self.price,
            'quantity': self.quantity,
            'weight': self.weight,
            'brand': self.brand,
            'addedDate': self.added_date.strftime('%Y-%m-%d') if self.added_date else None,
            'minimumStock': self.minimum_stock,
            'expirationDate': self.expiration_date.strftime('%Y-%m-%d') if self.expiration_date else None,
            'user_id': self.user_id,
            'stock_migration_id': self.stock_migration_id,
            'invoices': [invoice.to_dict() for invoice in self.invoices] if self.invoices else None,
            'group_prices': [gp.to_dict() for gp in self.group_prices] if self.group_prices else None
        }

class StockMigration(db.Model):
    __tablename__ = 'stock_migration'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_migration = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    date_migration = db.Column(db.DateTime, default=db.func.current_timestamp())
    quantite = db.Column(db.Integer, nullable=False)

    stock = db.relationship("Stock", backref=db.backref("stock_migration", uselist=False))

    def to_dict(self):
        return {
            'id': self.id,
            'type_migration': self.type_migration,
            'user_id': self.user_id,
            'date_migration': self.date_migration.strftime('%Y-%m-%d %H:%M:%S') if self.date_migration else None,
            'quantite': self.quantite,
            'stock_id': self.stock.id if self.stock else None
        }

    def __repr__(self):
        return f"<StockMigration {self.id} de {self.quantite} pour l'article {self.stock_id}>"
  
class GroupPrice(db.Model):
    __tablename__ = 'groups_prices'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Float, nullable=False)

    group_id = db.Column(db.Integer, db.ForeignKey('groups_clients.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)

    groups_clients = db.relationship('Groups_clients', back_populates='group_prices')
    stocks = db.relationship('Stock', back_populates='group_prices')

    def __repr__(self):
        return f"<GroupPrice group={self.group_id} product={self.stock_id} price={self.price}>"

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'group_name': self.group.name if self.group else None,
            'stock_id': self.stock_id,
            'stock_name': self.product.name if self.product else None,
            'price': self.price
        }

