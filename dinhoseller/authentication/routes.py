# from datetime import datetime, timedelta
from datetime import datetime, timedelta
import json
import os
import random
import string
import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
import jwt

from dinhoseller.config import Config
from dinhoseller.manage_user.model import User
from dinhoseller import db
from dinhoseller.manage_session.model import Session
from dinhoseller.manage_user.model import User
from werkzeug.security import generate_password_hash,check_password_hash
import os


auth = Blueprint('auth', __name__)
# Chemin absolu vers application.setting.json
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SETTINGS_FILE = os.path.join('dinhoseller','application.settings', 'application.setting.json')



@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.form

        # Vérification de la présence du téléphone et du mot de passe
        phone = data.get('phone')
        password = data.get('password')
        rememberme = data.get('rememberme')

        if not phone or not password:
            return jsonify({'message': 'Veuillez bien saisir les données.'}), 400

        # Vérification si l'utilisateur existe et s'il est actif
        user = User.query.filter_by(phone=phone, is_active=True).first()
        if not user:
            return jsonify({'message': 'Utilisateur introuvable ou compte désactivé.'}), 404

        # Vérification du mot de passe
        if not check_password_hash(user.password, password):
            return jsonify({'message': 'Mot de passe incorrect.'}), 400

        # Gérer le type de token en fonction du choix de l'utilisateur
        if rememberme == "true":
            token = month_refresh_token(user.id, user.role_id, user.firstname)
        else:
            token = generate_token(user.id, user.role_id, user.firstname)

        # Gestion de la session utilisateur
        user_agent = request.user_agent.string
        usersession = Session.query.filter_by(user_id=user.id, user_agent=user_agent).first()
        
        if usersession:
            usersession.token = token
            db.session.add(usersession)
        else:
            new_session = Session(
                user_id=user.id,
                token=token,
                ip_address=request.remote_addr,
                user_agent=user_agent,
            )
            db.session.add(new_session)
        
        # Commit de la session et du token
        db.session.commit()

        return jsonify({'token': token}), 200

    except Exception as e:
        return jsonify({'message': 'Une erreur est survenue.', 'error': str(e)}), 500

@auth.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logout successful.'}), 200

# Lire les paramètres
@auth.route('/all', methods=['GET'])
def get_settings():
    try:
        if not os.path.exists(SETTINGS_FILE):
            return jsonify({"error": f"Fichier non trouvé : {SETTINGS_FILE}"}), 500

        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data), 200

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Erreur JSON : {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Erreur interne : {str(e)}"}), 500

def parse_float(value, default=0.0):
    try:
        if isinstance(value, (float, int)):
            return float(value)
        value_str = str(value).replace(',', '.')
        return float(value_str)
    except (ValueError, TypeError):
        return default

# Modifier un ou plusieurs paramètres
@auth.route('/update', methods=['PUT'])
def update_settings():
    try:
        updates = request.json
        print(os.path.exists(SETTINGS_FILE))
        print(updates)
        # Charger les paramètres actuels
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        print(SETTINGS_FILE)

        # Champs nécessitant un traitement spécial
        percent_fields = ['TVA', 'PVC', 'BENEF', 'ECOMP', 'PRECOMPTE']

        for key, value in updates.items():
            if key in percent_fields:
                settings[key] = parse_float(value) / 100 if value is not None else 0.0
            else:
                settings[key] = value

        # Sauvegarder
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)

        return jsonify({"settings": settings}), 200

    except Exception as e:
        traceback.print_exc() 
        return jsonify({"error": f"Erreur interne : {str(e)}"}), 500
    
# @auth.route('/resetpassword/<phone>', methods=['GET'])
# def resetpassword(phone):
#     try:
#         user = User.query.filter_by(phone = phone).first()
#         if not user:
#            return jsonify({"message":"User not found!"}),409
        
#         password = generate_random_string()       
#         hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

#         user.password = hashed_password
#         db.session.add(user)
#         db.session.commit()
#         reset_password_mail(phone,password,mail)

#         return jsonify({"message" : "Password reset"}),200

#     except Exception as e:
#         return jsonify({"message": "Processing errors"}),500

def refresh_token(phone):
    token_payload = {
      'phone': phone,
      'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_payload, Config.SECRET_JWT_KEY, algorithm='HS256')
    return token

def month_refresh_token(id,role_id,firstname):
    claims = {
        "role_id": role_id,
        "firstname": firstname,
        "sub": str(id)
    }
    token = create_access_token(identity=str(id), additional_claims=claims, expires_delta=timedelta(days=30))
    return token

def generer_code_pin():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def generate_token(id,role_id,firstname):
    claims = {
        "role_id": role_id,
        "firstname": firstname,
        "sub": str(id)
    }
    token = create_access_token(identity=str(id), expires_delta=timedelta(days=30), additional_claims=claims)
    return token

def generate_random_string():
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(8))
    return random_string
