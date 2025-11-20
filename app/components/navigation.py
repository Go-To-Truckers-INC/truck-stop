from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from flask import request, session, redirect, url_for


@dataclass
class NavItem:
    """Modelo para elementos de navegación"""
    name: str
    endpoint: str
    title: str
    requires_auth: bool = False
    requires_guest: bool = False
    icon: str = ""
    children: List['NavItem'] = None


class NavigationManager:
    """
    Gestor de navegación para la aplicación Truck Stop
    """

    def __init__(self):
        self.nav_items: List[NavItem] = []
        self._setup_navigation()

    def _setup_navigation(self):
        """Configura la estructura de navegación"""
        self.nav_items = [
            NavItem(
                name="signin",
                endpoint="auth.signin",
                title="Sign In",
                requires_guest=True,
                icon="🔐"
            ),
            NavItem(
                name="register",
                endpoint="auth.register",
                title="Register",
                requires_guest=True,
                icon="📝"
            ),
            NavItem(
                name="dashboard",
                endpoint="dashboard.index",
                title="Dashboard",
                requires_auth=True,
                icon="📊"
            ),
            NavItem(
                name="companies",
                endpoint="companies.index",
                title="Companies",
                requires_auth=True,
                icon="🏢"
            ),
            NavItem(
                name="developers",
                endpoint="developers.index",
                title="Developers",
                requires_auth=False,
                icon="👨‍💻"
            )
        ]

    def get_navigation(self, user_authenticated: bool = False) -> List[Dict[str, Any]]:
        """
        Obtiene los elementos de navegación filtrados por autenticación

        Args:
            user_authenticated: Si el usuario está autenticado

        Returns:
            Lista de elementos de navegación
        """
        filtered_nav = []

        for item in self.nav_items:
            # Verificar condiciones de acceso
            if item.requires_auth and not user_authenticated:
                continue
            if item.requires_guest and user_authenticated:
                continue

            filtered_nav.append({
                'name': item.name,
                'endpoint': item.endpoint,
                'title': item.title,
                'icon': item.icon,
                'is_active': self._is_active_route(item.endpoint),
                'children': [
                    {
                        'name': child.name,
                        'endpoint': child.endpoint,
                        'title': child.title,
                        'icon': child.icon,
                        'is_active': self._is_active_route(child.endpoint)
                    }
                    for child in (item.children or [])
                ] if item.children else None
            })

        return filtered_nav

    def _is_active_route(self, endpoint: str) -> bool:
        """
        Verifica si la ruta actual coincide con el endpoint

        Args:
            endpoint: Nombre del endpoint a verificar

        Returns:
            bool: True si es la ruta activa
        """
        try:
            return endpoint == request.endpoint
        except RuntimeError:
            # Fuera de contexto de request
            return False

    def get_breadcrumbs(self, current_endpoint: str) -> List[Dict[str, str]]:
        """
        Genera breadcrumbs para la ruta actual
        """
        breadcrumbs = [
            {'title': 'Home', 'url': '/', 'endpoint': 'main.index'}
        ]

        # SOLO TUS RUTAS EXISTENTES
        endpoint_map = {
            'auth.signin': 'Sign In',
            'auth.register': 'Register',
            'dashboard.index': 'Dashboard',
            'companies.index': 'Companies',
            'companies.create': 'Create Company',
            'companies.detail': 'Company Details',
            'developers.index': 'Developers'
        }

        if current_endpoint in endpoint_map and current_endpoint != 'main.index':
            breadcrumbs.append({
                'title': endpoint_map[current_endpoint],
                'url': self._get_url_for_endpoint(current_endpoint),
                'endpoint': current_endpoint
            })

        return breadcrumbs

    def _get_url_for_endpoint(self, endpoint: str) -> str:
        """Obtiene la URL para un endpoint"""
        endpoint_url_map = {
            'main.index': '/',
            'auth.signin': '/auth/signin',
            'auth.register': '/auth/register',
            'dashboard.index': '/dashboard',
            'companies.index': '/companies',
            'companies.create': '/companies/create',
            'developers.index': '/developers'
        }
        return endpoint_url_map.get(endpoint, '/')

    def should_redirect(self, user_authenticated: bool, endpoint: str) -> Optional[str]:
        """
        Verifica si se necesita redirección basado en autenticación

        Args:
            user_authenticated: Si el usuario está autenticado
            endpoint: Endpoint actual

        Returns:
            str: Endpoint de redirección o None
        """
        nav_item = next((item for item in self.nav_items if item.endpoint == endpoint), None)

        if nav_item:
            if nav_item.requires_auth and not user_authenticated:
                return 'auth.signin'
            elif nav_item.requires_guest and user_authenticated:
                return 'dashboard.index'

        return None