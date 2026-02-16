import os

import pandas as pd
import streamlit as st
from fastapi import Exception
from sqlmodel import Session, create_engine, select

from nexslog.app.models import Order

# Configuração da página
st.set_page_config(page_title='NEXSLOG Hub - Dashboard', layout='wide')

# Conexão com Banco (Usa a mesma lógica do app)
DATABASE_URL = os.getenv(
    'DATABASE_URL', 'postgresql://user:pass@db:5432/interop_db'
)
engine = create_engine(DATABASE_URL)


st.title('🚚 NEXSLOG Hub: Monitor de Interoperabilidade')
st.markdown(
    'Visualização em tempo real dos pedidos integrados entre ERP, WMS e TMS.',
)


# Função para buscar dados
def get_orders():
    with Session(engine) as session:
        statement = select(Order)
        results = session.exec(statement).all()
        return results


# Interface
if st.button('🔄 Atualizar Dados'):
    st.rerun()


# Simulando a tabela de pedidos
try:
    with Session(engine):
        from nexslog.app.models import Order

        orders = Session.exec(select(Order)).all()

        if orders:
            df = pd.DataFrame([o.dict() for o in orders])

            # Gráfico de Status
            st.subheader('📊 Pedidos por Status')
            status_count = df['status'].value_counts()
            st.bar_chart(status_count)

            # Tabela Detalhada
            st.subheader('📑 Listagem de Pedidos')
            # Formatando a exibição
            st.dataframe(
                df[
                    [
                        'order_id',
                        'customer_name',
                        'total_value',
                        'status',
                        'tracking_code',
                        'created_at',
                    ]
                ],
                use_container_width=True,
            )
        else:
            st.info('Nenhum pedido encontrado no banco de dados.')
except Exception as e:
    st.error(f'Erro ao conectar no banco: {e}')
