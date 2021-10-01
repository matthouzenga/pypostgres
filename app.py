from flask import Flask
from flask import jsonify,render_template, request,redirect
import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import boto3
import botocore

app = Flask(__name__)

#Check if NOTCONTAINER environmental variable set by user
AM_I_LOCAL = os.environ.get('NOTCONTAINER', False)
  #If not in container, get DB info from regular env variables
if AM_I_LOCAL:
    pUser = os.getenv('DBUSER')
    pPassword = os.getenv('DBPASSWORD')
    pDatabase = os.getenv('DBNAME')
    #get s3 bucket info
    pBucketHost = os.getenv('BUCKETHOST')
    pBucketName = os.getenv('BUCKETNAME')
    pBucketPort = os.getenv('BUCKETPORT')
    pBucketAccessKey = os.getenv('BUCKETACCESSKEY')
    pBucketSecretKey = os.getenv('BUCKETSECRETKEY')
  #If in container, use the standard DB env variables set by OpenShift
else:
    pUser = os.getenv('database-user')
    pPassword = os.getenv('database-password')
    pDatabase = os.getenv('database-name')
    pBucketHost = os.getenv('BUCKET_HOST')
    pBucketName = os.getenv('BUCKET_NAME')
    pBucketPort = os.getenv('BUCKET_PORT')
    pBucketAccessKey = os.getenv('AWS_ACCESS_KEY_ID')
    pBucketSecretKey = os.getenv('AWS_SECRET_ACCESS_KEY')

#confirm that all environment variables were read
if pUser and pPassword and pDatabase and pBucketHost and pBucketName and pBucketAccessKey and pBucketSecretKey:
  print('all env variable successfully read')
else:
  print('some env variables were missing')

#connect to object bucket
access_key = pBucketAccessKey
secret_key = pBucketSecretKey
endpoint_url = 'https://' + str(pBucketHost)
connection = boto3.client('s3',
    verify=False,
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key)

#connect to database
db_string = "postgresql://" + pUser + ":" + pPassword + "@postgresql:5432/" + pDatabase
db = create_engine(db_string)
base = declarative_base()

#define the table 
class Storage(base):
    __tablename__ = 'sample'

    name = Column(String, primary_key=True)
    machinetype = Column(Integer)
    model = Column(String)
    year = Column(Integer)

Session = sessionmaker(db)
session = Session()
base.metadata.create_all(db)  #creates the table if not already defined


@app.route('/', methods=["POST", "GET"])
def index():
    #handle form being submitted
    if request.method == "POST":
       in_name = request.form["name"]
       in_machinetype = request.form["machinetype"]
       in_model = request.form["model"]
       in_year = request.form["year"]
       in_file = request.files["file1"]

       print('Name: ',in_name,'MT: ',in_machinetype,'Model: ',in_model, 'Year: ',in_year)

      #upload file to object bucket
       if in_file and in_name:
        connection.upload_fileobj(in_file,
          pBucketName,
          in_name)
       else: 
        print('no file uploaded')

       #Insert new row into database

       new_storage = Storage(name=in_name, machinetype=in_machinetype, model=in_model, year=in_year)
       session.add(new_storage)
       session.commit()

       #return redirect("/", code=302)  #this doesn't work on PVS OCP instance for some reason
       storage = session.query(Storage)
       return render_template('base.html',storage=storage)

    else:   #GET request
       storage = session.query(Storage)    #query all rows from database
       return render_template('base.html',storage=storage)

#app.run(host='0.0.0.0', port=8080)
app.run(host='0.0.0.0', port=8080,threaded=True)
