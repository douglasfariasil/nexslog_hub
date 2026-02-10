from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

# Definição do Modelo (O que o ERP envia)


# Modelo que representa um item dentro do pedido
class OrderItem(BaseModel):
    sku: str
    quantity: int
    price: float


# O "Contrato" entre o ERP e a ferramenta
class ERPOrderInput(BaseModel):
    order_id: str = Field(..., examples=['PED-12345'])
    customer_name: str
    items: List[OrderItem]
    total_value: float
    created_at: datetime = Field(default_factory=datetime.now)
