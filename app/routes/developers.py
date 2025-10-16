from flask import Blueprint, render_template, session
from app.components.navigation import NavigationManager

# Crear blueprint de developers
developers_bp = Blueprint('developers', __name__, url_prefix='/developers')
nav_manager = NavigationManager()


@developers_bp.route('/')
def index():
    """Página de información para desarrolladores"""
    navigation = nav_manager.get_navigation(
        user_authenticated=session.get('user_authenticated', False)
    )
    breadcrumbs = nav_manager.get_breadcrumbs('developers.index')

    api_endpoints = [
        {
            'method': 'GET',
            'endpoint': '/api/companies',
            'description': 'Get list of all companies',
            'auth_required': True
        },
        {
            'method': 'POST',
            'endpoint': '/api/companies',
            'description': 'Create a new company',
            'auth_required': True
        },
        {
            'method': 'GET',
            'endpoint': '/api/companies/{id}',
            'description': 'Get company details',
            'auth_required': True
        },
        {
            'method': 'GET',
            'endpoint': '/api/status',
            'description': 'Get system status',
            'auth_required': False
        }
    ]

    return render_template('developers/index.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           api_endpoints=api_endpoints,
                           title='Developers')


@developers_bp.route('/api-docs')
def api_docs():
    """Documentación completa de la API"""
    navigation = nav_manager.get_navigation(
        user_authenticated=session.get('user_authenticated', False)
    )
    breadcrumbs = nav_manager.get_breadcrumbs('developers.api_docs')

    return render_template('developers/api_docs.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           title='API Documentation')