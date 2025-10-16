from flask import Blueprint, render_template, session
from app.components.navigation import NavigationManager

# Crear blueprint principal
main_bp = Blueprint('main', __name__)
nav_manager = NavigationManager()


@main_bp.route('/')
def index():
    """Landing Page Principal - Muestra directamente el template"""
    navigation = nav_manager.get_navigation(
        user_authenticated=session.get('user_authenticated', False)
    )
    breadcrumbs = nav_manager.get_breadcrumbs('main.index')

    return render_template('main/index.html',
                         navigation=navigation,
                         breadcrumbs=breadcrumbs,
                         title='Truck Stop - Home')