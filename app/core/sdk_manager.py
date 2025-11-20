from typing import Dict, Any, Optional
from .sdk import SDK


class SDKManager:
    """
    Gestor centralizado para múltiples SDKs
    """

    def __init__(self):
        self._sdks: Dict[str, SDK] = {}

    def register_sdk(self, name: str, sdk: SDK, config: Dict[str, Any] = None) -> bool:
        """
        Registra y inicializa un SDK

        Args:
            name: Nombre identificador del SDK
            sdk: Instancia del SDK
            config: Configuración opcional para el SDK

        Returns:
            bool: True si el registro fue exitoso
        """
        try:
            if sdk.initialize(config):
                self._sdks[name] = sdk
                return True
            return False
        except Exception as e:
            print(f"Error registrando SDK {name}: {e}")
            return False

    def get_sdk(self, name: str) -> Optional[SDK]:
        """Obtiene un SDK por nombre"""
        return self._sdks.get(name)

    def is_initialized(self, name: str) -> bool:
        """Verifica si un SDK está inicializado"""
        sdk = self.get_sdk(name)
        return sdk.is_initialized() if sdk else False

    def cleanup_all(self):
        """Limpia todos los SDKs registrados"""
        for name, sdk in self._sdks.items():
            sdk.cleanup()
        self._sdks.clear()

    def get_status(self) -> Dict[str, Any]:
        """Retorna el estado de todos los SDKs"""
        status = {}
        for name, sdk in self._sdks.items():
            status[name] = {
                'initialized': sdk.is_initialized(),
                'config': sdk.get_config()
            }
        return status