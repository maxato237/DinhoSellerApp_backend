from dinhoseller import db
from datetime import date, datetime


# Table d'association entre Invoice et Stock
invoice_products = db.Table(
    'invoice_products',
    db.Column('invoice_id', db.Integer, db.ForeignKey('invoices.num'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
)


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    num = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    code_facture = db.Column(db.String(20), unique=True, nullable=False) 
    status = db.Column(db.String(50), nullable=False)  
    TVA = db.Column(db.Float, nullable=True)  
    HT = db.Column(db.Float, nullable=True)  
    TTC = db.Column(db.Float, nullable=True)  
    ECOMP = db.Column(db.Float, nullable=True)
    PRECOMPTE = db.Column(db.Float, nullable=True)
    avance = db.Column(db.Float, nullable=True)  
    echeance = db.Column(db.Date)
    dateAdded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    invoice_lines = db.relationship("Invoice_line", backref="invoices", lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Stock', secondary=invoice_products, back_populates='invoices')

    def __repr__(self):
        return f"<Invoice {self.num} (CODE: {self.code_facture}, TYPE: {self.type})>"
    
    def generate_invoice_code(self):
        date_facture = self.dateAdded or datetime.utcnow()
        prefix = f"{date_facture.year}{date_facture.month:02d}-FAC-"

        dernier = db.session.query(Invoice).filter(Invoice.code_facture.startswith(prefix)) \
                        .order_by(Invoice.num.desc()) \
                        .with_for_update() \
                        .first()

        numero_facture = 1 if not dernier else int(dernier.code_facture.split("-")[-1]) + 1
        return f"{prefix}{numero_facture}"

    
    def to_dict(self):
        return {
            "num": self.num,
            "code_facture": self.code_facture,
            "status": self.status,
            "TVA": self.TVA,
            "HT": self.HT,
            "TTC": self.TTC,
            "ECOMP": self.ECOMP,
            "PRECOMPTE": self.PRECOMPTE,
            "avance": self.avance.strftime("%Y-%m-%d") if self.avance else None,
            "echeance": self.echeance.strftime("%Y-%m-%d") if self.echeance else None,
            "dateAdded": self.dateAdded.strftime("%Y-%m-%d %H:%M:%S"),
            "client_id": self.client_id,
            "user_id": self.user_id,
            "invoice_lines": [line.to_dict() for line in self.invoice_lines] if self.invoice_lines else None,
            "products": [product.to_dict() for product in self.products] if self.products else None
        }
    
class Invoice_line(db.Model):
    __tablename__ = 'invoice_lines'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    designation = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    PUH = db.Column(db.Float, nullable=False)
    PUTTC = db.Column(db.Float, nullable=True)
    PTTTC = db.Column(db.Float, nullable=True)
    PTH = db.Column(db.Float, nullable=False)
    PVC = db.Column(db.Float, nullable=False)

    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.num'), nullable=False)
    
    def __repr__(self):
        return f"<Invoice_line {self.id} (TYPE: {self.designation})>"
    
    def get_id(self):
        return self.id
    
    def to_dict(self):
        return {
            'id': self.id,
            'designation': self.designation,
            'quantity': self.quantity,
            'PUH': self.PUH,
            'PUTTC': self.PUTTC,
            'PTTTC': self.PTTTC,
            'PTH': self.PTH,
            'PVC': self.PVC,
            'invoice_id': self.invoice_id
        }
