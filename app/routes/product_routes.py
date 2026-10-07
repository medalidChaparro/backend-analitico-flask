from flask import Blueprint, jsonify

from app.services.analytics.products_service import ProductService


products_bp = Blueprint("products", __name__)
service = ProductService()


@products_bp.route("/analytics/top-product", methods=["GET"])
def top_product_month():
    result = service.get_top_product_month()

    if not result:
        return jsonify({"message": "No se encontró información"}), 404

    return jsonify(result.__dict__)
