import os
import json
import firebase_admin

from firebase_admin import credentials
from typing import Any, Dict
from ..core.sdk import SDK


class FirebaseSDK(SDK):
    """
    Implementación del SDK para Firebase usando variables de entorno
    """

    def __init__(self):
        self._app = None
        self._config = {}
        self._initialized = False

    def _load_from_env(self) -> Dict[str, Any]:
        """
        Carga la configuración de Firebase desde variables de entorno

        Returns:
            Dict con la configuración de Firebase
        """
        # Opción 1: Service account JSON completo desde variable de entorno
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            try:
                return {
                    'service_account_json': json.loads(service_account_json)
                }
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}")

        # Opción 2: Variables individuales
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        if private_key:
            return {
                'project_id': os.getenv('FIREBASE_PROJECT_ID'),
                'private_key': private_key.replace('\\n', '\n'),
                'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
                'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                'client_id': os.getenv('FIREBASE_CLIENT_ID')
            }

        # Opción 3: Archivo de credenciales
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if cred_path and os.path.exists(cred_path):
            return {
                'credential_path': cred_path
            }

        raise ValueError("No se encontraron variables de entorno de Firebase configuradas")

    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Inicializa Firebase Admin SDK desde variables de entorno o configuración proporcionada

        Args:
            config: Configuración opcional (si no se proporciona, usa variables de entorno)

        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            if self._initialized:
                return True

            # Cargar configuración desde variables de entorno si no se proporciona
            if config is None:
                config = self._load_from_env()

            self._config = config.copy()

            # Verificar que no hay apps inicializadas
            if not firebase_admin._apps:
                # Método 1: Credenciales desde JSON string
                if 'service_account_json' in config:
                    cred = credentials.Certificate(config['service_account_json'])

                # Método 2: Credenciales desde archivo
                elif 'credential_path' in config:
                    cred = credentials.Certificate(config['credential_path'])

                # Método 3: Parámetros individuales
                elif all(key in config for key in ['project_id', 'private_key', 'client_email']):
                    service_account_info = {
                        "type": "service_account",
                        "project_id": config['project_id'],
                        "private_key_id": config.get('private_key_id', ''),
                        "private_key": config['private_key'],
                        "client_email": config['client_email'],
                        "client_id": config.get('client_id', ''),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": config.get('client_x509_cert_url', ''),
                        "universe_domain": "googleapis.com"
                    }
                    cred = credentials.Certificate(service_account_info)
                else:
                    raise ValueError("Configuración de Firebase incompleta")

                # Inicializar la app
                self._app = firebase_admin.initialize_app(cred)
                self._initialized = True
                return True
            else:
                # Ya hay una app inicializada
                self._app = firebase_admin.get_app()
                self._initialized = True
                return True

        except Exception as e:
            print(f"❌ Error inicializando Firebase SDK: {e}")
            self._initialized = False
            return False

    def is_initialized(self) -> bool:
        """Verifica si Firebase está inicializado"""
        return self._initialized and self._app is not None

    def get_client(self) -> Any:
        """
        Retorna el cliente de Firebase Admin

        Returns:
            Firebase App instance
        """
        return self._app

    def cleanup(self) -> bool:
        """Limpia recursos de Firebase"""
        try:
            if self._app:
                firebase_admin.delete_app(self._app)
                self._app = None
            self._initialized = False
            return True
        except Exception as e:
            print(f"❌ Error limpiando Firebase SDK: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """Retorna la configuración actual (sin datos sensibles)"""
        safe_config = self._config.copy()
        # Ocultar datos sensibles
        if 'private_key' in safe_config:
            safe_config['private_key'] = '***HIDDEN***'
        if 'service_account_json' in safe_config and 'private_key' in safe_config['service_account_json']:
            safe_config['service_account_json']['private_key'] = '***HIDDEN***'
        return safe_config