from flask import Blueprint, render_template, session, redirect, url_for
from app.components.navigation import NavigationManager

# Crear blueprint del dashboard
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
nav_manager = NavigationManager()

# Datos de ejemplo (en una app real esto vendría de tu base de datos)
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
    },
    {
        'record_id': 1006,
        'hubspot_company_name': 'Southern Trucking Co.',
        'comercial_name': 'Southern Trucking',
        'state_region': 'Florida',
        'average_days_to_pay': 25,
        'credit_score': 95,
        'companies_reporting': 20,
        'website_url': 'https://southerntrucking.com'
    }
]


def calculate_dashboard_metrics(companies):
    """Calcula métricas del dashboard basadas en los datos de empresas"""

    total_companies = len(companies)

    # Métricas de días de pago
    avg_days_to_pay = sum(c['average_days_to_pay'] for c in companies) / total_companies if total_companies > 0 else 0
    fast_payers = len([c for c in companies if c['average_days_to_pay'] <= 30])
    slow_payers = len([c for c in companies if c['average_days_to_pay'] > 45])

    # Métricas de crédito
    avg_credit_score = sum(c['credit_score'] for c in companies) / total_companies if total_companies > 0 else 0
    excellent_credit = len([c for c in companies if c['credit_score'] >= 85])
    poor_credit = len([c for c in companies if c['credit_score'] < 70])

    # Métricas de reporting
    total_reporting = sum(c['companies_reporting'] for c in companies)
    avg_reporting = total_reporting / total_companies if total_companies > 0 else 0
    well_reported = len([c for c in companies if c['companies_reporting'] >= 10])

    # Distribución por región
    regions = {}
    for company in companies:
        region = company['state_region']
        regions[region] = regions.get(region, 0) + 1

    top_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        'total_companies': total_companies,
        'avg_days_to_pay': round(avg_days_to_pay, 1),
        'fast_payers': fast_payers,
        'slow_payers': slow_payers,
        'avg_credit_score': round(avg_credit_score, 1),
        'excellent_credit': excellent_credit,
        'poor_credit': poor_credit,
        'total_reporting': total_reporting,
        'avg_reporting': round(avg_reporting, 1),
        'well_reported': well_reported,
        'top_regions': top_regions
    }


@dashboard_bp.route('/')
def index():
    """Página principal del dashboard con métricas reales"""
    # Verificar autenticación
    if not session.get('user_authenticated'):
        return redirect(url_for('auth.signin'))

    navigation = nav_manager.get_navigation(user_authenticated=True)
    breadcrumbs = nav_manager.get_breadcrumbs('dashboard.index')

    # Calcular métricas
    metrics = calculate_dashboard_metrics(sample_companies)

    # Empresas recientes (últimas 3)
    recent_companies = sample_companies[-3:] if len(sample_companies) >= 3 else sample_companies

    # Empresas con mejor crédito
    top_credit_companies = sorted(sample_companies, key=lambda x: x['credit_score'], reverse=True)[:3]

    # Empresas que pagan más rápido
    fast_paying_companies = sorted(sample_companies, key=lambda x: x['average_days_to_pay'])[:3]

    return render_template('dashboard/index.html',
                           navigation=navigation,
                           breadcrumbs=breadcrumbs,
                           metrics=metrics,
                           recent_companies=recent_companies,
                           top_credit_companies=top_credit_companies,
                           fast_paying_companies=fast_paying_companies,
                           title='Dashboard')