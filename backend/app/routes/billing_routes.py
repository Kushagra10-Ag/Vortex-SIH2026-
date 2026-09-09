from flask import Blueprint, request, jsonify, send_file
from app.controllers import billing_controller

billing_bp = Blueprint("billing", __name__)

@billing_bp.route("/create-bill", methods=["POST"])
def create_bill():
    data = request.get_json()
    result = billing_controller.create_bill(data)
    return jsonify(result)

@billing_bp.route("/bills", methods=["GET"])
def get_bills():
    result = billing_controller.get_all_bills()
    return jsonify(result)

# ✅ NEW — serves the actual PDF for a bill
@billing_bp.route("/bill-pdf/<int:bill_id>", methods=["GET"])
def get_bill_pdf(bill_id):
    result = billing_controller.get_bill_pdf(bill_id)
    if isinstance(result, dict):
        return jsonify(result), 404
    return send_file(result, mimetype="application/pdf", as_attachment=False)