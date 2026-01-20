from flask import Blueprint, render_template
from models.database import db

admin_bp = Blueprint("admin", __name__)
