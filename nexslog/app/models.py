from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


# O "Contrato" entre o ERP e a ferramenta
class Order(SQLModel, table=True):
    """Está classe é ao mesmo tempo um modelo Pydantic e uma tabela SQL"""

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    customer_name: str
    total_value: float
    status: str = Field(default='RECEIVED')  # Status inicial no Hub
    created_at: datetime = Field(default_factory=datetime.now)
    tracking_code: Optional[str] = Field(default=None)
