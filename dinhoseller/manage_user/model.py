from dinhoseller import db
from flask_sqlalchemy import SQLAlchemy



class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastname = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    details = db.relationship("UserDetails", backref="users", uselist=False)
    stocks = db.relationship("Stock", backref="users", lazy=True)
    clients = db.relationship('Client', backref='users', lazy=True)
    invoices = db.relationship('Invoice', backref='users', lazy=True)
    suppliers = db.relationship('Supplier', backref='users', lazy=True)
    stock_migrations = db.relationship('StockMigration', backref='users', lazy=True)
    notifications = db.relationship('Notification', backref = 'users',lazy=True)
    sessions = db.relationship('Session', backref = 'users',lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'lastname': self.lastname,
            'firstname': self.firstname,
            'phone': self.phone,
            'role_id': self.role_id,
            'password': self.password
        }
    

class UserDetails(db.Model):
    __tablename__ = 'user_details'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    genre = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    personnal_mail_address = db.Column(db.String(150), unique=True, nullable=True)
    address_mail = db.Column(db.String(150), unique=True, nullable=True)
    poste = db.Column(db.String(100), nullable=True)
    start_date_of_hire = db.Column(db.Date, nullable=True)
    contract_type = db.Column(db.String(50), nullable=True)
    salary = db.Column(db.Float, nullable=True)
    group = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
