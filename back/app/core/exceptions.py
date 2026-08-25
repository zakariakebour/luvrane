# Excepcion base del sistema
class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# Errores de autenticacion
class UnauthorizedException(AppException):
    def __init__(self, message: str = "Non autorisé"):
        super().__init__(message, status_code=401)

# Errores de recurso no encontrado
class NotFoundException(AppException):
    def __init__(self, message: str = "Ressource introuvable"):
        super().__init__(message, status_code=404)

# Errores de conflicto (ya existe)
class ConflictException(AppException):
    def __init__(self, message: str = "Ressource déjà existante"):
        super().__init__(message, status_code=409)

# Errores de permisos
class ForbiddenException(AppException):
    def __init__(self, message: str = "Accès interdit"):
        super().__init__(message, status_code=403)

# Errores de validacion
class ValidationException(AppException):
    def __init__(self, message: str = "Données invalides"):
        super().__init__(message, status_code=422)