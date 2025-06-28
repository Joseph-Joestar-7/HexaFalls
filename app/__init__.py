from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
import base64

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///student.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']= 'd29ac4d5dce439ea77f1ef13'

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
csrf=CSRFProtect(app)

# Register a filter called “b64encode” that turns raw bytes into a UTF‑8 base64 string
@app.template_filter('b64encode')
def b64encode_filter(raw_bytes):
    return base64.b64encode(raw_bytes).decode('utf-8')

from app import routes