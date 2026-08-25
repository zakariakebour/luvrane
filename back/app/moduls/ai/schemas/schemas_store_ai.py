from pydantic import BaseModel, ConfigDict,Field
from typing import Optional

# Clase para validación de cada campo de tienda
class StoreAIData(BaseModel):
    """
    Datos de una tienda necesarios para construir
    su conocimiento para el sistema de IA.
    """

    model_config = ConfigDict(from_attributes=True)

    store_id: str = Field(alias="id")
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    logistics_partner: Optional[str] = None