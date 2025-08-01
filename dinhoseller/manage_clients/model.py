from dinhoseller import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nc = db.Column(db.String(255),unique=True)
    name = db.Column(db.String(255), nullable=False)
    principal_address = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)  
    specific_price = db.Column(db.Float, nullable=True)  
    payment_requirement = db.Column(db.String(255), nullable=True)  
    facturation_address = db.Column(db.String(255))
    payment_method = db.Column(db.String(100), nullable=False)  
    notes = db.Column(db.Text) 
    representant = db.Column(db.Integer)
    assujetti_tva = db.Column(db.Boolean, default = False)
    concern_ecomp = db.Column(db.Boolean, default = False)
    concern_precompte = db.Column(db.Boolean, default = False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    invoices = db.relationship("Invoice", backref="clients", lazy=True)


    def __repr__(self):
        return f"<Client {self.name} (ID: {self.id})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            'nc': self.nc,
            "principal_address": self.principal_address,
            "email": self.email,
            "phone": self.phone,
            "specific_price": self.specific_price,
            "payment_requirement": self.payment_requirement,
            "facturation_address": self.facturation_address,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "representant": self.representant,
            "assujetti_tva": self.assujetti_tva,
            "concern_ecomp": self.concern_ecomp,
            "concern_precompte": self.concern_precompte,
            "user_id": self.user_id,
            "invoices": [invoice.to_dict() for invoice in self.invoices] if self.invoices else None
        }
