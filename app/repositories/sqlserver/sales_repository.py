from app.database.sqlserver import get_sqlserver_connection


class SalesRepository:

    def get_total_sales(self):
        connection = get_sqlserver_connection()
        cursor = connection.cursor()

        query = """
        SELECT SUM(total_amount)
        FROM sales
        """

        cursor.execute(query)
        result = cursor.fetchone()

        connection.close()

        return result[0]

    def get_sales_by_region(self):
        connection = get_sqlserver_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            region,
            SUM(total_amount) AS sales
        FROM sales
        GROUP BY region
        """

        cursor.execute(query)
        results = cursor.fetchall()

        connection.close()

        return [
            {
                "region": row[0],
                "sales": row[1]
            }
            for row in results
        ]

    def get_top_products(self):
        connection = get_sqlserver_connection()

        try:
            cursor = connection.cursor()
            query = """
            WITH latest_month AS (
                SELECT MAX(
                    DATEFROMPARTS(YEAR(header.sale_date), MONTH(header.sale_date), 1)
                ) AS month_start
                FROM sales AS header
                INNER JOIN sales_detail AS detail
                    ON detail.sale_id = header.sale_id
            )
            SELECT
                detail.product_id,
                SUM(detail.quantity) AS total_quantity,
                CONVERT(char(7), latest_month.month_start, 126) AS month
            FROM sales_detail AS detail
            INNER JOIN sales AS header
                ON header.sale_id = detail.sale_id
            CROSS JOIN latest_month
            WHERE header.sale_date >= latest_month.month_start
                AND header.sale_date < DATEADD(MONTH, 1, latest_month.month_start)
            GROUP BY detail.product_id, latest_month.month_start
            ORDER BY total_quantity DESC, detail.product_id ASC
            """

            cursor.execute(query)
            results = cursor.fetchall()
        finally:
            connection.close()

        return [
            {
                "product_id": result[0],
                "quantity": result[1],
                "month": result[2]
            }
            for result in results
        ]