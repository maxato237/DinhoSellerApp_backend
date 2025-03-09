from flask import Blueprint, request, jsonify
from dinhoseller import db

session_bp = Blueprint('session_bp', __name__)
