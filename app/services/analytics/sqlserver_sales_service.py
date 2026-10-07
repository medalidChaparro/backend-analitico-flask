from app.repositories.sqlserver.sales_repository import SalesRepository
from app.schemas.analytics_schema import IndicatorResponse


class SQLServerSalesService:

    def __init__(self):
        self.repository = SalesRepository()

    def total_sales(self):
        result = self.repository.get_total_sales()

        return IndicatorResponse(
            indicator="sales_total",
            title="Ventas Totales",
            chart_type="card",
            data=result,
            sources=[
                "SQL Server"
            ]
        )