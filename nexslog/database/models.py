from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, func


class Order(SQLModel, table=True):
    """
    Esta classe representa o contrato de dados entre o ERP e o Hub NEXSLOG.
    Funciona como modelo Pydantic para a API e tabela SQL para o banco.
    """

    __table_args__ = {'extend_existing': True}
    __tablename__ = 'orders'

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    customer_name: str
    total_value: float
    status: str = Field(default='RECEIVED')
    city: str = Field(default='São Paulo')
    tracking: Optional[str] = Field(default=None)

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    city: Optional[str] = Field(default='São Paulo')
