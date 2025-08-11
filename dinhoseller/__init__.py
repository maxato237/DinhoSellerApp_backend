import os
import subprocess
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sys
import shutil
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

    def resource_path(relative_path):
        """Donne le chemin absolu (compatible PyInstaller et mode normal)."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    # -- Gestion base de données SQLite --
    db_path = config.SQLITE_DB_CONNEXION['database']
    db_dir = os.path.dirname(db_path)
    db_source_embedded = resource_path("dinho_local.db")

    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
        except Exception as e:
            print(f"Erreur création dossier base: {e}")

    if not os.path.exists(db_path):
        try:
            shutil.copy2(db_source_embedded, db_path)
        except Exception as e:
            print(f"Erreur copie base: {e}")

    # -- Gestion des fichiers de settings --
    settings_path = config.Config.SETTINGS_FILE
    settings_dir = os.path.dirname(settings_path)
    settings_source_embedded = resource_path(os.path.join("dinhoseller", "application.settings", "application.setting.json"))

    if not os.path.exists(settings_dir):
        try:
            os.makedirs(settings_dir)
        except Exception as e:
            print(f"Erreur création dossier settings: {e}")

    if not os.path.exists(settings_path):
        try:
            shutil.copy2(settings_source_embedded, settings_path)
        except Exception as e:
            print(f"Erreur copie fichier settings: {e}")


    # -- Création de l'app Flask --
    app = Flask(__name__)
    if config:
        app.config.from_object(config)

    CORS(app,
         resources={r"/api/*": {"origins": ["file://",
             "http://localhost:4200",
             "https://drinhosellerapp-fontend.onrender.com"
         ]}},
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"]
    )

        # Charge la configuration fournie, sinon utilise la configuration par défaut
    if config_class:
        app.config.from_object(config_class)
    else:
        # Utilisation de la configuration définie dans le fichier de config
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{config.SQLITE_DB_CONNEXION['database']}"
        # app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config.AWS_DB_CONNEXION['user']}:" \
        #                                         f"{config.AWS_DB_CONNEXION['password']}@" \
        #                                         f"{config.AWS_DB_CONNEXION['host']}:" \
        #                                         f"{config.AWS_DB_CONNEXION['port']}/" \
        #                                         f"{config.AWS_DB_CONNEXION['database']}"
        # app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{config.POSTGRESQL_CONNEXION['user']}:" \
        #                                         f"{config.POSTGRESQL_CONNEXION['password']}@" \
        #                                         f"{config.POSTGRESQL_CONNEXION['host']}:" \
        #                                         f"{config.POSTGRESQL_CONNEXION['port']}/" \
        #                                         f"{config.POSTGRESQL_CONNEXION['database']}"
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

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Votre session a expiré. Veuillez vous reconnecter.'}), 401

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

        app.register_blueprint(auth, url_prefix='/api/auth')
        app.register_blueprint(client_bp, url_prefix='/api/clients')
        app.register_blueprint(invoice_bp, url_prefix='/api/invoices')
        app.register_blueprint(stock_bp, url_prefix='/api/stocks')
        app.register_blueprint(supplier_bp, url_prefix='/api/suppliers')
        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(charge_bp, url_prefix='/api/charges')
        app.register_blueprint(notication_bp, url_prefix='/api/notifications')
        app.register_blueprint(session_bp, url_prefix='/api/sessions')

        db.create_all()
        insert_initial_data()
    return app