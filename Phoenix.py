from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
from PIL import Image
import os
import pickle
import cv2
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pymongo

path = (
    "/Users/aviral/Documents/JIIT/5th Semester/Minor Project/Web App/testpnimage.jpeg"
)

app = Flask(__name__)
app.secret_key = "abc123"
global USERNAME
global linchk
USERNAME = ""
linchk = 0

# LOGGED OUT PAGES

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/reset")
def reset():
    global USERNAME, linchk
    USERNAME = ""
    linchk = 0
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html", bool=0)


@app.route("/check_login", methods=["POST"])
def check_login():
    uname = request.form.get("uname")
    upass = request.form.get("upass")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Minor_Project_5thSem"]
    mycol = mydb["UserPass1"]
    dblist = mycol.find({}, {"_id": 0})
    query = {"username": uname, "password": upass}
    if query in dblist:
        global USERNAME, linchk
        USERNAME = uname
        linchk = 1
        return render_template("home_lin.html", un=USERNAME)
    else:
        return render_template("login.html", bool=1)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/check_register", methods=["POST"])
def check_register():
    uname = request.form.get("uname")
    upass1 = request.form.get("upass1")
    upass2 = request.form.get("upass2")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Minor_Project_5thSem"]
    mycol = mydb["UserPass1"]
    flag = 0
    dblist = mycol.find({}, {"_id": 0, "password": 0})
    query = {"username": uname}
    if query in dblist:
        flag = 1
    if flag == 1:
        return render_template("register.html", bool=1)
    elif upass1 == upass2:
        query = {"username": uname, "password": upass1}
        dblist = mycol.insert_one(query)
        return render_template("login.html", bool=0)
    elif upass1 != upass2:
        return render_template("register.html", bool=2)


@app.route("/contact")
def contact():
    return render_template("contactus.html", bool=0)

@app.route("/enquiry_form", methods = ["POST"])
def enquiry_form():
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    email = request.form.get("email")
    mobile = request.form.get("mobile")
    desc = request.form.get("desc")
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Minor_Project_5thSem"]
    mycol = mydb["EnquiryForm"]
    query = {"First Name": fname, "Last Name": lname, "Email ID": email, "Mobile Number": mobile, "Enquiry": desc}
    dblist = mycol.insert_one(query)
    return render_template("contactus.html", bool=1)

@app.route("/upload_form")
def xray():
    global linchk, USERNAME
    if linchk==1:
        return render_template("xrayform.html",un=USERNAME)
    else:
        return render_template("login.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    global USERNAME
    if "file" in request.files:
        file = request.files["file"]
        filename = secure_filename(file.filename)
        if os.path.isfile(path):
            os.remove(path)
        file.save(path)
    lm = tf.keras.models.load_model(
        "/Users/aviral/Documents/JIIT/5th Semester/Minor Project/Web App/model/my_model.h5"
    )
    y = pickle.load(
        open(
            "/Users/aviral/Documents/JIIT/5th Semester/Minor Project/Web App/y.pkl",
            "rb",
        )
    )
    img = cv2.imread(path)
    img = cv2.resize(img, (100, 100))
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    predictions = lm.predict(img_array, verbose=0)
    finalans = y[np.argmax(predictions)]
    if finalans == 0:
        finalans = "The model diagnoses it as Pneumonia."
    if finalans == 1:
        finalans = "The model diagnoses it as not Pneumonia."
    return render_template(
        "result.html",
        result=finalans,
        un=USERNAME
    )

# LOGGED IN PAGES
@app.route("/home_lin")
def home_lin():
    global USERNAME
    return render_template("home_lin.html", un=USERNAME)

app.run("localhost", 3000)