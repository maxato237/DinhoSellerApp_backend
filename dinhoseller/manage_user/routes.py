import re
from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_user.model import User, UserDetails
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user_bp', __name__)

# Create User
@user_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['lastname', 'firstname', 'phone', 'role_id','password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Validation du format du numéro de téléphone (exemple de format : +1234567890)
        phone_regex = r'^\+\d{8,15}$'
        if 'phone' in data and not re.match(phone_regex, data['phone']):
            return jsonify({'message': 'Invalid phone number format.'}), 400

        # Vérification si l'utilisateur existe déjà
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
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get All Users
@user_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        if not users:
            return jsonify({'message': 'No users found'}), 404
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get User by ID
@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update User
@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['lastname', 'firstname', 'phone', 'role_id']
        missing_fields = [field for field in required_fields if field not in data and getattr(user, field, None) is None]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        user.lastname = data.get('lastname', user.lastname)
        user.firstname = data.get('firstname', user.firstname)
        user.phone = data.get('phone', user.phone)
        user.role_id = data.get('role_id', user.role_id)
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete User
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@user_bp.route('/userdetails', methods=['POST'])
def create_user_details():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        user_details = UserDetails(
            date_of_birth=data.get('date_of_birth'),
            genre=data.get('genre'),
            address=data.get('address'),
            country=data.get('country'),
            city=data.get('city'),
            personnal_mail_address=data.get('personnal_mail_address'),
            address_mail=data.get('address_mail'),
            poste=data.get('poste'),
            start_date_of_hire=data.get('start_date_of_hire'),
            contract_type=data.get('contract_type'),
            salary=data.get('salary'),
            group=data.get('group'),
            department=data.get('department'),
            user_id=user_id
        )
        
        db.session.add(user_details)
        db.session.commit()
        return jsonify(user_details.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get UserDetails by User ID
@user_bp.route('/userdetails/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    try:
        user_details = UserDetails.query.filter_by(user_id=user_id).first()
        if not user_details:
            return jsonify({'error': 'User details not found'}), 404
        return jsonify(user_details.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update UserDetails
@user_bp.route('/userdetails/<int:user_id>', methods=['PUT'])
def update_user_details(user_id):
    try:
        user_details = UserDetails.query.filter_by(user_id=user_id).first()
        if not user_details:
            return jsonify({'error': 'User details not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        user_details.date_of_birth = data.get('date_of_birth', user_details.date_of_birth)
        user_details.genre = data.get('genre', user_details.genre)
        user_details.address = data.get('address', user_details.address)
        user_details.country = data.get('country', user_details.country)
        user_details.city = data.get('city', user_details.city)
        user_details.personnal_mail_address = data.get('personnal_mail_address', user_details.personnal_mail_address)
        user_details.address_mail = data.get('address_mail', user_details.address_mail)
        user_details.poste = data.get('poste', user_details.poste)
        user_details.start_date_of_hire = data.get('start_date_of_hire', user_details.start_date_of_hire)
        user_details.contract_type = data.get('contract_type', user_details.contract_type)
        user_details.salary = data.get('salary', user_details.salary)
        user_details.group = data.get('group', user_details.group)
        user_details.department = data.get('department', user_details.department)
        
        db.session.commit()
        return jsonify(user_details.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Delete UserDetails
@user_bp.route('/userdetails/<int:user_id>', methods=['DELETE'])
def delete_user_details(user_id):
    try:
        user_details = UserDetails.query.filter_by(user_id=user_id).first()
        if not user_details:
            return jsonify({'error': 'User details not found'}), 404
        
        db.session.delete(user_details)
        db.session.commit()
        return jsonify({'message': 'User details deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500