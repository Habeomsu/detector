from flask import Flask,render_template,url_for,current_app,g,request,redirect,flash,make_response,session
from email_validator import validate_email,EmailNotValidError
import logging
import os
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail,Message
app = Flask(__name__)

app.debug = True
app.config["SECRET_KEY"]="2AZSMss3p5QPbcY2hBsJ"

app.logger.setLevel(logging.DEBUG)

app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]=False

toolbar = DebugToolbarExtension(app)

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail=Mail(app)

@app.route("/",
           methods=["GET","POST"])
def index():
    return "hello,Flaskbook!"

@app.route("/hello/<name>",
           methods=["GET","POST"],
           endpoint="hello-endpoint")
def hello(name):
    return f"Hello, {name}!"

@app.route("/name/<name>")
def show_name(name):

    return render_template("index.html",name=name)

with app.test_request_context():

    print(url_for("index"))

    print(url_for("hello-endpoint",name="world"))

    print(url_for("show_name",name="AK",page="1"))

ctx=app.app_context()
ctx.push()

print(current_app.name)

g.connection="connection"
print(g.connection)

with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated"))

@app.route("/contact")
def contact():
    response = make_response(render_template("contact.html"))

    response.set_cookie("flaskbook key", "flaskbook value")

    session["username"] = "AK"

    
    return response

@app.route("/contact/complete",methods=["GET","POST"])
def contact_complete():
    if request.method=="POST":
        username=request.form["username"]
        email=request.form["email"]
        description =request.form["description"]
        
        is_valid = True

        if not username:
            flash("사용자명은 필수입니다")
            is_valid=False

        if not email:
            flash("메일 주소는 필수입니다")
            is_valid=False
        
        try:
            validate_email(email)
        except EmailNotValidError:
            flash("메일 주소의 형식으로 입력해 주세요")
            is_valid=False
        
        if not description:
            flash("문의 내용은 필수입니다")
            is_valid=False
        
        if not is_valid:
            return redirect(url_for("contact"))

        send_email(
            email,
            "문의 감사합니다.",
            "contact_mail",
            username=username,
            description=description,
        )
        flash("문의해 주셔서 감사합니다. ")
        return redirect(url_for("contact_complete"))
    return render_template("contact_complete.html")

def send_email(to,subject,template,**kwargs):
    msg=Message(subject,recipients=[to])
    msg.body=render_template(template+".txt",**kwargs)
    msg.html=render_template(template+".html",**kwargs)
    mail.send(msg)



