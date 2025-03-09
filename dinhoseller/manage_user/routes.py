from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_clients.model import Client

user_bp = Blueprint('user_bp', __name__)
