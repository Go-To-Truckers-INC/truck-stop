from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.components.navigation import NavigationManager

# Crear blueprint de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
nav_manager = NavigationManager()


@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    """Página de inicio de sesión"""
    navigation = nav_manager.get_navigation(user_authenticated=False)
    breadcrumbs = nav_manager.get_breadcrumbs('auth.signin')

    if request.method == 'POST':
        # Aquí iría la lógica de autenticación con Firebase
        email = request.form.get('email')
        password = request.form.get('password')

        # Simulación de autenticación exitosa
        if email and password:
            session['user_authenticated'] = True
            session['user_email'] = email
            flash('Successfully signed in!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('auth/signin.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           title='Sign In')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    navigation = nav_manager.get_navigation(user_authenticated=False)
    breadcrumbs = nav_manager.get_breadcrumbs('auth.register')

    if request.method == 'POST':
        # Aquí iría la lógica de registro con Firebase
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
        elif email and password:
            # Simulación de registro exitoso
            session['user_authenticated'] = True
            session['user_email'] = email
            flash('Successfully registered!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Please fill all fields', 'error')

    return render_template('auth/register.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           title='Register')


@auth_bp.route('/signout')
def signout():
    """Cerrar sesión"""
    session.clear()
    flash('You have been signed out', 'info')
    return redirect(url_for('auth.signin'))