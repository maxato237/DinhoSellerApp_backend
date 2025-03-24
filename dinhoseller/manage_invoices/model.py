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
    
    num = db.Column(db.Integer, primary_key=True) 
    code_facture = db.Column(db.String(20), unique=True, nullable=False)  # Code facture ajouté
    type = db.Column(db.String(100), nullable=False)  
    status = db.Column(db.String(50), nullable=False)  
    TVA = db.Column(db.Float, nullable=True)  
    HT = db.Column(db.Float, nullable=True)  
    TTC = db.Column(db.Float, nullable=True)  
    ECOMP = db.Column(db.Float, nullable=True)
    avance = db.Column(db.Float, nullable=True)  
    echeance = db.Column(db.Date)
    dateAdded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    invoice_lines = db.relationship("Invoice_line", backref="invoices", lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Stock', secondary=invoice_products, back_populates='invoices')

    def __repr__(self):
        return f"<Invoice {self.num} (CODE: {self.code_facture}, TYPE: {self.type})>"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.code_facture = self.generate_invoice_code()

    def generer_num(self, numero_facture):
        return f"{self.date_ajout.year}{self.date_ajout.month:02d}-FAC-{numero_facture}"
    
    def generate_invoice_code(self):
        date_facture = self.dateAdded or datetime.utcnow()
        prefix = f"{date_facture.year}{date_facture.month:02d}-FAC-"

        dernier = Invoice.query.filter(Invoice.code_facture.startswith(prefix)) \
                               .order_by(Invoice.num.desc()).first()

        numero_facture = 1 if not dernier else int(dernier.code_facture.split("-")[-1]) + 1
        return f"{prefix}{numero_facture}"


    
    def to_dict(self):
        return {
            "num": self.num,
            "code_facture": self.code_facture,
            "type": self.type,
            "status": self.status,
            "TVA": self.TVA,
            "HT": self.HT,
            "TTC": self.TTC,
            "ECOMP": self.ECOMP,
            "avance": self.avance.strftime("%Y-%m-%d") if self.avance else None,
            "echeance": self.echeance.strftime("%Y-%m-%d") if self.echeance else None,
            "dateAdded": self.dateAdded.strftime("%Y-%m-%d %H:%M:%S"),
            "client_id": self.client_id,
            "user_id": self.user_id
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
