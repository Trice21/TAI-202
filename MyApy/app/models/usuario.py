from pydantic import BaseModel, Field
from typing import Optional
#******************************
# Modelo de validación de usuarios
#******************************
class CrearUsuario(BaseModel):

    nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
    edad: int = Field(..., ge=1, le=123, description="Edad valida entre 1 y 123")
class PatchUsuario(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=50, example="Juanita")
    edad: Optional[int] = Field(None, ge=1, le=123, description="Edad valida entre 1 y 123")


