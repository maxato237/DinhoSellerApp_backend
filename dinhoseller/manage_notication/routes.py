from flask import Blueprint, request, jsonify
from dinhoseller import db

notication_bp = Blueprint('notication_bp', __name__)
