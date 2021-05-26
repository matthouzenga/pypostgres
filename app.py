from flask import Flask
import os

app = Flask(__name__)
pUser = os.getenv('database-user')       
pPassword = os.getenv('database-password')       
pDatabase = os.getenv('database-name')       

@app.route('/')
def index():
    out_string = 'database: ' + pDatabase + 'user: ' + pUser + ' password: ' + pPassword
    return 'Hello, Web App with Python Flask!'

app.run(host='0.0.0.0', port=5000)
