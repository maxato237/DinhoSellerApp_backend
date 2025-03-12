from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dinhoseller import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref("roles", uselist=False))

def insert_initial_data():
    if Role.query.first() is None:
        roles = [
            Role(name='supadmin', description='super admin role with full access'),
            Role(name='admin', description='admin role with limited access'),
            Role(name='basic', description='Basic employee role')
        ]
        
        db.session.bulk_save_objects(roles)
        db.session.commit()

def create_app(config_class=None):
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

        # Charge la configuration fournie, sinon utilise la configuration par défaut
    if config_class:
        app.config.from_object(config_class)
    else:
        # Utilisation de la configuration définie dans le fichier de config
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config.SQL_CONNEXION['user']}:" \
                                                f"{config.SQL_CONNEXION['password']}@" \
                                                f"{config.SQL_CONNEXION['host']}:" \
                                                f"{config.SQL_CONNEXION['port']}/" \
                                                f"{config.SQL_CONNEXION['database']}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config.from_object(config)

    # Configuration JWT et autres paramètres
    app.config['SECRET_KEY'] = config.Config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = config.Config.SECRET_JWT_KEY
    app.config['JWT_TOKEN_LOCATION'] = config.Config.JWT_TOKEN_LOCATION
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_SESSION_COOKIE'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)


    with app.app_context():
        from dinhoseller.authentication.routes import auth
        from dinhoseller.manage_clients.routes import client_bp
        from dinhoseller.manage_invoices.routes import invoice_bp
        from dinhoseller.manage_stock.routes import stock_bp
        from dinhoseller.manage_suppliers.routes import supplier_bp
        from dinhoseller.manage_user.routes import user_bp
        from dinhoseller.manage_charge.routes import charge_bp
        from dinhoseller.manage_notication.routes import notication_bp
        from dinhoseller.manage_session.routes import session_bp    

        app.register_blueprint(auth, url_prefix='/auth')
        app.register_blueprint(client_bp, url_prefix='/clients')
        app.register_blueprint(invoice_bp, url_prefix='/invoices')
        app.register_blueprint(stock_bp, url_prefix='/stock')
        app.register_blueprint(supplier_bp, url_prefix='/suppliers')
        app.register_blueprint(user_bp, url_prefix='/users')
        app.register_blueprint(charge_bp, url_prefix='/charges')
        app.register_blueprint(notication_bp, url_prefix='/notifications')
        app.register_blueprint(session_bp, url_prefix='/sessions')

        db.create_all()
        insert_initial_data()
    return app