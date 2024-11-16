from fastapi import FastAPI,Depends,HTTPException,status
import uvicorn
from schemas import  Salida,   UsuarioSalida, BitacoraInsert, BitacorasSalida, AlumnosSalida

from database import get_db
from sqlalchemy.orm import Session
from typing import Any
from typing import List



import models
from fastapi.security import HTTPBasic,HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware

class Config:
        orm_mode = True  # Esto es necesario para poder trabajar con instancias de SQLAlchemy


app=FastAPI()
security=HTTPBasic()

from fastapi.middleware.cors import CORSMiddleware


# Permitir solicitudes CORS de todos los orígenes (esto es para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)


# Configura CORS
origins = [
    "http://localhost:3000",  # Dominio del frontend
    "http://127.0.0.1:3000",  # Otra posible URL local
]

@app.get('/')
def home():
    return {"mensaje":"Bienvenido a SolicitudesREST"}
async def autenticar(credenciales:HTTPBasicCredentials=Depends(security),
               db:Session=Depends(get_db))->UsuarioSalida:
    return models.autenticar(credenciales.username,credenciales.password,db)


#Bitacoras-------------------------------------------------------------------
@app.post('/bitacoras',tags=["Bitacoras"],summary="Registrar Bitacora",response_model=Salida)
def agregarBitacora(insertarB:BitacoraInsert, db:Session=Depends(get_db))->Any:
    solicitud=models.Bitacoras(nControl=insertarB.nControl, fecha=insertarB.fecha, hEntrada=insertarB.hEntrada,
                               hSalida=insertarB.hSalida, clase=insertarB.clase, siesta=insertarB.siesta,
                                 desayuno=insertarB.desayuno)
    return solicitud.registrarBitacora(db)
#--------------------------------------------------------------------------------

#---------------------------------------------------------------------------

@app.get('/consultarBitacora/{fecha}', tags=["Bitacoras Fecha"], summary="Consultar Bitacoras por Fecha", response_model=BitacorasSalida)
async def consultar_por_fecha(fecha: str, db: Session = Depends(get_db)):
    servicio_bitacoras = models.Bitacoras()
    return servicio_bitacoras.consultarPorFecha(db, fecha)

#------------------------------------------------
# Bitacoras
@app.put('/bitacoras/{idBitacora}', tags=["Bitacoras"], summary="Modificar Bitacora", response_model=Salida)
def modificar_bitacora(idBitacora: int, modificarB: BitacoraInsert, db: Session = Depends(get_db)) -> Any:
    # Instanciamos el modelo de Bitacoras con los datos recibidos
    solicitud = models.Bitacoras(
        nControl=modificarB.nControl,
        fecha=modificarB.fecha,
        hEntrada=modificarB.hEntrada,
        hSalida=modificarB.hSalida,
        clase=modificarB.clase,
        siesta=modificarB.siesta,
        desayuno=modificarB.desayuno
    )
    
    # Llamamos al método para actualizar la bitácora usando el procedimiento almacenado
    resultado = solicitud.actualizarBitacora(db, idBitacora)
    
    # Devolvemos el resultado de la operación
    return resultado

#------------------------------------------


@app.get('/consultarBitacoraAlumno/{nControl}', tags=["Bitacoras por Alumo"], summary="Consultar Bitacoras por Alumno", response_model=BitacorasSalida)
async def consultar_por_Alumno(nControl: str, db: Session = Depends(get_db)):
    servicio_bitacoras = models.Bitacoras()
    return servicio_bitacoras.consultarPorAlumno(db, nControl)

#--------------------------------------------------------------------------------
@app.post('/usuarios/autenticar',tags=["Usuarios"],summary='Autenticacion de un Usuario',response_model=UsuarioSalida)
async def login(usuario:UsuarioSalida=Depends(autenticar))->Any:
     return usuario


#-------------------------------------------------------------------------


@app.get('/consultarAlumnos', tags=["Alumnos"], summary="Consultar Todos los Alumnos", response_model=List[AlumnosSalida])
async def consultar_todos_los_alumnos(db: Session = Depends(get_db)):
    servicio_alumnos = models.Alumnos  # El servicio para consultar alumnos
    return servicio_alumnos.consultarTodos(db)

#-------------------------------------------------------------------------------
@app.get('/consultarTodasBitacoras', tags=["Bitacoras"], summary="Consultar todas las Bitacoras", response_model=BitacorasSalida)
async def consultar_todas_bitacoras(db: Session = Depends(get_db)):
    servicio_bitacoras = models.Bitacoras()
    return servicio_bitacoras.consultarTodasBitacoras(db)

#-------------------------------
#------------------------------------------

# Ruta para eliminar la bitácora
# Bitacoras
@app.delete('/bitacoras/{idBitacora}', tags=["Bitacoras"], summary="Eliminar Bitacora", response_model=Salida)
def eliminar_bitacora(idBitacora: int, db: Session = Depends(get_db)) -> Any:
    # Instanciamos el modelo de Bitacoras
    solicitud = models.Bitacoras()

    # Llamamos al método eliminarBitacora y pasamos la sesión de base de datos y el ID de la bitácora
    return solicitud.eliminarBitacora(db, idBitacora)



if __name__=="__main__":
    uvicorn.run("main:app", host="127.0.0.1", reload=True)

