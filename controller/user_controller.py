from app import app
from flask import jsonify , request ,send_file
from datetime import datetime
from model.user_model import UserModel
from model.auth_model import AuthModel

# Instantiate UserModel class

obj = UserModel()
auth = AuthModel()
@app.route('/user/getall')
@auth.token_auth()
def user_getall_controller():
    
    # Fetch the data using user_getall_model
   # users = obj.user_getall_model()

    # Return the data as a JSON response using jsonify
    return obj.user_getall_model()  # Ensure the response is in JSON format

# Define a route to fetch a user by ID
@app.route('/user/getbyid/<int:id>')
def user_getbyid_controller(id):
    # Fetch the data using user_getbyid_model
    return obj.user_getbyid_model(id) 

# Define a route to update
@app.route('/user/update' , methods=['PUT'])
def user_update_controller():
    # Update the user using user_update_model
    
    return obj.user_update_model(request.form)

# Define a route to delete a user by ID
@app.route('/user/delete/<int:id>' , methods=['DELETE'])
def user_delete_controller(id):

    # Delete the user using user_delete_model
    
    return obj.user_delete_model(id)

# Def a route for patch
@app.route('/user/patch/<int:id>' , methods=['PATCH'])
def user_patch_controller(id):
    # Update the user using user_update_model
    return obj.user_patch_model(request.form , id)

# Define a route to add a user
@app.route('/user/adduser', methods=['POST'])
# @auth.token_auth('/user/adduser')
def user_add_controller():

    # add user by form data
    # return  obj.user_add_model(request.form)
    # Add user by raw data
    # Get the raw JSON data from the request body
    data = request.get_json()  # This will get the data as a Python dictionary
    # Pass the raw data to the model
    return obj.user_add_model(data)

# Define a route to add multiple users
@app.route('/user/addmultiple', methods=['POST'])
def user_addmultiple_controller():
    # Get the raw JSON data from the request body
    data = request.get_json()  # This will get the data as a Python dictionary
    
    # Pass the raw data to the model
    return obj.user_addmultiple_model(data)

# Define a route to fetch all users with pagination
@app.route('/user/getusers', methods=['GET'])
def user_pagination_controller():
    # Get the page number and page size from the query string (defaults if not provided)
    page = int(request.args.get('page', 1))  # Default to page 1 if not provided
    page_size = int(request.args.get('page_size', 10))  # Default to 10 records per page
    
    # Call the model to fetch paginated data
    users, total_records = obj.user_pagination_model(page, page_size)
    
    # Calculate total pages
    total_pages = (total_records // page_size) + (1 if total_records % page_size > 0 else 0)
    
    # Prepare the response with pagination metadata
    response = {
        "current_page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "data": users
    }
    
    return jsonify(response)

# upload file to the server
@app.route('/user/<int:id>/uploads/avatar', methods=['PUT'])
def user_upload_avatar_controller(id):
    # print(request.files['avatar'])
    file = request.files['avatar']
    # file.save('uploads/' + file.filename)
    uniqueFileName = str(datetime.now().timestamp()).replace('.', '') 
    fileNameSplit = file.filename.split('.')
    ext = fileNameSplit[len(fileNameSplit) - 1]
    finalFilePath = f"uploads/{uniqueFileName}.{ext}"
    file.save(finalFilePath)
   
    return obj.user_upload_avatar_model(id, finalFilePath)  # Ensure the response is in JSON format

# show the avatar
@app.route('/uploads/<filename>' , methods=['GET'])
def user_getavatar_controller(filename):
    return send_file(f'uploads/{filename}')

# user login
@app.route('/user/login', methods=['POST'])
def user_login_controller():
    # request.get_json()
    # request.form
    return obj.user_login_model(request.get_json())

