# from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
# from dinhoseller import db
# from dinhoseller.manage_session.model import Session
# from dinhoseller.manage_user.model import User
# from werkzeug.security import check_password_hash
# from werkzeug.security import generate_password_hash
# import jwt

auth = Blueprint('auth', __name__)


# # @auth.route('/login', methods=['POST'])
# # def login():
# #     try:
# #         data = request.form

# #         # Vérification de la présence du nom d'utilisateur et du mot de passe
# #         username = data['username']
# #         password = data['password']
# #         rememberme = data['rememberme']
# #         if not username or not password:
# #             return jsonify({'message' :'Username and password are required.'})

# #         # Vérification si l'utilisateur existe
# #         user = User.query.filter_by(email=username).first()
# #         if not user:
# #             return jsonify({'message' :'User not found.'}), 404
            

# #         # Vérification du mot de passe
# #         if not check_password_hash(user.password, password):
# #             return jsonify({'message' :'Incorrect password.'}),400

# #         # Authentification réussie
    
# #         if(rememberme):
# #             token = month_refresh_token(username)
# #         else:
# #             token = refresh_token(username)

# #         user_agent = request.user_agent.string
# #         usersession = Session.query.filter_by(user_id = user.id, user_agent = user_agent ).first()
# #         if(usersession):
# #             usersession.token = token
# #             db.session.add(usersession)
# #             db.session.commit()
# #         else:
# #             new_session = Session(
# #                 user_id = user.id,
# #                 token = token,
# #                 ip_address = request.remote_addr,
# #                 user_agent = user_agent,
# #             )

# #             db.session.add(new_session)
# #             db.session.commit()

# #         return jsonify({'email': username, 'username':user.username}), 200
# #     except Exception as e:
# #         return jsonify({'message': 'An error occurred.', 'error': str(e)}), 500

# # @auth.route('/logout', methods=['POST'])
# # def logout():
# #     # implémentation la logique de déconnexion, comme la suppression de la session utilisateur
# #     return jsonify({'message': 'Logout successful.'}), 200

# # @auth.route('/resetpassword/<email>', methods=['GET'])
# # def resetpassword(email):
# #     try:
# #         user = User.query.filter_by(email = email).first()
# #         if not user:
# #            return jsonify({"message":"User not found!"}),409
        
# #         password = generate_random_string()       
# #         hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

# #         user.password = hashed_password
# #         db.session.add(user)
# #         db.session.commit()
# #         reset_password_mail(email,password,mail)

# #         return jsonify({"message" : "Password reset"}),200

# #     except Exception as e:
# #         return jsonify({"message": "Processing errors"}),500


# # def refresh_token(email):
# #     token_payload = {
# #       'user_id': email,
# #       'exp': datetime.utcnow() + timedelta(hours=1)
# #     }
# #     token = jwt.encode(token_payload, Config.SECRET_JWT_KEY, algorithm='HS256')
# #     return token

# # def month_refresh_token(email):
# #     token_payload = {
# #       'user_id': email,
# #       'exp': datetime.utcnow() + timedelta(days=30)
# #     }
# #     token = jwt.encode(token_payload, Config.SECRET_JWT_KEY, algorithm='HS256')
# #     return token

# # def generer_code_pin():
# #     return ''.join([str(random.randint(0, 9)) for _ in range(8)])

# # def generate_token(email, codeping):
# #     token_payload = {
# #       'user_id': email,
# #       'codeping':codeping,
# #       'exp': datetime.utcnow() + timedelta(hours=1)
# #     }
# #     token = jwt.encode(token_payload,  Config.SECRET_JWT_KEY, algorithm='HS256')

# #     return token

# # def generate_random_string():
#     characters = string.ascii_letters + string.digits + string.punctuation
#     random_string = ''.join(random.choice(characters) for _ in range(8))
#     return random_string