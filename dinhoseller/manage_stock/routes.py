from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_clients.model import Client

stock_bp = Blueprint('stock_bp', __name__)
