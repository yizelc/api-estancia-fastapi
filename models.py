from database import Base
from sqlalchemy import Column,Integer,String,text,Date, Time
from sqlalchemy.orm import Session
from datetime import datetime
from schemas import Salida,UsuarioSalida,Usuario, BitacorasSalida, Alumnos, BitacoraSelect, AlumnosSalida, AlumnosPydantic
import schemas

from fastapi import  HTTPException



#API REST PARA BITACORAS------------------------------------------------

class Bitacoras(Base):
    __tablename__='bitacoras'
    idBitacora=Column(Integer,primary_key=True)
    nControl=Column(String(6),nullable=False)
    fecha=Column(Date)
    hEntrada=Column(Time)
    hSalida=Column(Time)
    clase=Column(String)
    siesta=Column(String)
    desayuno=Column(String)




    def to_schema(self, objeto):

       
        alumno=schemas.Alumnos()
        alumno.nombreAlumno=objeto.nombreAlumno
        alumno.aPaterno=objeto.aPaterno
        
        bitacora=schemas.BitacoraSelect()
        bitacora.idBitacora=objeto.idBitacora
        bitacora.nControl=objeto.nControl
        bitacora.fecha=objeto.fecha
        bitacora.hEntrada=objeto.hEntrada
        bitacora.hSalida=objeto.hSalida
        bitacora.siesta=objeto.siesta
        bitacora.clase=objeto.clase
        bitacora.desayuno=objeto.desayuno
        return bitacora

    def registrarBitacora(self,db):
        datos_entrada={"p_nControl":self.nControl,"p_fecha":self.fecha,
                       "p_hEntrada":self.hEntrada, "p_hSalida":self.hSalida,
                         "p_clase":self.clase, "p_siesta":self.siesta, "p_desayuno": self.desayuno}
        db.execute(text('call insertar_bitacora(:p_nControl, :p_fecha, :p_hEntrada, :p_hSalida, :p_clase, :p_siesta, :p_desayuno,@p_estatus,@p_mensaje)'),
                   datos_entrada)
        db.commit()
        respuesta=db.execute(text('select @p_estatus,@p_mensaje')).fetchone()
        salida=Salida()
        salida.estatus=respuesta[0]
        salida.mensaje=respuesta[1]
        return salida.dict()
    
#------------------------------------------------
#COMNSULTAR TODAS LA BITACORAS 


#-----------MODIFICAR BITACORA-------------------------------------------------   
# Método para actualizar la bitácora usando procedimiento almacenado
    def actualizarBitacora(self, db: Session, idBitacora: int):
        try:
            # Parámetros para el procedimiento almacenado
            params = {
                "p_idBitacora": idBitacora,
                "p_nControl": self.nControl,
                "p_fecha": self.fecha,
                "p_hEntrada": self.hEntrada,
                "p_hSalida": self.hSalida,
                "p_clase": self.clase,
                "p_siesta": self.siesta,
                "p_desayuno": self.desayuno
            }

            # Ejecutamos el procedimiento almacenado
            db.execute(
                text('CALL actualizar_bitacora(:p_idBitacora, :p_nControl, :p_fecha, :p_hEntrada, :p_hSalida, :p_clase, :p_siesta, :p_desayuno, @p_estatus, @p_mensaje)'),
                params
            )
            db.commit()

            # Recuperamos el mensaje de salida del procedimiento
            respuesta = db.execute(text('SELECT @p_estatus, @p_mensaje')).fetchone()
            estatus = respuesta[0] if respuesta[0] is not None else "Error"
            mensaje = respuesta[1] if respuesta[1] is not None else "Error al recuperar el mensaje"

            # Devolvemos el resultado
            return {"estatus": estatus, "mensaje": mensaje}

        except Exception as e:
            db.rollback()  # Revertir cambios en caso de error
            return {"estatus": "Error", "mensaje": f"Error al actualizar la bitácora: {str(e)}"}


#--------------------------------------------
    def consultarPorFecha(self, db: Session, fecha: str):
        salida = BitacorasSalida()
        try:
            fecha_consulta = datetime.strptime(fecha, '%Y-%m-%d')
            lista = db.query(VistaBitacorasAlumnos).filter(VistaBitacorasAlumnos.fecha == fecha_consulta).all()
            listaSolicitudes = []
            
            for s in lista:
                alumno_data = Alumnos(nombreAlumno=s.nombreAlumno, aPaterno=s.aPaterno)

            # Crea un objeto BitacoraSelect
                objSol = BitacoraSelect(
                    alumno=alumno_data,  # Asigna el objeto Alumnos
                    fecha=s.fecha,
                    hEntrada=s.hEntrada,
                    hSalida=s.hSalida,
                    clase=s.clase,
                    siesta=s.siesta,
                    desayuno=s.desayuno
                )
                listaSolicitudes.append(objSol)
            salida.bitacoras = listaSolicitudes
            salida.estatus = 'OK'
            salida.mensaje = 'Listado de Bitacoras'

        except Exception as e:
            salida.bitacoras = []
            salida.estatus = 'Error'
            salida.mensaje = f'Error al consultar las Bitacoras: {str(e)}'

        return salida.dict()
    
#   -----------------------------------------------

# Método para eliminar una bitácora
    def eliminarBitacora(self, db, idBitacora):
        salida = Salida()
        try:
            # Parámetros para el procedimiento almacenado
            datos_entrada = {
                "p_idBitacora": idBitacora
            }
            
            # Ejecutamos el procedimiento almacenado para eliminar la bitácora
            db.execute(text('CALL eliminar_bitacora(:p_idBitacora, @p_estatus, @p_mensaje)'), datos_entrada)
            db.commit()
            
            # Obtenemos el estatus y mensaje de la ejecución del procedimiento
            respuesta = db.execute(text('SELECT @p_estatus, @p_mensaje')).fetchone()
            
            # Asignamos el estatus y mensaje al objeto Salida
            salida.estatus = respuesta[0]
            salida.mensaje = respuesta[1]
            
        except Exception as e:
            salida.estatus = 'Error'
            salida.mensaje = f'Error al eliminar la bitácora: {str(e)}'
        
        return salida.dict()


#   #----------------------------------------------------

    def consultarPorAlumno(self, db: Session, nControl: str):
        salida = BitacorasSalida()
        try:
            lista = db.query(VistaBitacorasAlumnos).filter(VistaBitacorasAlumnos.nControl == nControl).all()
            listaSolicitudes = []

            for s in lista:
                # Aquí creamos el objeto AlumnosPydantic, que es lo que se espera en BitacoraSelect
                alumno_data = AlumnosPydantic(
                    nControl=s.nControl,
                    nombreAlumno=s.nombreAlumno,
                    aPaterno=s.aPaterno
                )

                # Crea un objeto BitacoraSelect
                objSol = BitacoraSelect(
                    alumno=alumno_data,  # Asigna el objeto AlumnosPydantic
                    fecha=s.fecha,
                    hEntrada=s.hEntrada,
                    hSalida=s.hSalida,
                    clase=s.clase,
                    siesta=s.siesta,
                    desayuno=s.desayuno
                )
                listaSolicitudes.append(objSol)

            salida.bitacoras = listaSolicitudes
            salida.estatus = 'OK'
            salida.mensaje = 'Listado de Bitacoras'

        except Exception as e:
            salida.bitacoras = []
            salida.estatus = 'Error'
            salida.mensaje = f'Error al consultar las Bitacoras: {str(e)}'

        return salida.dict()
    

    def consultarTodasBitacoras(self, db: Session):
        salida = BitacorasSalida()
        try:
            # Consultar todas las bitácoras
            lista = db.query(VistaBitacorasAlumnos).all()
            listaSolicitudes = []

            for s in lista:
                # Crear el objeto AlumnosPydantic
                alumno_data = AlumnosPydantic(
                    nControl=s.nControl,
                    nombreAlumno=s.nombreAlumno,
                    aPaterno=s.aPaterno
                )

                # Crear el objeto BitacoraSelect
                objSol = BitacoraSelect(
                    alumno=alumno_data,  # Asignar el objeto AlumnosPydantic
                    idBitacora=s.idBitacora,
                    fecha=s.fecha,
                    hEntrada=s.hEntrada,
                    hSalida=s.hSalida,
                    clase=s.clase,
                    siesta=s.siesta,
                    desayuno=s.desayuno
                )
                listaSolicitudes.append(objSol)

            # Asignar la respuesta
            salida.bitacoras = listaSolicitudes
            salida.estatus = 'OK'
            salida.mensaje = 'Listado de todas las Bitacoras'

        except Exception as e:
            salida.bitacoras = []
            salida.estatus = 'Error'
            salida.mensaje = f'Error al consultar las Bitacoras: {str(e)}'

        return salida.dict()



#----------------------------------------------

#----------------------------------------------------

class VistaBitacorasAlumnos(Base):
    __tablename__ = 'vista_bitacoras_alumnos1'  # Nombre de la vista en MySQL

    idBitacora = Column(Integer, primary_key=True)
    nombreAlumno = Column(String)
    nControl=Column(String)
    aPaterno = Column(String)
    fecha = Column(Date)
    hEntrada = Column(Time)
    hSalida = Column(Time)
    clase = Column(String)
    siesta = Column(String)
    desayuno = Column(String)




 #------------------------------------------------------------------------------
 # 
class Usuarios(Base):
    __tablename__='Usuarios'
    id=Column(Integer,primary_key=True)
    usuario=Column(String)
    contraseniaE=Column(String)
    tipoUsuario=Column(String)
    status=Column(String)

    


    def agregarUsuario(self,db:Session):
        salida=Salida()
        try:
            db.add(self)
            db.commit()
            salida.estatus="OK"
            salida.mensaje="Usuario agregada con exito."
        except:
            salida.estatus="Error"
            salida.mensaje="Usuario al agregar la opcion"
        return salida.dict()
           
    
    
    
    def eliminar(self, id: int, db: Session):
        salida = Salida()
        try:
            # Busca al usuario por su ID
            usuario = db.query(Usuarios).filter(Usuarios.id == id).first()
            
            if usuario:
                # Cambia el estado a "Inactivo"
                usuario.status = "Inactivo"
                db.commit()
                salida.estatus = "OK"
                salida.mensaje = "Usuario inactivado con éxito"
            else:
                salida.estatus = "Error"
                salida.mensaje = "Usuario no encontrado"
        except Exception as e:
            salida.estatus = "Error"
            salida.mensaje = f"Error al inactivar el usuario: {str(e)}"
        return salida.dict()
    

def autenticar(usuario:str,contraseniaE:str,db:Session):
        entrada={"p_usuario":usuario,"p_contraseniaE":contraseniaE}
        salida = UsuarioSalida()
        try:
            respuesta=db.execute(text('call  validar_usuario_simple(:p_usuario,:p_contraseniaE)'  ),entrada).fetchone()
            salida.estatus="OK"
            salida.mensaje="Listado del Usuario"


            objU=Usuario()
            objU.id=respuesta[0]
            objU.usuario=respuesta[1]
            objU.contraseniaE=respuesta[2]
            objU.tipoUsuario=respuesta[3]
            objU.status=respuesta[4]
            
            salida.usuario=objU

        except:
            salida.estatus="Error"
            salida.mensaje="Credenciales incorrectas"
            

        return salida


class Alumnos(Base):
    __tablename__ = 'alumnos'

    idAlumno = Column(Integer, primary_key=True)
    nombreAlumno = Column(String)
    nControl = Column(String(6), unique=True, nullable=False)
    aPaterno = Column(String)
    aMaterno = Column(String)

    def to_schema(self):
        return AlumnosSalida(
            idAlumno=self.idAlumno,
            nombreAlumno=self.nombreAlumno,
            nControl=self.nControl,
            aPaterno=self.aPaterno,
            aMaterno=self.aMaterno
        )

    @classmethod
    def consultarTodos(cls, db: Session):
        try:
            alumnos_lista = db.query(cls).all()
            return [alumno.to_schema() for alumno in alumnos_lista]
        except Exception as e:
            return {"status": "Error", "message": f"Error al consultar los alumnos: {str(e)}"}
        



