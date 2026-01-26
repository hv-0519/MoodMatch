from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

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
    '''View favorite activities - redirect to user version if logged in'''
    if current_user.is_authenticated:
        return redirect(url_for('user.favorites'))
    return render_template('main/Favorites.html')

@main_bp.route('/history')
def history():
    '''View search history - redirect to user version if logged in'''
    if current_user.is_authenticated:
        return redirect(url_for('user.history'))
    return render_template('main/history.html')
