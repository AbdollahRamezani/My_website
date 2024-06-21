import os
from flask import Flask, render_template, request, redirect, url_for, session
from deepface import DeepFace
from sqlmodel import Field, SQLModel, create_engine, Session, select
from pydantic import BaseModel  #validation


app = Flask("Analyze Face")
app.config["UPLOAD_FOLDER"] = './uploads'  #کانفیگها حتما باید با حروف بزرگ نوشته بشن
app.config["ALLOWED_EXTENSIONS"] = {'png', 'jpg', 'jpeg'}

class User(SQLModel, table=True):  
    id: int = Field(default=None, primary_key=True )
    city: str = Field()
    username: str = Field()
    password: str = Field()

engine = create_engine('sqlite:///./my_website.db', echo=True)    
SQLModel.metadata.create_all(engine)    

                                 # pydantic models for request validation
class RegisterModel(BaseModel):
    city= str
    username= str
    password= str

class LoginModel(BaseModel):
    username= str
    password= str    

def auth(email, password):  # authentication
    if email =="admin@gmail.com" and password == "admin":
        return True
    else:
        return False
    
def allowed_files(filename):
    return True    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])  # Login
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        result = auth(email, password)
        if result:
            #upload
            return redirect(url_for("upload"))
        else:
            #login
            return redirect(url_for("login"))
        
@app.route("/register", methods=["GET", "POST"])  # Register    
def register():  
    if request.method == "GET":
        return render_template("register.html")     
    elif request.method == "POST":
        try:
            register_data = RegisterModel(username=request.form["username"], 
                                        password=request.form["password"],
                                        city=request.form["city"])
        except:
            print("Type error")
            return redirect(url_for("register"))

        with Session(engine) as db_session:
            statement = select(User).where(User.username == request.form["username"])   
            result = db_session.exec(statement).first() 

        if not result: 
            with Session(engine) as db_session:
                user = User(
                    username=request.form["username"], 
                    password=request.form["password"],
                    city=request.form["city"]
                )
                db_session.add(user)
                db_session.commit()
            print("Your register Done successfully")   
            return redirect(url_for("login"))
        else:
            print("Username already exist, Try another username")    
            return redirect(url_for("register"))

@app.route("/upload", methods = ["GET", "POST"])  # Upload
def upload():
    if request.method == "GET":
        return render_template("upload image.html")
    
    elif request.method == "POST":
        image = request.files["image"]
        if image.filename == "":  #فایل خالی
            return redirect(url_for("upload"))
        else:
            if image and allowed_files(image.filename):
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
                image.save(save_path)
                result = DeepFace.analyze(
                    img_path = save_path, 
                    actions = ['age'],
                )

        return render_template("result face analyzing.html", age=result[0]["age"])
    
@app.route("/form_bmr", methods = ["GET", "POST"])  # BMR
def bmr():
    if request.method == "GET":
        return render_template("form_bmr.html")
    
    elif request.method == "POST":
        weight = int(request.form["weight"])
        height = int(request.form["height"])
        age = int(request.form["age"])
        gender = request.form["gender"]

        if gender == "1":
            result = (10*weight)+(6.25*height)-(5*age)+5
        elif gender == "2":
            result = (10*weight)+(6.25*height)-(5*age)-161

        return render_template("result_calc_BMR.html", BMR=result)




