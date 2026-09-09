from app.models import Product
from app.db import db

def add_product(data):
    product = Product(
        name=data.get("name"),
        category=data.get("category"),
        brand=data.get("brand"),
        cost_price=data.get("cost_price"),
        selling_price=data.get("selling_price"),
        quantity=data.get("quantity"),
        min_stock_level=data.get("min_stock_level", 5),
        expiry_date=data.get("expiry_date"),
        batch_number=data.get("batch_number")
    )

    db.session.add(product)
    db.session.commit()

    return {"message": "Product added successfully"}


def get_all_products():
    products = Product.query.all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "brand": p.brand,
            "cost_price": float(p.cost_price or 0),
            "selling_price": float(p.selling_price or 0),
            "quantity": p.quantity or 0,
            "min_stock_level": p.min_stock_level or 5,
            "expiry_date": str(p.expiry_date) if p.expiry_date else "",
            "batch_number": p.batch_number or ""
        }
        for p in products
    ]
def update_product(product_id, data):
    product = Product.query.get(product_id)

    if not product:
        return {"error": "Product not found"}, 404

    # 🔥 update fields
    product.name = data.get("name", product.name)
    product.category = data.get("category", product.category)
    product.brand = data.get("brand", product.brand)
    product.cost_price = data.get("cost_price", product.cost_price)
    product.selling_price = data.get("selling_price", product.selling_price)
    product.quantity = data.get("quantity", product.quantity)
    product.min_stock_level = data.get("min_stock_level", product.min_stock_level)
    product.expiry_date = data.get("expiry_date", product.expiry_date)
    product.batch_number = data.get("batch_number", product.batch_number)

    db.session.commit()

    return {
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "brand": product.brand,
            "cost_price": float(product.cost_price or 0),
            "selling_price": float(product.selling_price or 0),
            "quantity": product.quantity or 0,
            "min_stock_level": product.min_stock_level or 5,
            "expiry_date": str(product.expiry_date) if product.expiry_date else "",
            "batch_number": product.batch_number or ""
        }
    }
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return {"error": "Product not found"}, 404

    db.session.delete(product)
    db.session.commit()

    return {"message": "Product deleted successfully"}