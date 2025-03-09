from dinhoseller import db

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    group = db.Column(db.Integer)
    principal_address = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)  
    specific_price = db.Column(db.String(255), nullable=True)  
    payment_requirement = db.Column(db.String(255), nullable=True)  
    facturation_address = db.Column(db.String(255))
    payment_method = db.Column(db.String(100), nullable=False)  
    notes = db.Column(db.Text) 

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    invoices = db.relationship("Invoice", backref="clients", lazy=True)


    def __repr__(self):
        return f"<Client {self.name} (ID: {self.id})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "group": self.group,
            "principal_address": self.principal_address,
            "email": self.email,
            "phone": self.phone,
            "specific_price": self.specific_price,
            "payment_requirement": self.payment_requirement,
            "facturation_address": self.facturation_address,
            "payment_method": self.payment_method,
            "notes": self.notes
        }
