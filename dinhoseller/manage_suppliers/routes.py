from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_clients.model import Client

supplier_bp = Blueprint('supplier_bp', __name__)
