from app.database.mongodb import get_database


class ProductRepository:

    def get_product_by_id(self, product_id):
        db = get_database()
        return db["products"].find_one({"product_id": product_id})
