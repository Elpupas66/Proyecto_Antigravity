from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    # Definición de configuraciones con valores por defecto seguros (cierre por defecto)
    environment: str = Field(default="development", alias="ENVIRONMENT")
    allow_real_execution: bool = Field(default=False, alias="ALLOW_REAL_EXECUTION")
    require_approval: bool = Field(default=True, alias="REQUIRE_APPROVAL")
    
    # Especificamos que lea desde el archivo .env en la raíz del proyecto
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

def validate_execution_safety() -> None:
    """
    Función central que valida si la ejecución real está permitida.
    Levanta una excepción si se intenta saltar los candados en un entorno no productivo.
    """
    if settings.allow_real_execution:
        if settings.environment != "production":
            raise PermissionError("Ejecución real bloqueada: el entorno no es 'production'.")
        if not settings.require_approval:
            raise PermissionError("Ejecución real bloqueada: la aprobación (REQUIRE_APPROVAL) debe ser obligatoria.")
