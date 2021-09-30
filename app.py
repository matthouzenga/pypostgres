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

    #connect to object bucket
bucket_name = 'comms-architect-s3-ocp'
bucket_host = 's3.us-south.cloud-object-storage.appdomain.cloud'
access_key = pBucketAccessKey
secret_key = pBucketSecretKey
endpoint_url = 'https:://' + str(bucket_host)
#connection = boto3.client('s3',
#    verify=False,
#    endpoint_url=endpoint_url,
#    aws_access_key_id=access_key,
#    aws_secret_access_key=secret_key)

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


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
       in_name = request.form["name"]
       in_machinetype = request.form["machinetype"]
       in_model = request.form["model"]
       in_year = request.form["year"]
       in_file = request.files["file1"]

       print('Name: ',in_name,'MT: ',in_machinetype,'Model: ',in_model, 'Year: ',in_year)

      #upload file to object bucket
#       connection.upload_fileobj(in_file,
#         bucket_name,
#         in_name)

       #Insert new row into database

       new_storage = Storage(name=in_name, machinetype=in_machinetype, model=in_model, year=in_year)
       session.add(new_storage)
       session.commit()

       #return redirect("/", code=302)
       storage = session.query(Storage)
       return render_template('base.html',storage=storage)

    else:   #GET request
       storage = session.query(Storage)
       print('GET, writing Bucket = ',pBucketName)
       return render_template('base.html',storage=storage)

#app.run(host='0.0.0.0', port=8080)
app.run(host='0.0.0.0', port=8080,threaded=True)
