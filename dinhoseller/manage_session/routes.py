from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_session.model import Session
from dinhoseller.manage_session.utilities import is_valid_ip
from dinhoseller.manage_user.model import User

session_bp = Blueprint('session_bp', __name__)


@session_bp.route('/gettoken/<phone>', methods=['GET'])
def gettoken(phone):
  try:
    user = User.query.filter_by(phone = phone).first()
    session = Session.query.filter_by(user_id = user.id).first()
    return jsonify({"message": session.token}),200
  except Exception as e:
    return jsonify({"message" : e})


@session_bp.route('/create', methods=['POST'])
def create_session():
  data = request.form
    
  # Vérifier si toutes les données nécessaires sont fournies
  if 'user_id' not in data or 'token' not in data or 'ip_address' not in data or 'user_agent' not in data:
    return jsonify({'message': 'Toutes les données requises ne sont pas fournies'}), 400
  
  # Vérifier le format de l'adresse IP
  if not is_valid_ip(data['ip_address']):
    return jsonify({'message': 'Format d\'adresse IP invalide'}), 400
  
  # Créer une nouvelle session
  new_session = Session(
    user_id=data['user_id'],
    token=data['token'],
    ip_address=data['ip_address'],
    user_agent=data['user_agent']
  )
  
  # Ajouter la session à la base de données
  db.session.add(new_session)
  db.session.commit()
  
  return jsonify({'message': 'Session créée avec succès'}), 201