from flask import Blueprint, jsonify
from app.services.analytics.sales_service import SalesService


sales_bp = Blueprint(
    "sales",
    __name__
)

service = SalesService()


@sales_bp.route(
    "/analytics/sales-total",
    methods=["GET"]
)
def sales_total():
    result = service.total_sales()

    return jsonify(result.__dict__)


@sales_bp.route(
    "/analytics/sales-by-region",
    methods=["GET"]
)
def sales_by_region():
    result = service.sales_by_region()

    return jsonify(result.__dict__)