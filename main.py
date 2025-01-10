import json
import logging
from datetime import date, datetime
from decimal import Decimal
from http.server import HTTPServer, BaseHTTPRequestHandler
import mysql.connector
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Secure database configuration
DB_CONF = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'dipakroot'),
    'database': os.getenv('DB_NAME', 'train_system'),
}

def get_db_connection():
    """Establish a database connection."""
    return mysql.connector.connect(**DB_CONF)

def date_converter(obj):
    """Convert date and decimal objects for JSON serialization."""
    if isinstance(obj, (datetime, date)):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# Allowed tables and their primary key mappings
ALLOWED_TABLES = {
    "bookings": "booking_id",
    "cancellations": "cancellation_id",
    "passengers": "passenger_id",
    "paymentrecords": "payment_id",
    "reviews": "review_id",
    "stations": "station_id",
    "ticketprices": "price_id",
    "trainclasses": "class_id",
    "trains": "train_id",
    "trainschedules": "schedule_id",
}

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        conn, cursor = None, None
        try:
            # Parse the path to determine the table
            path_parts = self.path.strip("/").split("/")
            if len(path_parts) != 1 or path_parts[0] not in ALLOWED_TABLES:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid table name"}).encode())
                return

            table_name = path_parts[0]

            # Parse the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            # Construct the SQL query dynamically
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            values = tuple(data.values())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # Execute the query
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()

            # Respond with the inserted record ID
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Record inserted", "id": cursor.lastrowid}).encode())

        except mysql.connector.Error as e:
            logging.error(f"MySQL error: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Database error: {str(e)}"}).encode())
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Server error: {str(e)}"}).encode())
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def do_GET(self):
        conn, cursor = None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Parse path to identify the table and optional record ID
            path_parts = self.path.strip("/").split("/")
            if len(path_parts) < 1 or path_parts[0] not in ALLOWED_TABLES:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid table name"}).encode())
                return

            table_name = path_parts[0]
            primary_key = ALLOWED_TABLES[table_name]

            if len(path_parts) == 2:
                # Query a specific record by its primary key
                record_id = path_parts[1]
                cursor.execute(f"SELECT * FROM {table_name} WHERE {primary_key} = %s", (record_id,))
                result = cursor.fetchone()

                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(result, default=date_converter).encode())
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"{table_name[:-1].capitalize()} not found"}).encode())
            else:
                # Query all records from the table
                cursor.execute(f"SELECT * FROM {table_name}")
                result = cursor.fetchall()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result, default=date_converter).encode())

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}", exc_info=True)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Server error: {str(e)}"}).encode())
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    """Start the HTTP server."""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
