from flask import Blueprint, render_template
# from models.database import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    '''Home page with mood selector'''
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    '''About page'''
    return render_template('main/about.html')

@main_bp.route('/favorites')
def favorites():
    '''View favorite activities'''
    return render_template('main/favorites.html')

@main_bp.route('/history')
def history():
    '''View search history'''
    return render_template('main/history.html')