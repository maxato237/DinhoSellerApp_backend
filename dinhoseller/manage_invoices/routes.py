from flask import Blueprint, request, jsonify
from dinhoseller import db
from dinhoseller.manage_clients.model import Client

invoice_bp = Blueprint('invoice_bp', __name__)
