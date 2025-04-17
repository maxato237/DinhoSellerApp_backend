from flask import Flask,json, jsonify
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
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{config.DISTANT_DB_CONNEXION['user']}:" \
                                                f"{config.DISTANT_DB_CONNEXION['password']}@" \
                                                f"{config.DISTANT_DB_CONNEXION['host']}:" \
                                                f"{config.DISTANT_DB_CONNEXION['port']}/" \
                                                f"{config.DISTANT_DB_CONNEXION['database']}"
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
    
    @app.route('/api/')
    def root():
        return jsonify({'message': 'good job'})
    
    @app.route('/api/isSuperAdminConfigured')
    def is_super_admin_configured():
        try:
            with open('dinhoseller/app_settings.json', 'r') as file:
                settings = json.load(file)
                return jsonify({
                    'isSuperAdminConfigured': settings.get('isSuperAdminConfigured', False)
                })
        except FileNotFoundError:
            return jsonify({'error': 'app_settings.json not found'}), 404
        except json.JSONDecodeError:
            return jsonify({'error': 'Error decoding JSON'}), 500

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