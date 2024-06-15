import os
from flask import Flask, render_template, request, redirect, url_for, session
from deepface import DeepFace


app = Flask("Analyze Face")
app.config["UPLOAD_FOLDER"] = './uploads'  #کانفیگها حتما باید با حروف بزرگ نوشته بشن
app.config["ALLOWED_EXTENSIONS"] = {'png', 'jpg', 'jpeg'}

def auth(email, password):
    if email =="admin@gmail.com" and password == "admin":
        return True
    else:
        return False
    
def allowed_files(filename):
    return True    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
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

@app.route("/upload", methods = ["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    
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

        return render_template("result.html", age=result[0]["age"])
    
@app.route("/bmr", methods = ["GET", "POST"])
def bmr():
    if request.method == "GET":
        return render_template("bmr.html")
    
    elif request.method == "POST":
        weight = int(request.form["weight"])
        height = int(request.form["height"])
        age = int(request.form["age"])
        gender = request.form["gender"]

        if gender == "1":
            result = (10*weight)+(6.25*height)-(5*age)+5
        elif gender == "2":
            result = (10*weight)+(6.25*height)-(5*age)-161

        return render_template("calculate.html", BMR=result)




