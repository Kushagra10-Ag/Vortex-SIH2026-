from app.services import inventory_service

def add_product(data):
    return inventory_service.add_product(data)

def get_products():
    return inventory_service.get_all_products()
def update_product(product_id, data):
    return inventory_service.update_product(product_id, data)
def delete_product(product_id):
    return inventory_service.delete_product(product_id)
