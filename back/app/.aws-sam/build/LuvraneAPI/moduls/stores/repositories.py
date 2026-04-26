#Importamos Sesion
from sqlalchemy.orm import Session
#Importamos el modelo de tienda
from moduls.stores.modules import Store
#Importamos fechas
from datetime import datetime,timezone

#Creamos metodo para que inserte los datos de la tienda
def create_store(db: Session,store_data: dict) -> dict:
    store = Store(
        **store_data
    )
    db.add(store) 
    db.commit()
    db.refresh(store)
    return store

#Creamos el metodo que selecciona las tiendas para mostrar
def select_stores(db: Session,skip: int,limit: int=20) -> dict:
    #Contamos el total de las tiendas
    total = db.query(Store).count()  
    #Las paginamos                      
    stores = db.query(Store).offset(skip).limit(limit).all()
    #Devolvemos resultado total y las tiendas
    return {"total": total, "stores": stores}

#Metodo que selecciona segun identificador de la tienda
def select_store_by_id(db: Session,store_id):
    #Hacemos una consulta con ese identificador para filtrar la tienda
    return db.query(Store).filter(Store.id == store_id).first()

#Metodo para buscar la tienda segun nombre
def get_store_by_name(db: Session,store_name):
    #Hacemos una consulta segun el nombre recibido por el parametro para buscar
    return db.query(Store).filter(Store.name == store_name).first()

#Metodo para eliminar/desactivar la cuenta de tienda
def delete_store(db: Session,store: Store) -> Store:
    #Si todo correcto activamos opcion
    store.is_active = False
    #Insertamos fecha del evento
    store.deleted_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(store)

    return store

# Metodo para actualizar la tienda e insertar la fecha de ultima actualizacion
def update_store(db: Session, store: Store, store_data: dict) -> Store:  #Recibe datos de store exsistenes
   #Actualizamos solo el dato que se cambio, los otros campos como son None los ignoramos 
    for field,value in store_data.items():
       if value is not None:
           setattr(store,field,value)
    
    #Insertamos fecha actual de la modificacion
    store.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(store)

    return store
