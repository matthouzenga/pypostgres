from flask import Flask
from flask import jsonify
import os
import psycopg2

app = Flask(__name__)
pUser = os.getenv('database-user')
pPassword = os.getenv('database-password')
pDatabase = os.getenv('database-name')

@app.route('/')
def index():
    conn = psycopg2.connect(
       host="postgresql",
       database=pDatabase,
       user=pUser,
       password=pPassword)

    cur = conn.cursor()
    cur.execute('SELECT * FROM sample')

    return_row = cur.fetchone()

    conn.close()    

    out_string = 'row 1: ' + return_row[0] + ' ' + str(return_row[1])
    return out_string

app.run(host='0.0.0.0', port=5000)
