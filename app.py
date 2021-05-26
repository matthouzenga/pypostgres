from flask import Flask
import os

app = Flask(__name__)
pUser = os.getenv('database-user')       
pPassword = os.getenv('database-password')       
pDatabase = os.getenv('database-name')       

@app.route('/')
def index():
    out_string = 'version 3 - database: ' + pDatabase + 'user: ' + pUser + ' password: ' + pPassword
    return out_string

app.run(host='0.0.0.0', port=5000)
