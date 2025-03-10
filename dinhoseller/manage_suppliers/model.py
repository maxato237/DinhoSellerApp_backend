from dinhoseller import db

supplier_products = db.Table(
    'supplier_products',
    db.Column('supplier_id', db.Integer, db.ForeignKey('suppliers.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), )
    city = db.Column(db.String(100), )
    postal_code = db.Column(db.String(20), )
    country = db.Column(db.String(100), )
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), unique=True, )
    website = db.Column(db.String(255), nullable=True)
    preferred_payment_method = db.Column(db.String(100), nullable=False)
    added_at = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relation plusieurs à plusieurs avec Product via la table d'association supplier_products
    products = db.relationship('Stock', secondary='supplier_products', backref='suppliers', lazy='dynamic')

    def __repr__(self):
        return f"<Supplier {self.name} (ID: {self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'address': self.address,
            'city': self.city,
            'postalCode': self.postal_code,
            'country': self.country,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'preferredPaymentMethod': self.preferred_payment_method,
            'productsSupplied': [product.to_dict() for product in self.products],
            'addedAt': self.added_at.strftime('%Y-%m-%d') if self.added_at else None
        }