from app.repositories.mongodb.product_repository import ProductRepository
from app.repositories.sqlserver.sales_repository import SalesRepository
from app.schemas.analytics_schema import IndicatorResponse


class ProductService:

    def __init__(self):
        self.sales_repository = SalesRepository()
        self.product_repository = ProductRepository()

    def get_top_product_month(self):
        sales_by_product = self.sales_repository.get_top_products()

        for sales_data in sales_by_product:
            product = self.product_repository.get_product_by_id(
                sales_data["product_id"]
            )

            if not product:
                continue

            data = {
                "product_id": sales_data["product_id"],
                "product": product.get("name"),
                "category": product.get("category"),
                "quantity": sales_data["quantity"],
                "month": sales_data["month"]
            }

            return IndicatorResponse(
                indicator="top_product_month",
                title=(
                    "Producto con más ventas con ficha en catálogo "
                    f"de {sales_data['month']}"
                ),
                chart_type="card",
                data=data,
                sources=["SQL Server", "MongoDB"]
            )

        return None
