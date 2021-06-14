from flask import Flask
from flask import jsonify,render_template, request,redirect
import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

#Check if NOTCONTAINER environmental variable set by user
AM_I_LOCAL = os.environ.get('NOTCONTAINER', False)
  #If not in container, get DB info from regular env variables
if AM_I_LOCAL:
    pUser = os.getenv('DBUSER')
    pPassword = os.getenv('DBPASSWORD')
    pDatabase = os.getenv('DBNAME')
  #If in container, use the standard DB env variables set by OpenShift
else:
    pUser = os.getenv('database-user')
    pPassword = os.getenv('database-password')
    pDatabase = os.getenv('database-name')

db_string = "postgresql://" + pUser + ":" + pPassword + "@postgresql:5432/" + pDatabase

db = create_engine(db_string)
base = declarative_base()

class Storage(base):
    __tablename__ = 'sample'

    name = Column(String, primary_key=True)
    machinetype = Column(Integer)
    model = Column(String)
    year = Column(Integer)

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)


@app.route('/')
def index():
    return redirect("/base")

@app.route('/base', methods=["POST", "GET"])
def base():
    if request.method == "POST":
       in_name = request.form["name"]
       in_machinetype = request.form["machinetype"]
       in_model = request.form["model"]
       in_year = request.form["year"]
       print('Name: ',in_name)
       print('MT: ',in_machinetype)
       print('Model: ',in_model)
       print('Year: ',in_year)

       #Insert new row into database

       new_storage = Storage(name=in_name, machinetype=in_machinetype, model=in_model, year=in_year)
       session.add(new_storage)
       session.commit()

       return redirect("/base", code=302)

    else:   #GET request
       storage = session.query(Storage)

       return render_template('base.html',storage=storage)

app.run(host='0.0.0.0', port=5000)
