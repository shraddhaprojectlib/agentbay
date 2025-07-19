from flask import Flask, render_template, request, redirect, url_for, flash, session
from auth import signup_db, login_db
from functools import wraps
from models import User, Tool
from tools.tool_operations import create_tool, tools_by_user, update_tool, delete_tool
from peewee import fn

app = Flask(__name__)
app.secret_key = "windows"


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        message, category, status = signup_db(name, email, username, password)
        flash(message=message, category=category)
        if status == True:
            return redirect(url_for("login"))
        else:
            return redirect(url_for("signup"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        message, category, status, user = login_db(username, password)
        flash(message=message, category=category)
        if status == True:
            session["user_id"] = user.id
            print(f"USER {session['user_id']} is now logged in")
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = User.get_by_id(session["user_id"])
    tools = tools_by_user(user)
    return render_template("dashboard.html", current_user=user, tools=tools)


@app.route("/create-tool", methods=["GET", "POST"])
@login_required
def add_tool():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        type = request.form["type"]
        url = request.form["url"]
        user = User.get_by_id(session["user_id"])
        message, category, status = create_tool(name, description, url, type, user)
        flash(message=message, category=category)
        if status:
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("add_tool"))

    return render_template("tools/add_tool.html")


@app.route("/update-tool/<int:id>", methods=["GET", "POST"])
@login_required
def edit_tool(id):
    user = User.get_by_id(session["user_id"])
    current_tool = Tool.get_or_none((Tool.id == id) & (Tool.user == user))
    if not current_tool:
        flash("you cannot access other IDs", category="danger")
        return redirect(url_for("dashboard"))
    print(f"{user} and the {current_tool}")
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        type = request.form["type"]
        url = request.form["url"]
        user = User.get_by_id(session["user_id"])
        message, category, status = update_tool(
            current_tool, name, description, type, url
        )
        flash(message=message, category=category)
        if status:
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("edit_tool", id=id))

    return render_template("tools/update_tool.html", current_tool=current_tool)


@app.route("/delete-tool/<int:id>", methods=["GET", "POST"])
@login_required
def del_tool(id):
    # access logic
    user = User.get_by_id(session["user_id"])
    current_tool = Tool.get_or_none((Tool.id == id) & (Tool.user == user))
    if not current_tool:
        flash("you cannot access other IDs", category="danger")
        return redirect(url_for("dashboard"))
    meessage, category = delete_tool(current_tool)
    flash(message=meessage, category=category)
    return redirect(url_for("dashboard"))


@app.route("/all-tools",methods=["GET", "POST"])
def alltools():

    query = request.args.get('query',"").strip().lower()
    tools = Tool.select(Tool,User).join(User).where(fn.LOWER(Tool.name).contains(query.lower()))
    #tool.select - all columns of User and Tool
    #tool.join - able to access username of User
    #tool.where - condition only exact match  From Tool
    #if you wanted to use contains it will works only with the fn object
    #fn object provides you flitering action and string actions
    #contains - query : Can --> Tool starting name with 'can'
    return render_template("tools/all_tools.html",tools=tools)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
