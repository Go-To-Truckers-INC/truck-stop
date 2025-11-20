from abc import ABC, abstractmethod

class Auth(ABC):
    @abstractmethod
    def sign_in(self, email: str, password: str):
        """Iniciar sesión con email y contraseña"""
        pass

    @abstractmethod
    def sign_out(self):
        """Cerrar sesión del usuario"""
        pass

    @abstractmethod
    def forgot_password(self, email: str):
        """Enviar correo para restablecer contraseña"""
        pass

    @abstractmethod
    def reset_password(self, oob_code: str, new_password: str):
        """Restablecer la contraseña usando código y nueva contraseña"""
        pass