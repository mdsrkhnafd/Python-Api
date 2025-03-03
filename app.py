import os
from flask import Flask
app = Flask(__name__)

# # Check if FLASK_ENV is being recognized
# print("FLASK_ENV:", os.getenv("FLASK_ENV"))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/home')
def home():
    return 'This is the home page'

# Importing the controllers
from controller import *



# if __name__ == "__main__":
#     app.run(debug=True)  # This also ensures debug mode is enabled