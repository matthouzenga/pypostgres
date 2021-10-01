This is a sample application program written in Python that utilizes a PostgreSQL database and object storage.  It was written such that it could be tested locally on my macbook and then deployed to OpenShift via github.  The application will retrieve all the information it needs to connect to the database and object storage from environmental variables.  For OpenShift these variables are shared via the object bucket claim and secret.  When running locally these variables should be set before running the application.


