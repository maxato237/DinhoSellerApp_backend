from sqlalchemy.orm import Session
from dinhoseller.manage_invoices.model import Invoice_line
from dinhoseller.manage_stock.model import Stock


def process_invoice_line(invoice_line: Invoice_line, db_session: Session):

    designation = invoice_line.designation.strip().lower()

    stock_item = db_session.query(Stock).filter(Stock.name.ilike(designation)).first()

    if not stock_item:
        return {
            'success': False,
            'error': f"Produit '{invoice_line.designation}' introuvable dans le stock."
        }

    if invoice_line.quantity > stock_item.quantity:
        return {
            'success': False,
            'error': f"Stock insuffisant pour '{stock_item.name}': demandé={invoice_line.quantity}, disponible={stock_item.quantity}."
        }

    # Mise à jour du stock
    stock_item.quantity -= invoice_line.quantity
    return {
        'success': True,
        'message': f"Stock mis à jour pour '{stock_item.name}': -{invoice_line.quantity} (reste: {stock_item.quantity})"
    }
