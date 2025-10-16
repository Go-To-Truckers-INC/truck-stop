import os
import requests
from abc import ABC
from ..core.auth import Auth


class CommonAuth(Auth, ABC):
    def __init__(self):
        self.api_key = os.getenv("FIREBASE_API_KEY")
        self.user = None

    def sign_in_with_email(self, email: str, password: str):
        """
        Autentica usuario con email y contraseña usando Firebase REST API

        Args:
            email (str): Email del usuario
            password (str): Contraseña del usuario

        Returns:
            Dict con información del usuario o error
        """
        try:
            if not email or not password:
                return {"error": "Email y contraseña son requeridos"}

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
            payload = {
                "email": email.strip().lower(),
                "password": password,
                "returnSecureToken": True
            }

            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if "idToken" in data:
                self.user = data
                return {"success": True, "user": data}
            else:
                error_msg = data.get("error", {}).get("message", "Error de autenticación")
                return {"error": error_msg}

        except requests.exceptions.Timeout:
            return {"error": "Timeout en la conexión"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}

    # Implementación de métodos abstractos de Auth
    def sign_in(self, email: str, password: str):
        """Alias para sign_in_with_email"""
        return self.sign_in_with_email(email, password)

    def sign_out(self):
        self.user = None
        return {"success": True, "message": "Usuario desconectado"}

    def forgot_password(self, email: str):
        """
        Envia correo para restablecer contraseña

        Args:
            email (str): Email del usuario

        Returns:
            Dict con resultado de la operación
        """
        try:
            if not email:
                return {"error": "Email requerido"}

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.api_key}"
            payload = {"requestType": "PASSWORD_RESET", "email": email}

            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if "email" in data:
                return {"success": True, "message": "Correo para restablecer contraseña enviado"}
            else:
                error_msg = data.get("error", {}).get("message", "Error desconocido")
                return {"error": error_msg}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}

    def reset_password(self, oob_code: str, new_password: str):
        """
        Restablece la contraseña usando código OOB

        Args:
            oob_code (str): Código de restablecimiento
            new_password (str): Nueva contraseña

        Returns:
            Dict con resultado de la operación
        """
        try:
            if not oob_code or not new_password:
                return {"error": "Código y nueva contraseña son requeridos"}

            if len(new_password) < 6:
                return {"error": "La contraseña debe tener al menos 6 caracteres"}

            url = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={self.api_key}"
            payload = {"oobCode": oob_code, "newPassword": new_password}

            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if "email" in data:
                return {"success": True, "message": "Contraseña restablecida con éxito"}
            else:
                error_msg = data.get("error", {}).get("message", "Error desconocido")
                return {"error": error_msg}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error de conexión: {str(e)}"}