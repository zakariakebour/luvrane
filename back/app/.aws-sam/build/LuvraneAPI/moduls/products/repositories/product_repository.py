#Importamos el modelo de productos con todas las tablas
from moduls.products.modules import Product
#Importamos ORM con la sesion
from sqlalchemy.orm import Session
#Importamos fecha
from datetime import datetime, timezone
#Importamos estado del producto
from moduls.products.modules import ProductStatus
#Importamos Joinedload para cargar relaciones
from sqlalchemy.orm import joinedload
#Importamos la clase de atributos
from moduls.products.modules import ProductVariant

#Creamos el metodo que se encarga de insertar los datos del producto creado
def create_product(db: Session, product_data: dict) -> Product:
    product = Product(**product_data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


#Metodo para seleccionar todos los productos con paginacion y filtro opcional de genero
def get_products(db: Session, skip: int = 0, limit: int = 20, gender_category=None) -> dict:
    query = db.query(Product).options(joinedload(Product.store)).filter(Product.is_active == True)
    
    if gender_category:
        query = query.filter(Product.gender_category == gender_category)
        
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {"products": items, "total": total}



#Metodo para seleccionar producto segun su identificador
def get_product_by_id(db: Session, product_id: str) -> Product:
    return db.query(Product).options(
        joinedload(Product.images),
        joinedload(Product.variants).joinedload(ProductVariant.color),
        joinedload(Product.variants).joinedload(ProductVariant.size),
        joinedload(Product.variants).joinedload(ProductVariant.images)
    ).filter(Product.id == product_id).first()


#Metodo para buscar producto segun nombre (busqueda flexible)
def get_product_by_name(db: Session, product_name: str):
    #ilike = insensible a mayusculas + % permite busqueda parcial
    return db.query(Product).options(
        joinedload(Product.images),
        joinedload(Product.variants).joinedload(ProductVariant.color),
        joinedload(Product.variants).joinedload(ProductVariant.size),
        joinedload(Product.variants).joinedload(ProductVariant.images)
    ).filter(
        Product.name.ilike(f"%{product_name}%"),
        Product.is_active == True
    ).all()



#Metodo para listar productos de una tienda concreta con paginacion y filtro opcional de genero
def get_products_by_store(db: Session, store_id: str, skip: int = 0, limit: int = 20, gender_category=None) -> dict:
    query = db.query(Product).options(
        joinedload(Product.images),
        joinedload(Product.variants).joinedload(ProductVariant.color),
        joinedload(Product.variants).joinedload(ProductVariant.size),
        joinedload(Product.variants).joinedload(ProductVariant.images),
        joinedload(Product.store)
    ).filter(
        Product.store_id == store_id,
        Product.is_active == True
    )
    #Aplicamos filtro de categoria de genero si se envia
    if gender_category:
        query = query.filter(Product.gender_category == gender_category)

    total = query.count()
    products = query.offset(skip).limit(limit).all()
    return {"total": total, "products": products}

#Metodo para eliminar producto (soft delete)
def delete_product(db: Session, product: Product) -> Product:
    #Lo desactivamos
    product.is_active = False
    product.deleted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    #Devolvemos el producto
    return product


#Metodo para actualizar el producto en la base de datos
def update_product(db: Session, product: Product, product_data: dict) -> Product:
    for field, value in product_data.items():
        if value is not None:
            setattr(product, field, value)
    #Insertamos la fecha en la que se realizo la ultima modificacion del producto
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    #Devolvemos el producto
    return product


#Metodo para consultar estado del producto
def get_product_status(db: Session, product_id: str):
    #Realizamos la consulta a la base de datos filtrando el producto
    product = db.query(Product).filter(Product.id == product_id).first()
    #Si tiene estado el producto
    if product:
        return product.status
    return None


#Metodo para actualizar estado del producto
def update_product_status(db: Session, product: Product, status: ProductStatus) -> Product:
    product.status = status
    product.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(product)
    return product

#Metodo para selccionar producto por nombrey tienda
def get_product_by_name_and_store(db: Session, name: str, store_id: str):
    return (
        db.query(Product)
        .options(
            joinedload(Product.images),
            joinedload(Product.variants).joinedload(ProductVariant.color),
            joinedload(Product.variants).joinedload(ProductVariant.size),
            joinedload(Product.variants).joinedload(ProductVariant.images),
            joinedload(Product.store)
        )
        .filter(
            Product.name == name,
            Product.store_id == store_id,
            Product.is_active == True
        )
        .first()
    )

