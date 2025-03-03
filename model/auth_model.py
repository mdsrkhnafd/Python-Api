from functools import wraps
import pyodbc as odbc
from flask import make_response , request
from config.config import DB_CONFIG  # Import the configuration from config.py
import jwt
import re

class AuthModel():
    def __init__(self):
        try:
            # Prepare the connection string using the configuration from config.py
            conn_str = (
                f"DRIVER={{{DB_CONFIG['DRIVER']}}};"
                f"SERVER={DB_CONFIG['SERVER']};"
                f"DATABASE={DB_CONFIG['DATABASE']};"
                f"Trusted_Connection={DB_CONFIG['Trusted_Connection']};"
            )
            # Establish the connection (use conn_str, not self.conn)
            self.conn = odbc.connect(conn_str)  
            self.conn.autocommit = True  # Enable autocommit for this connection
            self.cur = self.conn.cursor()  # Create a cursor object to interact with the database
            print("Connection Successful")
        except odbc.Error as e:
            print("Connection Error:", e)
            # Add specific error handling for better debugging
            sqlstate = e.args[0]
            message = e.args[1]
            print(f"Error Code: {sqlstate}, Error Message: {message}")


    # authenticate user
    def token_auth(self, endpoint = ""):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                endpoint = request.url_rule.rule
                
                print(f"Endpoint: {endpoint}")
                # Get the Authorization header from the request
                authorization = request.headers.get('Authorization')
                print(f"Authorization Header: {authorization}")

                # Check if Bearer token is provided
                if authorization and re.match("^Bearer *([^ ]+) *$", authorization):
                    token = authorization.split(" ")[1]
                    try:
                        # Decode the JWT
                        jwtdecoded = jwt.decode(token, 'mudasir', algorithms=['HS256'])
                        role_id = jwtdecoded['payload']['role_id']
                    except jwt.ExpiredSignatureError:
                        return make_response({"Error": "Token Expired"}, 401)
                    except jwt.InvalidTokenError:
                        return make_response({"Error": "Invalid Token"}, 401)

                    # Debugging: print the endpoint being searched
                    print(f"Searching for endpoint: {endpoint}")

                    # Query the database to check if the endpoint exists
                    query = "SELECT roles FROM accessbility_view WHERE endpoint = ?"
                    print(f"Executing query: {query} with parameter: {endpoint}")

                    self.cur.execute(query, (endpoint,))
                    rows = self.cur.fetchall()

                    # Debugging: print the fetched rows
                    print(f"Rows fetched: {rows}")
                    if not rows:
                        print("No rows found")
                        return make_response({"Error": "UNKNOWN ENDPOINT"}, 401)
                    else:
                        print("Rows found:", rows[0].roles)
                        allowed_roles = rows[0].roles
                        # Check if role_id is not None before checking if it's in allowed_roles
                        if isinstance(allowed_roles, str):
                            allowed_roles = eval(allowed_roles)
                        if role_id is not None and role_id in allowed_roles:
                            return func(*args, **kwargs)  # Proceed with the request if role is valid
                        else:
                            return make_response({"Error": "Invalid Role"}, 401)
                else:
                    return make_response({"Error": "Invalid Token"}, 401)  # Invalid Token if no Bearer token

            return wrapper
        return decorator
