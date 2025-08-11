from dinhoseller import db

supplier_products = db.Table(
    'supplier_products',
    db.Column('supplier_id', db.Integer, db.ForeignKey('suppliers.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nc = db.Column(db.String(255),unique=True)
    name = db.Column(db.String(255), nullable=False,unique=True)
    status = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    postalCode = db.Column(db.String(20))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=False,unique=True)
    email = db.Column(db.String(255), unique=True)
    website = db.Column(db.String(255), nullable=True,unique=True)
    preferredPaymentMethod = db.Column(db.String(100), nullable=False)
    addedAt = db.Column(db.Date, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relation plusieurs à plusieurs avec Product via la table d'association supplier_products
    products = db.relationship('Stock', secondary='supplier_products', backref='suppliers', lazy='dynamic')

    def __repr__(self):
        return f"<NC : {self.nc} (ID: {self.id})>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nc': self.nc,
            'status': self.status,
            'address': self.address,
            'city': self.city,
            'postalCode': self.postalCode,
            'country': self.country,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'preferredPaymentMethod': self.preferredPaymentMethod,
            'addedAt': self.addedAt.strftime('%Y-%m-%d') if self.addedAt else None,
            'user_id' : self.user_id,
            'products': [product.to_dict() for product in self.products] if self.products else None
        }