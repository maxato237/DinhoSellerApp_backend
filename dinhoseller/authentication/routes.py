# from datetime import datetime, timedelta
from datetime import datetime, timedelta
import random
import string
from flask import Blueprint, jsonify, request
import jwt

from dinhoseller.config import Config
from dinhoseller.manage_user.model import User
from dinhoseller import db
from dinhoseller.manage_session.model import Session
from dinhoseller.manage_user.model import User
from werkzeug.security import generate_password_hash,check_password_hash
# import jwt

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    # try:
        data = request.form

        # Vérification de la présence du nom d'utilisateur et du mot de passe
        phone = data['phone']
        password = data['password']
        rememberme = data['rememberme']
        if not phone or not password:
            return jsonify({'message' :'Veillez bien saisir les données '})

        # Vérification si l'utilisateur existe
        user = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({'message' :'Utilisateur introuvable'}), 404
            

        # Vérification du mot de passe
        if not check_password_hash(user.password, password):
            return jsonify({'message' :'Utilisateur introuvable'}),400

    
        if(rememberme):
            token = month_refresh_token(phone)
        else:
            token = generate_token(phone)

        user_agent = request.user_agent.string
        usersession = Session.query.filter_by(user_id = user.id, user_agent = user_agent ).first()
        if(usersession):
            usersession.token = token
            db.session.add(usersession)
            db.session.commit()
        else:
            new_session = Session(
                user_id = user.id,
                token = token,
                ip_address = request.remote_addr,
                user_agent = user_agent,
            )

            db.session.add(new_session)
            db.session.commit()

        return jsonify({'token': token}), 200
    # except Exception as e:
    #     return jsonify({'message': 'An error occurred.', 'error': str(e)}), 500

@auth.route('/logout', methods=['POST'])
def logout():
    # implémentation la logique de déconnexion, comme la suppression de la session utilisateur
    return jsonify({'message': 'Logout successful.'}), 200

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
      'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(token_payload, Config.SECRET_JWT_KEY, algorithm='HS256')
    return token

def month_refresh_token(phone):
    token_payload = {
      'phone': phone,
      'exp': datetime.utcnow() + timedelta(days=30)
    }
    token = jwt.encode(token_payload, Config.SECRET_JWT_KEY, algorithm='HS256')
    return token

def generer_code_pin():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def generate_token(phone):
    token_payload = {
      'phone': phone,
      'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(token_payload,  Config.SECRET_JWT_KEY, algorithm='HS256')

    return token

def generate_random_string():
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choice(characters) for _ in range(8))
    return random_string