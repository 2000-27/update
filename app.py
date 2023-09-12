from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from datetime import datetime,timedelta
import re

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY']="adfkfj"

db = SQLAlchemy(app)
ma = Marshmallow(app)



class signup(UserMixin,db.Model):
      
      id = db.Column(db.Integer,autoincrement=True, primary_key=True)
      username = db.Column(db.String(200))
      userpassword = db.Column(db.String(),unique=True)
      email = db.Column(db.String(100),unique=True)
      
      
      

      def __init__(self,username, userpassword,email ):
            self.username = username
            self.userpassword =userpassword
            self.email=email
            
      def set_password(self,userpassword):
        self.userpassword = generate_password_hash(userpassword)
        

      def check_password(self,userpassword):
        return check_password_hash(self.userpassword,userpassword)     

class signupSchema(ma.Schema):
      class Meta:
            fields=('id','username','userpassword','email')

single_data = signupSchema()
multiple_data = signupSchema(many=True)


@app.route('/register', methods =['POST'])
def register():
  try:  
    json_body = request.get_json()

    msg = ''
    if request.method == 'POST'  :
        username = json_body['username']
        userpassword = json_body['userpassword']
        email = json_body['email']
      
                  
        if not re.match(r'[^@]+@[^@]+\.[^@]+',email):
           msg = 'Invalid email address !'
           print(msg)
        elif not (re.match(r'[a-zA-Z\s]+$', username)):
           msg = 'Username must contain only characters  and space !'
           print(msg)
       
       
        else:
                 msg = 'You have successfully registered !'
                 new_product = signup(username, userpassword, email)
                 new_product.set_password(userpassword)
                 db.session.add(new_product)
                 db.session.commit()
                 return single_data.jsonify(new_product)
    
       

    return jsonify(username,userpassword,email,msg)
  except :
    msg="ALREAD RECORD IS EXIT "
    return jsonify(msg)
      

@app.route('/register', methods=['GET'])
def get_data():
  all_products = signup.query.all()
  result = multiple_data.dump(all_products)
  return jsonify(result)


@app.route('/register/<username>', methods=['GET'])
def singleuser(username):
     
    all_product=signup.query.filter_by(username=username).first()
    print("ALL PRODUCT: ", all_product)
    result = single_data.dump(all_product)
    print(result)
    return jsonify(result)

def checkpass(email):
 
  all_product=signup.query.filter_by(email=email).first()

  print("ALL PRODUCT: ",all_product)
  result = single_data.dump(all_product)
  print("your emai id is correct and result is => ",result)
  return result



@app.route('/login', methods =['POST'])
def login():
   
    json_body = request.get_json()

    msg = ''
    if request.method == 'POST':
        userpassword = json_body['userpassword']
        email = json_body['email']
        print("password and email id iss => ",userpassword,email)
        # if not re.match(r'[^@]+@[^@]+\.[^@]+',email):
        #    msg = 'Invalid email address !'
        #    print(msg)
           
        try:  
           result=checkpass(email)
           if result=={}:
               msg="there is no record "
               print(msg)
           else:    
               msg="successfully sign up"
               print(msg)  
               token = jwt.encode({'public_id': 1,'exp' :str( datetime.utcnow() + timedelta(minutes = 30)) }, app.config['SECRET_KEY'])
               print("your token is  =>>>>",token)
               return jsonify(message="Login Succeeded!", access_token=token)
               
 
        except  Exception as error:
          msg= 'there is no user '
          print("your exception is ",error) 
            


        return jsonify({"msg": msg})


def create_table():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_table()
    app.run(debug=True)

 

