from flask import Blueprint, Flask,render_template
from flask_login import current_user

user_bp = Blueprint('user', __name__)

@user_bp.route("/user_dashboard")
def user_dashboard():
    print(current_user.first_name, current_user.profile_picture)
    return render_template("user/user_dashboard.html")