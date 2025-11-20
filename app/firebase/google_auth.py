import os
import firebase_admin
from firebase_admin import credentials, auth
from abc import ABC
from ..core.auth import Auth


class GoogleAuth(Auth, ABC):
    def __init__(self):
        self._initialize_firebase()
        self.user = None

    def _initialize_firebase(self):
        """Inicializa Firebase Admin SDK"""
        if not firebase_admin._apps:
            # Para la clave privada del .env, necesitamos manejarla correctamente
            service_account_info = {
                "type": "service_account",
                "project_id": "gtt-truck-stop",
                "private_key_id": "87999a934c500ea064a81ebed73351adb46e3a66",
                "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": "firebase-adminsdk-fbsvc@gtt-truck-stop.iam.gserviceaccount.com",
                "client_id": "110052854869427047912",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40gtt-truck-stop.iam.gserviceaccount.com"
            }

            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)

    def sign_in_with_google(self, id_token: str):
        """
        Autentica usuario usando Google OAuth token

        Args:
            id_token (str): Token ID de Google OAuth

        Returns:
            Dict con información del usuario o error
        """
        try:
            if not id_token:
                return {"error": "Token ID requerido"}

            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            user = auth.get_user(uid)

            self.user = {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'photo_url': user.photo_url
            }

            return {"success": True, "user": self.user}

        except auth.InvalidIdTokenError:
            return {"error": "Token inválido"}
        except auth.ExpiredIdTokenError:
            return {"error": "Token expirado"}
        except auth.RevokedIdTokenError:
            return {"error": "Token revocado"}
        except Exception as e:
            return {"error": f"Error de autenticación: {str(e)}"}

    # Implementación de métodos abstractos de Auth
    def sign_in(self, email: str, password: str):
        """No soportado para Google Auth - usar sign_in_with_google"""
        return {"error": "Use sign_in_with_google para autenticación con Google"}

    def sign_out(self):
        self.user = None
        return {"success": True, "message": "Usuario desconectado"}

    def forgot_password(self, email: str):
        """No aplicable para Google Auth"""
        return {"error": "No soportado para autenticación con Google"}

    def reset_password(self, oob_code: str, new_password: str):
        """No aplicable para Google Auth"""
        return {"error": "No soportado para autenticación con Google"}