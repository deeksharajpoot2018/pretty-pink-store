import mysql.connector
from datetime import datetime
from collections import defaultdict

class StoreBackend:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Root",
            database="clothingstore"
        )
        self.cursor = self.conn.cursor()

    def connect(self):
        # Ensures fresh connection for transactions
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Root",
            database="clothingstore"
        )

    def fetch_products(self):
        self.cursor.execute("SELECT product_id, product_name, product_price, product_qty, image_path FROM products")
        return self.cursor.fetchall()

    def record_sale(self, cart, total):
        conn = self.connect()
        cursor = conn.cursor()

        # Insert sale record
        cursor.execute("INSERT INTO salestotals (total_amount) VALUES (%s)", (total,))
        sale_id = cursor.lastrowid

        # Group cart items by product_id
        grouped_items = defaultdict(lambda: [None, 0, 0])  # [product_name, price, quantity]

        for product_id, product_name, product_price, quantity in cart:
            if grouped_items[product_id][0] is None:
                grouped_items[product_id] = [product_name, product_price, quantity]
            else:
                grouped_items[product_id][2] += quantity

        # Insert grouped items into salesitems and update stock
        for product_id, (name, price, qty) in grouped_items.items():
            cursor.execute(
                "INSERT INTO salesitems (sale_id, product_id, product_qty, product_price) VALUES (%s, %s, %s, %s)",
                (sale_id, product_id, qty, price)
            )

            cursor.execute(
                "UPDATE products SET product_qty = product_qty - %s WHERE product_id = %s AND product_qty >= %s",
                (qty, product_id, qty)
            )

        # Save to salestotals
        cursor.execute("INSERT INTO salestotals (sale_id, total) VALUES (%s, %s)", (sale_id, total))

        conn.commit()
        conn.close()
