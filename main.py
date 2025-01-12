from http.server import HTTPServer, BaseHTTPRequestHandler
import json
try:
    import mysql.connector
except ModuleNotFoundError:
    raise ImportError("The 'mysql-connector-python' package is not installed. Please install it using 'pip install mysql-connector-python'.")
from datetime import date, datetime
from decimal import Decimal

# MySQL database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "train_system"
}

def get_db_connection():
    """Get a MySQL database connection."""
    return mysql.connector.connect(**DB_CONFIG)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle date, datetime, and Decimal types."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

class RequestHandler(BaseHTTPRequestHandler):
    """RequestHandler to process GET, POST, PUT, and DELETE requests."""

    def do_GET(self):
        """Handle GET requests."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            result = None

            if self.path.startswith("/bookings/"):
                booking_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM bookings WHERE BookingID = %s", (booking_id,))
                result = cursor.fetchone()
            elif self.path.startswith("/trains/"):
                train_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM trains WHERE TrainID = %s", (train_id,))
                result = cursor.fetchone()
            elif self.path.startswith("/stations/"):
                station_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM stations WHERE StationID = %s", (station_id,))
                result = cursor.fetchone()
            elif self.path.startswith("/reviews/"):
                review_id = self.path.split("/")[-1]
                cursor.execute("SELECT * FROM reviews WHERE ReviewID = %s", (review_id,))
                result = cursor.fetchone()
            else:
                cursor.execute("SELECT * FROM trainschedules")
                result = cursor.fetchall()

            response_body = json.dumps(result, cls=CustomJSONEncoder)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response_body.encode())
        except mysql.connector.Error as db_err:
            self.send_error(500, f"Database error: {str(db_err)}")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def do_POST(self):
        """Handle POST requests."""
        conn = None
        cursor = None
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            if self.path.startswith("/bookings/"):
                passenger_id = data.get("PassengerID")
                schedule_id = data.get("ScheduleID")
                booking_date = data.get("BookingDate", datetime.now().isoformat())
                travel_date = data.get("TravelDate")
                travel_class = data.get("Class")
                fare = data.get("Fare")
                status = data.get("Status", "Pending")

                if not all([passenger_id, schedule_id, travel_date, travel_class, fare]):
                    self.send_error(400, "Missing required fields")
                    return

                insert_query = """
                    INSERT INTO bookings (PassengerID, ScheduleID, BookingDate, TravelDate, Class, Fare, Status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(insert_query, (passenger_id, schedule_id, booking_date, travel_date, travel_class, fare, status))
                conn.commit()

            elif self.path.startswith("/reviews/"):
                booking_id = data.get("BookingID")
                passenger_id = data.get("PassengerID")
                rating = data.get("Rating")
                comments = data.get("Comments")
                review_date = data.get("ReviewDate", datetime.now().isoformat())

                if not all([booking_id, passenger_id, rating, comments]):
                    self.send_error(400, "Missing required fields")
                    return

                insert_query = """
                    INSERT INTO reviews (BookingID, PassengerID, Rating, Comments, ReviewDate)
                    VALUES (%s, %s, %s, %s, %s)
                """
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(insert_query, (booking_id, passenger_id, rating, comments, review_date))
                conn.commit()

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": "Data added successfully"}
            self.wfile.write(json.dumps(response).encode())

        except mysql.connector.Error as db_err:
            self.send_error(500, f"Database error: {str(db_err)}")
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def do_PUT(self):
        """Handle PUT requests."""
        conn = None
        cursor = None
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            if self.path.startswith("/bookings/"):
                booking_id = self.path.split("/")[-1]
                updates = []
                update_query = "UPDATE bookings SET "

                for field, value in data.items():
                    updates.append(f"{field} = %s")

                update_query += ", ".join(updates) + " WHERE BookingID = %s"

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(update_query, (*data.values(), booking_id))
                conn.commit()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": "Data updated successfully"}
            self.wfile.write(json.dumps(response).encode())

        except mysql.connector.Error as db_err:
            self.send_error(500, f"Database error: {str(db_err)}")
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def do_DELETE(self):
        """Handle DELETE requests."""
        conn = None
        cursor = None
        try:
            if self.path.startswith("/bookings/"):
                booking_id = self.path.split("/")[-1]

                delete_query = "DELETE FROM bookings WHERE BookingID = %s"

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(delete_query, (booking_id,))
                conn.commit()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"message": "Data deleted successfully"}
            self.wfile.write(json.dumps(response).encode())

        except mysql.connector.Error as db_err:
            self.send_error(500, f"Database error: {str(db_err)}")
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Running the HTTP server
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
