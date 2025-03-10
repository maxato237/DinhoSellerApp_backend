from dinhoseller import db
from flask_sqlalchemy import SQLAlchemy



class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastname = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False, unique=True)
    password = db.column(db.String(255), nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    # Relation One-to-One avec UserDetails
    details = db.relationship("UserDetails", backref="users", uselist=False)

    # Relation One-to-Many avec Stock
    stocks = db.relationship("Stock", backref="users", lazy=True)

    # Ajout de la relation one-to-many avec Client
    clients = db.relationship('Client', backref='users', lazy=True)

    # Ajout de la relation One-to-Many avec Invoice
    invoices = db.relationship('Invoice', backref='users', lazy=True)

    # Relation One-to-Many avec Supplier
    suppliers = db.relationship('Supplier', backref='users', lazy=True)

    # Relation One-to-Many avec StockMigration
    stock_migrations = db.relationship('StockMigration', backref='users', lazy=True)

    notifications = db.relationship('Notification', backref = 'users',lazy=True)
    sessions = db.relationship('Session', backref = 'users',lazy=True)
    

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
