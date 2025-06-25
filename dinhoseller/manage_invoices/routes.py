from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from dinhoseller import db
from dinhoseller.manage_invoices.model import Invoice, Invoice_line
from dateutil.parser import isoparse
from sqlalchemy.exc import SQLAlchemyError

invoice_bp = Blueprint('invoice_bp', __name__)


@invoice_bp.route('/add', methods=['POST'])
@jwt_required()
def create_invoice():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['status', 'HT', 'client', 'lignes']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        date_added = isoparse(data['dateAdded']) if 'dateAdded' in data else datetime.utcnow()
        echeance = datetime.strptime(data['echeance'], "%Y-%m-%d") if data.get('echeance') else None
        decodeToken = get_jwt()

        with db.session.begin():
            invoice = Invoice(
                status=data['status']['name'],
                TVA=data.get('TVA'),
                HT=data.get('HT'),
                TTC=data.get('TTC'),
                ECOMP=data.get('ECOMP'),
                PRECOMPTE=data.get('PRECOMPTE'),
                avance=data.get('avance'),
                echeance=echeance,
                client_id=data['client']['id'],
                user_id=int(decodeToken.get("sub")),
                dateAdded=date_added,
            )
            
            invoice.code_facture = invoice.generate_invoice_code()
            db.session.add(invoice)
            db.session.flush()

            for ligne in data['lignes']:
                if not ligne.get('DESIGNATION'):
                    continue

                invoice_line = Invoice_line(
                    designation=ligne['DESIGNATION']['name'],
                    quantity=ligne.get('QUANTITY'),
                    PUH=ligne.get('PUH'),
                    PTH=ligne.get('PTH'),
                    PVC=ligne.get('PVC'),
                    PUTTC=ligne.get('PUTTC'),
                    PTTTC=ligne.get('PTTTC'),
                    invoice_id=invoice.num
                )
                db.session.add(invoice_line)
            db.session.commit()
        return jsonify( {'message': invoice.to_dict()} ), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur de base de données'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur inattendue'}), 500



@invoice_bp.route('/code', methods=['GET'])
@jwt_required()
def get_invoice_code():
    try:
        date_facture = datetime.utcnow()
        prefix = f"{date_facture.year}{date_facture.month:02d}FAC"
        
        dernier = (
            Invoice.query
            .filter(Invoice.code_facture.startswith(prefix))
            .order_by(Invoice.num.desc())
            .first()
        )

        if not dernier:
            numero_facture = 1
        else:
            numero_facture = int(dernier.code_facture.split("-")[-1]) + 1

        print(f"{prefix}{numero_facture}")

        return jsonify({'message': f"{prefix}{numero_facture}"}), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inattendue'}), 500


# Get All Invoices
@invoice_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_invoices():
    try:
        invoices = Invoice.query.all()
        if not invoices:
            return jsonify({'message': 'No invoices found'}), 404
        return jsonify([invoice.to_dict() for invoice in invoices]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get Invoice by ID
@invoice_bp.route('/invoices/<int:invoice_num>', methods=['GET'])
def get_invoice(invoice_num):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        return jsonify(invoice.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Update Invoice
@invoice_bp.route('/invoices/<int:invoice_num>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_num):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['type', 'status', 'TVA', 'HT', 'TTC']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        invoice.type = data.get('type', invoice.type)
        invoice.status = data.get('status', invoice.status)
        invoice.TVA = data.get('TVA', invoice.TVA)
        invoice.HT = data.get('HT', invoice.HT)
        invoice.TTC = data.get('TTC', invoice.TTC)
        invoice.ECOMP = data.get('ECOMP', invoice.ECOMP)
        invoice.avance = data.get('avance', invoice.avance)
        invoice.echeance = data.get('echeance', invoice.echeance)
        invoice.client_id = data.get('client_id', invoice.client_id)
        invoice.user_id = data.get('user_id', invoice.user_id)

        db.session.commit()
        return jsonify(invoice.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Delete Invoice
@invoice_bp.route('/invoices/<int:invoice_num>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_num):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'message': 'Invoice deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Create Invoice Line
@invoice_bp.route('/invoices/<int:invoice_num>/lines', methods=['POST'])
@jwt_required()
def create_invoice_line(invoice_num):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404

        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = ['designation', 'PUTTC', 'PTH', 'PVC']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        invoice_line = Invoice_line(
            designation=data.get('designation'),
            PUTTC=data.get('PUTTC'),
            PTH=data.get('PTH'),
            PVC=data.get('PVC'),
            invoice_id=invoice_num
        )

        db.session.add(invoice_line)
        db.session.commit()

        invoice.invoice_lines.append(invoice_line)
        db.session.commit()
        
        return jsonify(invoice_line.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Get All Lines for a Specific Invoice
@invoice_bp.route('/invoices/<int:invoice_num>/lines', methods=['GET'])
@jwt_required()
def get_invoice_lines(invoice_num):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        lines = invoice.invoice_lines
        return jsonify([line.to_dict() for line in lines]), 200
    except Exception as e:
        return jsonify({'error': 'Erreur inatendu'}), 500

# Update Invoice Line
@invoice_bp.route('/invoices/<int:invoice_num>/lines/<int:line_id>', methods=['PUT'])
@jwt_required()
def update_invoice_line(invoice_num, line_id):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404

        line = Invoice_line.query.get(line_id)
        if not line:
            return jsonify({'error': 'Line not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        line.designation = data.get('designation', line.designation)
        line.PUTTC = data.get('PUTTC', line.PUTTC)
        line.PTH = data.get('PTH', line.PTH)
        line.PVC = data.get('PVC', line.PVC)

        db.session.commit()
        return jsonify(line.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500

# Delete Invoice Line
@invoice_bp.route('/invoices/<int:invoice_num>/lines/<int:line_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice_line(invoice_num, line_id):
    try:
        invoice = Invoice.query.get(invoice_num)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404

        line = Invoice_line.query.get(line_id)
        if not line:
            return jsonify({'error': 'Line not found'}), 404
        
        db.session.delete(line)
        db.session.commit()
        return jsonify({'message': 'Invoice line deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erreur inatendu'}), 500
