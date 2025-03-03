import pyodbc as odbc
from flask import make_response
from datetime import datetime , timedelta
from config.config import DB_CONFIG  # Import the configuration from config.py
import jwt

class UserModel():
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
            self.conn = odbc.connect(conn_str)  # Corrected: Use conn_str for the connection
            self.conn.autocommit = True  # Enable autocommit for this connection
            self.cur = self.conn.cursor()  # Create a cursor object to interact with the database
            
            print("Connection Successful")
            
        except odbc.Error as e:
            print("Connection Error:", e)
            # Add specific error handling for better debugging
            sqlstate = e.args[0]
            message = e.args[1]
            print(f"Error Code: {sqlstate}, Error Message: {message}")
            # More specific troubleshooting can go here, like logging the error or retrying the connection.
            
    # get all users
    def user_getall_model(self):
        # Execute the query to fetch all users
        self.cur.execute("SELECT * FROM users")  # Replace 'users' with your actual table name
        rows = self.cur.fetchall()
        
        # Print the rows for debugging
        # print("Fetched rows:", rows)
        
        # If rows is empty, handle it appropriately
        if not rows:
            return make_response({"error": "No data found"}, 404)
        
        # Example: Return a list of dictionaries based on the query results
        user_list = []
        for row in rows:
            user_dict = {
                'id': row[0],  # Replace with the correct column indices
                'name': row[1],
                'email': row[2],
                'phone' : row[3],
                'role_id': row[6],
                'avatar': row[5]
            
                
                # Add more fields if necessary
            }
            user_list.append(user_dict)
        
        res = make_response({"payload": user_list}, 200)
        res.headers.add('Access-Control-Allow-Origin', '*')
        return res  # Return the list of users
    
    # get user by id
    def user_getbyid_model(self, id):
        # Execute the query to fetch a single user by ID
        self.cur.execute("SELECT * FROM users WHERE id = ?", (id,))  # Replace 'users' with your actual table name
        row = self.cur.fetchone()
        
        # Print the row for debugging
        print("Fetched row:", row)
        
        # If row is None, handle it appropriately
        if row is None:
            return make_response({"error": "User not found"}, 404)
        
        # Example: Return a dictionary based on the query result
        user_dict = {
            'id': row[0],  # Replace with the correct column indices
            'name': row[1],
            'email': row[2],
            'phone' : row[3],
            'avatar': row[5],
            'role_id': row[6]
            
            # Add more fields if necessary
        }
        
        
        return make_response({"payload": user_dict}, 200)  # Return the user dictionary 
        
    # delete user by id
    def user_delete_model(self, id):
        # Execute the query to delete a user by ID
        self.cur.execute("DELETE FROM users WHERE id = ?", (id,))
        self.conn.commit()  # Commit the transaction
        
        # Check if any rows were affected
        if self.cur.rowcount > 0:
            return make_response({"message": "User deleted successfully"}, 200)
        else:
            return make_response({"error": "User not found"}, 404)

    # add user
    def user_add_model(self, data):
        # Execute the query to add a new user
        self.cur.execute(f"INSERT INTO users (name, email, phone, password , role_id) VALUES ('{data['name']}' , '{data['email']}' , '{data['phone']}' , '{data['password']}' , '{data['role_id']}')")
        self.conn.commit()  # Commit the transaction
        
        # Check if any rows were affected
        if self.cur.rowcount > 0:
            return make_response({"message": "User added successfully"}, 201)
        else:
            return make_response({"error": "User not added"}, 400)

    # add multiple users
    def user_addmultiple_model(self, data):
        # print(data)  # Print the data for debugging

        qry = "INSERT INTO users (name, email, phone, password , role_id) VALUES "
        
        for userdata in data:
            qry += f"('{userdata['name']}', '{userdata['email']}', '{userdata['phone']}', '{userdata['password']}', '{userdata['role_id']}'),"
        # finalqry = qry.rstrip(',')  # Remove the trailing comma
        qry = qry[:-1]  # Remove the trailing comma
        # print(qry)  # Print the user for debugging
        self.cur.execute(qry)  # Execute the query
        self.conn.commit()  # Commit the transaction
        if self.cur.rowcount > 0:
            print(f"Rows affected: {self.cur.rowcount}")  # Print how many rows were affected
            return make_response({"message": "Multiple Users added successfully"}, 201)
        else:
            return make_response({"error": "Users not added"}, 400)    
    
    
    # update user
    def user_update_model(self, data):
        # Execute the query to add a new user
        self.cur.execute(f"UPDATE users SET name = '{data['name']}' , email = '{data['email']}' , phone = '{data['phone']}' , role = '{data['role']}' , password = '{data['password']}' WHERE id = {data['id']}")
        self.conn.commit()  # Commit the transaction
        
        # Check if any rows were affected
        if self.cur.rowcount > 0:
            return make_response({"message": "User updated successfully"}, 200)
        else:
            return make_response({"error": "User not updated"}, 400)  

    # patch user
    def user_patch_model(self, data, id):
        # Start the update query
        qry = "UPDATE users SET "
        
        # Add each column and its value to the query, excluding empty values
        for key in data:
            value = data[key]
            
            # Skip empty values (i.e., if value is empty or None)
            if value:
                if isinstance(value, str):
                    qry += f"{key}='{value}',"  # Add quotes for string values
                else:
                    qry += f"{key}={value},"  # Add without quotes for non-string values

        # Remove the last comma and add the WHERE condition
        qry = qry.rstrip(',')  # This removes the last comma
        qry += f" WHERE id={id}"

        print("Final SQL Query:", qry)  # Print the query for debugging purposes

        try:
            self.cur.execute(qry)  # Execute the query
            self.conn.commit()  # Commit the transaction
            
            print(f"Rows affected: {self.cur.rowcount}")  # Print how many rows were affected
            
            if self.cur.rowcount > 0:
                return make_response({"message": "User patched successfully"}, 200)
            else:
                return make_response({"error": "User not patched"}, 404)
        
        except Exception as e:
            # Handle any errors during query execution
            print(f"Error: {e}")
            return make_response({"error": "Failed to update user"}, 500)
        

    # Method to fetch paginated data
    def user_pagination_model(self, page, page_size):
        offset = (page - 1) * page_size  # Calculate the offset

        # Execute the SQL query to fetch paginated data
        self.cur.execute("SELECT * FROM users ORDER BY id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", (offset, page_size))
        users = self.cur.fetchall()

        # Get the total number of records in the table
        self.cur.execute("SELECT COUNT(*) FROM users")
        total_records = self.cur.fetchone()[0]

        # Format the users data as a list of dictionaries
        users_list = []
        for user in users:
            users_list.append({
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'phone': user[3],
                'role': user[4],
                'avatar': user[5]
            })

        return users_list, total_records  # Return users list and total records count
    
    # Method to upload avatar
    def user_upload_avatar_model(self, id, filepath):
        self.cur.execute(f"UPDATE users SET avatar = '{filepath}' WHERE id = {id}")

        if self.cur.rowcount > 0:
            return make_response({"message": "Avatar uploaded successfully"}, 200)
        else:
            return make_response({"error": "Avatar not uploaded"}, 400)
        
    # Method to login a user
    def user_login_model(self, data):
        # Execute the query to fetch a single user by email and password
        self.cur.execute(f"SELECT id , name , email , phone , avatar , role_id FROM users WHERE email = '{data['email']}' AND password = '{data['password']}'")
        row = self.cur.fetchone()
        print(row)
        # If row is None, handle it appropriately
        if row is None:
            return make_response({"error": "User not found"}, 404)
        
        # Example: Return a dictionary based on the query result
        user_dict = {
            'id': row[0],  # Replace with the correct column indices
            'name': row[1],
            'email': row[2],
            'phone' : row[3],
            'avatar': row[4],
            'role_id' : row[5]
            
            # Add more fields if
            # necessary
        }

        # Generate a JWT token
        exp_time = datetime.now() + timedelta(minutes=15)  # Set the expiration time
        exp_epoch_time = int(exp_time.timestamp())  # Convert the expiration time to epoch time
        
        # Create the payload for the JWT token
        payload = {
            "payload": user_dict,
            "exp": exp_epoch_time
        }

        # Generate the JWT token using the 'HS256' algorithm
        # and a secret key (can be any string)
        token = jwt.encode(payload, 'mudasir', algorithm='HS256')
        print(token)  

        # Return the user dictionary
        return make_response({"token": token}, 200)

           
