import os
import json
import firebase_admin
import logging

from firebase_admin import credentials
from typing import Any, Dict, Optional
from ..core.sdk import SDK

logger = logging.getLogger(__name__)

class FirebaseSDK(SDK):
    """
    Implementación del SDK para Firebase con manejo robusto de errores
    """

    def __init__(self):
        self._app = None
        self._config = {}
        self._initialized = False
        self._error = None

    def _load_from_env(self) -> Dict[str, Any]:
        """
        Carga la configuración de Firebase desde variables de entorno
        """
        try:
            # Opción 1: Service account JSON completo desde variable de entorno
            service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if service_account_json:
                try:
                    return {
                        'service_account_json': json.loads(service_account_json)
                    }
                except json.JSONDecodeError as e:
                    self._error = f"Error parsing FIREBASE_SERVICE_ACCOUNT_JSON: {e}"
                    logger.error(self._error)
                    return {}

            # Opción 2: Variables individuales
            private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            if private_key:
                private_key = private_key.replace('\\n', '\n')

            config = {
                'project_id': os.getenv('FIREBASE_PROJECT_ID'),
                'private_key': private_key,
                'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
                'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                'client_id': os.getenv('FIREBASE_CLIENT_ID')
            }

            # Verificar configuración mínima requerida
            if not config.get('project_id') or not config.get('private_key') or not config.get('client_email'):
                self._error = "Configuración mínima de Firebase no encontrada en variables de entorno"
                logger.warning(self._error)
                return {}

            return config

        except Exception as e:
            self._error = f"Error cargando configuración desde entorno: {e}"
            logger.error(self._error)
            return {}

    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Inicializa Firebase Admin SDK con manejo robusto de errores
        """
        try:
            if self._initialized:
                return True

            # Cargar configuración desde variables de entorno si no se proporciona
            if config is None:
                config = self._load_from_env()

            # Si no hay configuración válida, no inicializar
            if not config:
                logger.warning("No se pudo cargar configuración para Firebase SDK")
                self._initialized = False
                return False

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
                    self._error = "Configuración de Firebase incompleta"
                    logger.error(self._error)
                    self._initialized = False
                    return False

                # Inicializar la app
                self._app = firebase_admin.initialize_app(cred)
                self._initialized = True
                logger.info("✅ Firebase SDK inicializado correctamente")
                return True
            else:
                # Ya hay una app inicializada
                self._app = firebase_admin.get_app()
                self._initialized = True
                logger.info("✅ Firebase SDK ya estaba inicializado")
                return True

        except Exception as e:
            self._error = f"Error inicializando Firebase SDK: {e}"
            logger.error(self._error)
            self._initialized = False
            return False

    def is_initialized(self) -> bool:
        """Verifica si Firebase está inicializado"""
        return self._initialized and self._app is not None

    def get_error(self) -> Optional[str]:
        """Retorna el último error ocurrido"""
        return self._error

    def get_client(self) -> Any:
        """
        Retorna el cliente de Firebase Admin si está inicializado
        """
        if not self.is_initialized():
            raise RuntimeError("Firebase SDK no está inicializado")
        return self._app

    def get_client_safe(self) -> Optional[Any]:
        """
        Retorna el cliente de Firebase Admin de forma segura (puede retornar None)
        """
        return self._app if self.is_initialized() else None

    def cleanup(self) -> bool:
        """Limpia recursos de Firebase"""
        try:
            if self._app:
                firebase_admin.delete_app(self._app)
                self._app = None
            self._initialized = False
            self._error = None
            logger.info("Firebase SDK limpiado correctamente")
            return True
        except Exception as e:
            self._error = f"Error limpiando Firebase SDK: {e}"
            logger.error(self._error)
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