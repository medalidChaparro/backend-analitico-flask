import unittest
from unittest.mock import Mock, patch

from flask import Flask

from app.repositories.mongodb.product_repository import ProductRepository
from app.repositories.sqlserver.sales_repository import SalesRepository
from app.routes.product_routes import products_bp, service
from app.schemas.analytics_schema import IndicatorResponse
from app.services.analytics.products_service import ProductService


class TopProductRepositoryTests(unittest.TestCase):

    @patch("app.repositories.sqlserver.sales_repository.get_sqlserver_connection")
    def test_get_top_products_ranks_products_in_latest_month_with_sales(self, get_connection):
        connection = Mock()
        connection.cursor.return_value.fetchall.return_value = [
            ("P001", 15, "2026-03"),
            ("P002", 9, "2026-03")
        ]
        get_connection.return_value = connection

        result = SalesRepository().get_top_products()

        self.assertEqual(
            result,
            [
                {"product_id": "P001", "quantity": 15, "month": "2026-03"},
                {"product_id": "P002", "quantity": 9, "month": "2026-03"}
            ]
        )
        query = connection.cursor.return_value.execute.call_args.args[0]
        self.assertIn("MAX(", query)
        self.assertIn("latest_month.month_start", query)
        self.assertIn("INNER JOIN sales_detail", query)
        self.assertIn("ORDER BY total_quantity DESC", query)
        connection.close.assert_called_once_with()

    @patch("app.repositories.sqlserver.sales_repository.get_sqlserver_connection")
    def test_get_top_products_returns_empty_list_when_there_are_no_sales(self, get_connection):
        connection = Mock()
        connection.cursor.return_value.fetchall.return_value = []
        get_connection.return_value = connection

        self.assertEqual(SalesRepository().get_top_products(), [])
        connection.close.assert_called_once_with()

    @patch("app.repositories.mongodb.product_repository.get_database")
    def test_get_product_by_id_queries_products_collection(self, get_database):
        product = {"product_id": "P001", "name": "Laptop"}
        collection = get_database.return_value.__getitem__.return_value
        collection.find_one.return_value = product

        result = ProductRepository().get_product_by_id("P001")

        self.assertIs(result, product)
        get_database.return_value.__getitem__.assert_called_once_with("products")
        collection.find_one.assert_called_once_with(
            {"product_id": "P001"}
        )


class TopProductServiceTests(unittest.TestCase):

    def test_get_top_product_month_combines_sales_and_product_data(self):
        product_service = ProductService()
        product_service.sales_repository.get_top_products = Mock(
            return_value=[{
                "product_id": "P001",
                "quantity": 15,
                "month": "2026-03"
            }]
        )
        product_service.product_repository.get_product_by_id = Mock(
            return_value={
                "product_id": "P001",
                "name": "Laptop",
                "category": "Electrónica"
            }
        )

        result = product_service.get_top_product_month()

        self.assertIsInstance(result, IndicatorResponse)
        self.assertEqual(result.indicator, "top_product_month")
        self.assertEqual(
            result.title,
            "Producto con más ventas con ficha en catálogo de 2026-03"
        )
        self.assertEqual(
            result.data,
            {
                "product_id": "P001",
                "product": "Laptop",
                "category": "Electrónica",
                "quantity": 15,
                "month": "2026-03"
            }
        )
        self.assertEqual(result.sources, ["SQL Server", "MongoDB"])

    def test_get_top_product_month_skips_products_missing_from_catalog(self):
        product_service = ProductService()
        product_service.sales_repository.get_top_products = Mock(
            return_value=[
                {
                    "product_id": "P004",
                    "quantity": 10,
                    "month": "2026-03"
                },
                {
                    "product_id": "P003",
                    "quantity": 6,
                    "month": "2026-03"
                }
            ]
        )
        product_service.product_repository.get_product_by_id = Mock(
            side_effect=[
                None,
                {
                    "product_id": "P003",
                    "name": "Laptop Dell 3",
                    "category": "Tablets"
                }
            ]
        )

        result = product_service.get_top_product_month()

        self.assertEqual(
            result.data,
            {
                "product_id": "P003",
                "product": "Laptop Dell 3",
                "category": "Tablets",
                "quantity": 6,
                "month": "2026-03"
            }
        )
        self.assertEqual(
            result.title,
            "Producto con más ventas con ficha en catálogo de 2026-03"
        )
        product_service.product_repository.get_product_by_id.assert_any_call(
            "P004"
        )
        product_service.product_repository.get_product_by_id.assert_any_call(
            "P003"
        )

    def test_get_top_product_month_returns_none_when_no_ranked_product_is_catalogued(self):
        product_service = ProductService()
        product_service.sales_repository.get_top_products = Mock(
            return_value=[{
                "product_id": "P001",
                "quantity": 15,
                "month": "2026-03"
            }]
        )
        product_service.product_repository.get_product_by_id = Mock(
            return_value=None
        )

        self.assertIsNone(product_service.get_top_product_month())


class TopProductRouteTests(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(products_bp)
        self.client = app.test_client()

    @patch.object(service, "get_top_product_month")
    def test_top_product_endpoint_returns_integrated_indicator(self, get_indicator):
        get_indicator.return_value = IndicatorResponse(
            indicator="top_product_month",
            title="Producto con más ventas con ficha en catálogo de 2026-03",
            chart_type="card",
            data={
                "product_id": "P001",
                "quantity": 15,
                "month": "2026-03"
            },
            sources=["SQL Server", "MongoDB"]
        )

        response = self.client.get("/analytics/top-product")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["indicator"], "top_product_month")

    @patch.object(service, "get_top_product_month", return_value=None)
    def test_top_product_endpoint_returns_404_without_data(self, get_indicator):
        response = self.client.get("/analytics/top-product")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(),
            {"message": "No se encontró información"}
        )
