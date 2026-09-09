import tempfile

from app.models import Bill, BillItem, Product
from app.db import db
from app.utils import generate_bill_pdf
import os

def create_bill(data):
    items = data.get("items")
    payment_method = data.get("payment_method")
    customer_name = data.get("customer_name")
    customer_phone = data.get("phone") or data.get("customer_phone")

    subtotal = 0
    bill_items = []

    for item in items:
        product = Product.query.get(item["product_id"])

        if not product:
            return {"message": f"Product not found"}, 404

        if product.quantity < item["quantity"]:
            return {"message": f"Not enough stock for {product.name}"}, 400

        quantity = item["quantity"]
        selling_price = product.selling_price
        cost_price = product.cost_price
        total_price = selling_price * quantity
        subtotal += total_price

        product.quantity -= quantity

        bill_item = BillItem(
            product_id=product.id,
            product_name=product.name,
            category=product.category,
            quantity=quantity,
            cost_price=cost_price,
            selling_price=selling_price,
            total_price=total_price
        )
        bill_items.append(bill_item)

    tax = subtotal * 0.05
    discount = data.get("discount", 0)
    total_amount = subtotal + tax - discount

    bill = Bill(
        subtotal=subtotal,
        tax_amount=tax,
        discount=discount,
        total_amount=total_amount,
        payment_method=payment_method,
        customer_name=customer_name,
        customer_phone=customer_phone
    )

    db.session.add(bill)
    db.session.flush()

    for item in bill_items:
        item.bill_id = bill.id
        db.session.add(item)

    db.session.commit()

    return {
        "message": "Bill created successfully",
        "bill_id": bill.id,
        "total": total_amount
    }


def get_all_bills():
    bills = Bill.query.order_by(Bill.created_at.desc()).all()
    result = []
    for bill in bills:
        bill_data = {
            "bill_id": bill.id,
            "subtotal": bill.subtotal,
            "tax": bill.tax_amount,
            "discount": bill.discount,
            "total_amount": bill.total_amount,
            "payment_method": bill.payment_method,
            "customer_name": bill.customer_name,
            "customer_phone": bill.customer_phone,
            "created_at": bill.created_at,
            "items": []
        }
        for item in bill.items:
            bill_data["items"].append({
                "product_id": item.product_id,
                "product_name": item.product_name,
                "category": item.category,
                "quantity": item.quantity,
                "selling_price": item.selling_price,
                "total_price": item.total_price
            })
        result.append(bill_data)
    return result


# ✅ NEW — fetch bill from DB and generate real PDF
def generate_pdf_for_bill(bill_id):
    bill = Bill.query.get(bill_id)

    if not bill:
        return {"error": "Bill not found"}

    # ✅ Build bill_data from real DB record
    bill_data = {
        "bill_no": f"BILL-{str(bill.id).zfill(4)}",
        "customer": bill.customer_name or "Walk-in",
        "phone": bill.customer_phone or "—",
        "payment_method": bill.payment_method or "Cash",
        "subtotal": bill.subtotal,
        "tax": bill.tax_amount,
        "discount": bill.discount,
        "total": bill.total_amount,
        "created_at": bill.created_at.strftime("%d %b %Y, %H:%M") if bill.created_at else "—",
        "items": [
            {
                "name": item.product_name,
                "qty": item.quantity,
                "price": item.selling_price,
            }
            for item in bill.items
        ]
    }

    # ✅ Save to temp path
    path = os.path.join(tempfile.gettempdir(), f"bill_{bill_id}.pdf")
    generate_bill_pdf(path, bill_data)
    return path