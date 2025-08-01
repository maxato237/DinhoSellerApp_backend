from datetime import datetime
import os
import re
from flask import Blueprint, json, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_session.model import Session
from dinhoseller.manage_user.model import User, UserDetails
from werkzeug.security import generate_password_hash
from dateutil.parser import isoparse

user_bp = Blueprint('user_bp', __name__)

# Create User
@user_bp.route('/create', methods=['POST'])
def create_user():
    try:
        data = request.form
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        required_fields = ['lastname', 'firstname', 'phone', 'role_id','password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        phone_regex = r'^\d{8,15}$'
        if 'phone' in data and not re.match(phone_regex, data['phone']):
            return jsonify({'message': 'Invalid phone number format.'}), 400
        existing_phone = User.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            return jsonify({'message': 'This user already exists.'}), 409
        hashed_password = generate_password_hash(data.get('password'), method='pbkdf2:sha256', salt_length=8)

        user = User(
            lastname=data['lastname'],
            firstname=data['firstname'],
            phone=data['phone'],
            role_id=data['role_id'],
            password=hashed_password
        )
        
        db.session.add(user)
        db.session.flush()

        new_user_details = UserDetails(
            user_id=user.id,
            date_of_birth=None,
            genre=None,
            address=None,
            country=None,
            city=None,
            personnal_mail_address=None,
            address_mail=data.get('email'),
            post=None,
            start_date_of_hire=None,
            contract_type=None,
            salary=None,
            department=None,
        )

        db.session.add(new_user_details)
        db.session.commit()

        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

@jwt_required()
@user_bp.route('/addemployee', methods=['POST'])
def add_employee():
    try:
        data = request.get_json()

        # Vérification des champs obligatoires
        required_fields = ["lastname", "firstname", "phone", "role_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Le champ {field} est requis"}), 400

        # Vérifier si l'utilisateur existe déjà avec le même téléphone ou e-mails
        existing_user = User.query.filter(User.phone == data.get('phone')).first()
        existing_details = UserDetails.query.filter(
            (UserDetails.personnal_mail_address == data.get('personnal_mail_address')) |
            (UserDetails.address_mail == data.get('address_mail'))
        ).first()

        if existing_user:
            return jsonify({"error": "Un utilisateur avec ce numéro de téléphone existe déjà"}), 409
        if existing_details:
            return jsonify({"error": "Un utilisateur avec cette adresse e-mail existe déjà"}), 409

        # Hachage du mot de passe
        hashed_password = generate_password_hash("Drinh0access#", method='pbkdf2:sha256', salt_length=8)

        # Création de l'utilisateur
        new_user = User(
            lastname=data["lastname"],
            firstname=data["firstname"],
            phone=data["phone"],
            password=hashed_password,
            role_id=data["role_id"]['code']
        )
        db.session.add(new_user)
        db.session.flush()
     
        new_user_details = UserDetails(
            user_id=new_user.id,
            date_of_birth = isoparse(data["date_of_birth"]) if "date_of_birth" in data and data["date_of_birth"] else None,
            genre = data["genre"]["name"] if "genre" in data and isinstance(data["genre"], dict) else None,
            address = data.get("address"),
            country = data["country"]["name"] if "country" in data and isinstance(data["country"], dict) else None,
            city = data.get("city"),
            personnal_mail_address = data.get("personnal_mail_address"),
            address_mail = data.get("address_mail"),
            post = data.get("post"),
            start_date_of_hire = isoparse(data["start_date_of_hire"]) if "start_date_of_hire" in data and data["start_date_of_hire"] else None,
            contract_type = data["contract_type"]["name"] if "contract_type" in data and isinstance(data["contract_type"], dict) else None,
            salary = data.get("salary"),
            department = data["department"]["name"] if "department" in data and isinstance(data["department"], dict) else None,
        )
        db.session.add(new_user_details)
        db.session.commit()

        return jsonify({"message": "Employé enregistré avec succès"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500


@user_bp.route('/all', methods=['GET'])
@jwt_required()
def get_users():
    try:
        decodeToken = get_jwt()
        user_id = int(decodeToken.get("sub"))
        users = User.query.filter(User.is_active == True, User.id != user_id).all()
        if not users:
            return jsonify({'error': 'Aucun employés trouvés'}), 404
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inattendue'}), 500

@user_bp.route('/userById/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500
    
@user_bp.route('/accountDetails', methods=['GET'])
@jwt_required()
def my_account_details():
    try:
        decodeToken = get_jwt()
        user = User.query.get(decodeToken.get("sub"))
        if not user:
            print('go')
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

@user_bp.route('/updatemydetails', methods=['PUT'])
@jwt_required()
def update_my_details():
    try:
        user_id = get_jwt().get("sub")
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Veuillez remplir les champs obligatoires'}), 400

        required_fields = ['lastname', 'firstname', 'phone', 'role_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        # Vérifier duplication du numéro de téléphone
        existing_user = User.query.filter(User.phone == data.get('phone'), User.id != user.id).first()
        if existing_user:
            return jsonify({"error": "Un autre utilisateur avec ce numéro de téléphone existe déjà"}), 400

        # Vérifier duplication des adresses mail
        existing_details = UserDetails.query.filter(
            ((UserDetails.personnal_mail_address == data.get('personnal_mail_address')) |
             (UserDetails.address_mail == data.get('address_mail'))),
            UserDetails.user_id != user.id
        ).first()
        if existing_details:
            return jsonify({"error": "Un autre utilisateur avec cette adresse e-mail existe déjà"}), 400

        # Mise à jour de l'utilisateur
        user.lastname = data['lastname']
        user.firstname = data['firstname']
        user.phone = data['phone']
        user.role_id = data['role_id']['code'] if isinstance(data['role_id'], dict) else data['role_id']

        # Récupérer ou créer les détails utilisateur
        details = UserDetails.query.filter_by(user_id=user.id).first()
        if not details:
            details = UserDetails(user_id=user.id)
            db.session.add(details)

        # Mise à jour conditionnelle des champs UserDetails
        if 'date_of_birth' in data and data['date_of_birth']:
            details.date_of_birth = isoparse(data['date_of_birth']).date()
        if 'genre' in data:
            details.genre = data['genre']['name'] if isinstance(data['genre'], dict) else data['genre']
        if 'address' in data:
            details.address = data['address']
        if 'country' in data:
            details.country = data['country']['name'] if isinstance(data['country'], dict) else data['country']
        if 'city' in data:
            details.city = data['city']
        if 'personnal_mail_address' in data:
            details.personnal_mail_address = data['personnal_mail_address']
        if 'address_mail' in data:
            details.address_mail = data['address_mail']

        db.session.commit()
        return jsonify(user.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erreur lors de la mise à jour : {e}")
        return jsonify({'error': 'Erreur inattendue lors de la mise à jour'}), 500

@jwt_required()
@user_bp.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Employé introuvable'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Veuillez remplir les champs obligatoires'}), 400

        required_fields = ['lastname', 'firstname', 'phone', 'role_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        # Vérification duplication numéro ou email
        existing_user = User.query.filter(User.phone == data.get('phone'), User.id != user.id).first()
        existing_details = UserDetails.query.filter(
            ((UserDetails.personnal_mail_address == data.get('personnal_mail_address')) |
             (UserDetails.address_mail == data.get('address_mail'))),
            UserDetails.user_id != user.id
        ).first()
        if existing_user:
            return jsonify({"error": "Un autre utilisateur avec ce numéro de téléphone existe déjà"}), 400
        if existing_details:
            return jsonify({"error": "Un autre utilisateur avec cette adresse e-mail existe déjà"}), 400

        # Mise à jour des données User
        user.lastname = data['lastname']
        user.firstname = data['firstname']
        user.phone = data['phone']
        user.role_id = data['role_id']['code'] if isinstance(data['role_id'], dict) else data['role_id']

        details = UserDetails.query.filter_by(user_id=user.id).first()
        if not details:
            return jsonify({'error': 'Les détails de l\'utilisateur sont introuvables'}), 404

        # Mise à jour conditionnelle des détails
        if 'date_of_birth' in data and data['date_of_birth']:
            details.date_of_birth = isoparse(data['date_of_birth']).date()
        if 'genre' in data:
            details.genre = data['genre']['name'] if isinstance(data['genre'], dict) else data['genre']
        if 'address' in data:
            details.address = data['address']
        if 'country' in data:
            details.country = data['country']['name'] if isinstance(data['country'], dict) else data['country']
        if 'city' in data:
            details.city = data['city']
        if 'personnal_mail_address' in data:
            details.personnal_mail_address = data['personnal_mail_address']
        if 'address_mail' in data:
            details.address_mail = data['address_mail']
        if 'post' in data:
            details.post = data['post']
        if 'start_date_of_hire' in data and data['start_date_of_hire']:
            details.start_date_of_hire = isoparse(data['start_date_of_hire']).date()
        if 'contract_type' in data:
            details.contract_type = data['contract_type']['name'] if isinstance(data['contract_type'], dict) else data['contract_type']
        if 'salary' in data:
            details.salary = float(data['salary']) if data['salary'] is not None else None
        if 'group' in data:
            details.group = data['group']
        if 'department' in data:
            details.department = data['department']['name'] if isinstance(data['department'], dict) else data['department']

        db.session.commit()
        return jsonify(user.to_dict()), 200

    # except Exception as e:
    #     db.session.rollback()
    #     print(f"Erreur lors de la mise à jour : {e}")
    #     return jsonify({'error': 'Erreur inattendue lors de la mise à jour'}), 500


@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:  
        # Récupérer l'utilisateur
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Marquer l'utilisateur comme inactif
        user.is_active = False
        user.deleted_at = datetime.utcnow()

        # Désactiver toutes les sessions associées à l'utilisateur
        sessions = Session.query.filter_by(user_id=user_id).all()
        for session in sessions:
            session.is_active = False  # Désactiver la session

        db.session.commit()  # Sauvegarder les changements
        return jsonify({'message': 'User deleted successfully, all sessions deactivated'}), 200
    except Exception as e:
        db.session.rollback()  # Annuler la transaction en cas d'erreur
        return jsonify({'error': 'Erreur inattendue', 'details': str(e)}), 500
