from dinhoseller import db
from dinhoseller.manage_invoices.model import invoice_products

class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    brand = db.Column(db.String(100))
    added_date = db.Column(db.Date, nullable=False)
    minimum_stock = db.Column(db.Integer, nullable=False)
    supplier = db.Column(db.String(255), nullable=False)

    stock_migration_id = db.Column(db.Integer, db.ForeignKey('stock_migration.id'), unique=True)
        
    # Relation plusieurs à plusieurs avec Invoice via la table d'association
    invoices = db.relationship('Invoice', secondary=invoice_products, back_populates='products')


    # Clé étrangère pour l'utilisateur propriétaire du stock
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f"<Stock {self.id} (TYPE: {self.name})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'quantity': self.quantity,
            'weight': self.weight,
            'brand': self.brand,
            'addedDate': self.added_date.strftime('%Y-%m-%d') if self.added_date else None,
            'minimumStock': self.minimum_stock,
            'suppliers': [supplier.to_dict() for supplier in self.suppliers]
        }

class StockMigration(db.Model):
    __tablename__ = 'stock_migration'

    id = db.Column(db.Integer, primary_key=True)
    type_migration = db.Column(db.String(50), nullable=False)  # "ajout" ou "retrait"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    date_migration = db.Column(db.DateTime, default=db.func.current_timestamp())
    quantite = db.Column(db.Integer, nullable=False)

    stock = db.relationship("Stock", backref=db.backref("stock_migration", uselist=False))

    def __repr__(self):
        return f"<StockMigration {self.id} de {self.quantite} pour l'article {self.article_id}>"
