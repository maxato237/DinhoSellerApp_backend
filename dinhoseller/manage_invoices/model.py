from dinhoseller import db
from datetime import date


# Table d'association entre Invoice et Stock
invoice_products = db.Table(
    'invoice_products',
    db.Column('invoice_id', db.Integer, db.ForeignKey('invoices.num'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    num = db.Column(db.Integer, primary_key=True) 
    type = db.Column(db.String(100), nullable=False)  
    status = db.Column(db.String(50), nullable=False)  
    TVA = db.Column(db.Float, nullable=False)  
    HT = db.Column(db.Float, nullable=False)  
    TTC = db.Column(db.Float, nullable=False)  
    ECOMP = db.Column(db.Float, nullable=True)
    avance = db.Column(db.Date)  
    echeance = db.Column(db.Date)
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False) 

    # Ajout de la clé étrangère user_id pour lier l'Invoice à un User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relation avec les lignes de facture (One-to-Many)
    invoice_lines = db.relationship("Invoice_line", backref="invoices", lazy=True, cascade="all, delete-orphan")

    # Relation plusieurs à plusieurs avec Stock via la table d'association
    products = db.relationship('Stock', secondary=invoice_products, back_populates='invoices')

    def __repr__(self):
        return f"<Invoice {self.num} (TYPE: {self.type})>"
    
    def to_dict(self):
        return {
            'num': self.num,
            'type': self.type,
            'status': self.status,
            'TVA': self.TVA,
            'HT': self.HT,
            'TTC': self.TTC,
            'ECOMP': self.ECOMP,
            'avance': self.avance.strftime('%Y-%m-%d') if self.avance else None,
            'echeance': self.echeance.strftime('%Y-%m-%d') if self.echeance else None,
            'client_id': self.client_id,
            'products': [product.to_dict() for product in self.products]  # Correction ici
        }


    
class Invoice_line(db.Model):
    __tablename__ = 'invoice_lines'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    designation = db.Column(db.String(255), nullable=False)
    PUH = db.Column(db.Float, nullable=False)
    PTH = db.Column(db.Float, nullable=False)
    PVC = db.Column(db.Float, nullable=False)

    # Ajout de la clé étrangère pour lier la ligne de facture à une facture
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.num'), nullable=False)
    
    def __repr__(self):
        return f"<Invoice_line {self.id} (TYPE: {self.designation})>"
    
    def get_id(self):
        return self.id
    
    def to_dict(self):
        return {
            'id': self.id,
            'designation': self.designation,
            'PUH': self.PUH,
            'PTH': self.PTH,
            'PVC': self.PVC
        }
