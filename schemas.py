from pydantic import BaseModel,Field
from typing import List, Optional
from datetime import date, time, datetime

class Config:
        orm_mode = True  # Esto es necesario para poder trabajar con instancias de SQLAlchemy

class Salida(BaseModel):
    estatus:str=Field(default="")
    mensaje:str=Field(default="")

class Usuario(BaseModel):
    id:Optional[int]=None
    usuario:Optional[str]=None
    contraseniaE:Optional[str]=None
    tipoUsuario:Optional[str]=None
    status:Optional[str]=None
   


class UsuarioSalida(Salida):
    usuario:Optional[Usuario]=None

class UsuarioLogin(BaseModel):
    usuario: str
    contraseniaE: str

#-------------------------------------insertar usuarios
class UsuarioInsert(BaseModel):
    usuario:str
    contraseniaE:str
    tipoUsuario:str
    status:str

#-------------------------------------insertar Bitacora
class BitacoraInsert(BaseModel):
    nControl:str
    fecha:date
    hEntrada:time
    hSalida:time
    clase:str
    siesta:str
    desayuno:str



class Alumnos(BaseModel):
    # `idAlumno`, `nombreAlumno`, `aPaterno`, `aMaterno`, `fNacimiento`, `curp`, `domicilio`, `nControl`, `idUsuario`
   
    nombreAlumno:Optional[str]=None
    aPaterno:Optional[str]=None


class AlumnosPydantic(BaseModel):
    nControl: str
    nombreAlumno: str
    aPaterno: str

    class Config:
        from_attributes = True

        
    
class BitacoraSelect(BaseModel):
    alumno: Optional[AlumnosPydantic] = None  # Cambiado a AlumnosPydantic
    idBitacora:Optional[int] = None
    fecha: Optional[date] = None
    hEntrada: Optional[time] = None
    hSalida: Optional[time] = None
    clase: Optional[str] = None
    siesta: Optional[str] = None
    desayuno: Optional[str] = None

    class Config:
        from_attributes = True



    

class BitacorasSalida(Salida):
    bitacoras:Optional[List[BitacoraSelect]]=None


class AlumnosSalida(BaseModel):
    idAlumno: int
    nombreAlumno: str
    nControl: str
    aPaterno: str
    aMaterno: str

    class Config:
        from_attributes=True






