#Importamos el modelo de productos con todas las tablas
from moduls.products.modules import Product
#Importamos ORM con la sesion
from sqlalchemy.orm import Session
#Importamos fecha
from datetime import datetime,timezone
#Importamos estado del producto
from moduls.products.modules import ProductStatus

#Creamos el metodo que se encarga de insertar los datos del producto creado
def create_product(db: Session,product_data: dict) -> dict:
    product = Product(
        **product_data
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

#Metodo para listar todos los productos
def get_products(db: Session,skip: int=0,limit: int=20) -> dict:
    #Total de productos para paginacion, filtramos por activos
    total = db.query(Product).filter(Product.is_active == True).count()

    #productos a mostrar con paginacion, filtramos por activo
    products = db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

    #Devolvemos resultado total y los productos
    return {"total":total,"products":products}

#Metodo para seleccionar producto segun su identificador
def get_product_by_id(db: Session,product_id: str):
    #Hacemos la consulta y devolvemos resultado
    return db.query(Product).filter(Product.id == product_id).first()

#Metodo para buscar producto segun nombre
def get_product_by_name(db: Session,product_name: str):
    #Hacemos la consulta segun el nombre
    return db.query(Product).filter(Product.name == product_name).first()

#Metodo para selccionar producto segun nombre y su tienda
def get_product_by_name_and_store(db: Session,product_name: str,store_id: str):
    #Devolvemos consulta 
    return db.query(Product).filter(Product.name == product_name, Product.store_id == store_id).first()

#Metodo para eliminar producto
def delete_product(db: Session,product: Product )-> Product:
    #Lo desactivamos
    product.is_active = False
    product.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    #Devolvemos el producto
    return product

#Metodo para actualizar el producto en la base de datos
def update_product(db: Session,product: Product,product_data: dict) -> Product:
    for field,value in product_data.items():
        if value is not None:
            setattr(product,field,value)

    #Insertamos la fecha en la que se realizo la ultima modificacion del producto
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    #Devolvemos el producto
    return product

#Metodo para consultar estado del producto
def get_product_status(db: Session,product_id: str):
    #Realizamos la consulta a la base de datos filtrando el producto
    product =  db.query(Product).filter(Product.id == product_id).first()

    #Si tiene estado el producto
    if product:
        return  product.status
    return None

# Metodo para actualizar estado del producto
def update_product_status(db: Session, product: Product, status: ProductStatus) -> Product:
    product.status = status
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    return product

