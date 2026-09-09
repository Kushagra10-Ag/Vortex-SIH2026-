from app.services import billing_service

def create_bill(data):
    return billing_service.create_bill(data)

def get_all_bills():
    return billing_service.get_all_bills()

# ✅ NEW
def get_bill_pdf(bill_id):
    return billing_service.generate_pdf_for_bill(bill_id)