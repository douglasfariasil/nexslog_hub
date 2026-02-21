from http import HTTPStatus

from fastapi import HTTPException
from sqlmodel import Session, select

from nexslog.database.models import Order


class WMSAdapter:
    @staticmethod
    def process_status_update(session: Session, order_id: str, new_status: str):
        """
        Localiza o pedido e atualiza o status conforme informado pelo WMS.
        """
        # Busca o pedido pelo ID fornecido pelo ERP original
        statement = select(Order).where(Order.order_id == order_id)
        db_order = session.exec(statement).first()

        # Validação: O WMS não pode atualizar algo que não existe no Hub

        if not db_order:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f'Pedido {order_id} não encontrado no NEXSLOG hub.',
            )

        # Lógica de Negócio: Impede retrocesso ou alteração de pedidos finalizados

        if db_order.status == 'SHIPPED':
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Pedido {order_id} já enviado',
            )  # não pode ter o status alterado.

        # Evita update se o status for o mesmo
        if db_order.status == new_status:
            return db_order

        # Aplica a atualização
        db_order.status = new_status
        session.add(db_order)
        session.commit()
        session.refresh(db_order)

        return db_order
