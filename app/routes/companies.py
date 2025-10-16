from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.components.navigation import NavigationManager

# Crear blueprint de companies
companies_bp = Blueprint('companies', __name__, url_prefix='/companies')
nav_manager = NavigationManager()

# Datos de ejemplo según el nuevo modelo
sample_companies = [
    {
        'record_id': 1001,
        'hubspot_company_name': 'TechCorp Logistics Inc.',
        'comercial_name': 'TechCorp Logistics',
        'state_region': 'California',
        'average_days_to_pay': 45,
        'credit_score': 85,
        'companies_reporting': 12,
        'website_url': 'https://techcorplogistics.com'
    },
    {
        'record_id': 1002,
        'hubspot_company_name': 'Global Shipping Partners LLC',
        'comercial_name': 'Global Shipping',
        'state_region': 'Texas',
        'average_days_to_pay': 30,
        'credit_score': 92,
        'companies_reporting': 8,
        'website_url': 'https://globalshipping.com'
    },
    {
        'record_id': 1003,
        'hubspot_company_name': 'Midwest Freight Solutions',
        'comercial_name': 'Midwest Freight',
        'state_region': 'Illinois',
        'average_days_to_pay': 60,
        'credit_score': 78,
        'companies_reporting': 5,
        'website_url': 'https://midwestfreight.com'
    },
    {
        'record_id': 1004,
        'hubspot_company_name': 'Pacific Coast Transport Co.',
        'comercial_name': 'Pacific Transport',
        'state_region': 'Washington',
        'average_days_to_pay': 35,
        'credit_score': 88,
        'companies_reporting': 15,
        'website_url': 'https://pacifictransport.com'
    },
    {
        'record_id': 1005,
        'hubspot_company_name': 'Eastern Logistics Group',
        'comercial_name': 'Eastern Logistics',
        'state_region': 'New York',
        'average_days_to_pay': 55,
        'credit_score': 72,
        'companies_reporting': 6,
        'website_url': 'https://easternlogistics.com'
    }
]


@companies_bp.route('/')
def index():
    """Lista de todas las empresas según el nuevo modelo"""
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.signin'))

    navigation = nav_manager.get_navigation(user_authenticated=True)
    breadcrumbs = nav_manager.get_breadcrumbs('companies.index')

    search_query = request.args.get('search', '')

    # Filtrar empresas basado en búsqueda
    if search_query:
        filtered_companies = [
            company for company in sample_companies
            if search_query.lower() in company['hubspot_company_name'].lower() or
               search_query.lower() in company['comercial_name'].lower() or
               search_query.lower() in company['state_region'].lower()
        ]
    else:
        filtered_companies = sample_companies

    return render_template('companies/index.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           companies=filtered_companies,
                           search_query=search_query,
                           title='Companies')


@companies_bp.route('/<int:record_id>')
def detail(record_id):
    """Detalles de una empresa específica según el nuevo modelo"""
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.signin'))

    navigation = nav_manager.get_navigation(user_authenticated=True)
    breadcrumbs = nav_manager.get_breadcrumbs('companies.detail')

    company = next((c for c in sample_companies if c['record_id'] == record_id), None)

    if not company:
        flash('Company not found', 'error')
        return redirect(url_for('companies.index'))

    return render_template('companies/detail.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           company=company,
                           title=f"Company - {company['comercial_name']}")


@companies_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Crear nueva empresa según el nuevo modelo"""
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.signin'))

    navigation = nav_manager.get_navigation(user_authenticated=True)
    breadcrumbs = nav_manager.get_breadcrumbs('companies.create')

    if request.method == 'POST':
        # Lógica para crear la empresa con el nuevo modelo
        hubspot_company_name = request.form.get('hubspot_company_name')
        comercial_name = request.form.get('comercial_name')
        state_region = request.form.get('state_region')
        average_days_to_pay = request.form.get('average_days_to_pay')
        credit_score = request.form.get('credit_score')
        companies_reporting = request.form.get('companies_reporting')
        website_url = request.form.get('website_url')

        if hubspot_company_name and comercial_name:
            # En una app real, aquí guardarías en la base de datos
            new_company = {
                'record_id': len(sample_companies) + 1001,
                'hubspot_company_name': hubspot_company_name,
                'comercial_name': comercial_name,
                'state_region': state_region,
                'average_days_to_pay': int(average_days_to_pay) if average_days_to_pay else 0,
                'credit_score': int(credit_score) if credit_score else 0,
                'companies_reporting': int(companies_reporting) if companies_reporting else 0,
                'website_url': website_url or '#'
            }
            sample_companies.append(new_company)

            flash(f'Company "{comercial_name}" created successfully!', 'success')
            return redirect(url_for('companies.index'))
        else:
            flash('Please fill all required fields', 'error')

    return render_template('companies/create.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           title='Create Company')