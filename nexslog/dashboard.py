import os

import pandas as pd
import streamlit as st
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


# # Função para buscar dados
# def get_orders():
#     with Session(engine) as session:
#         statement = select(Order)
#         results = session.exec(statement).all()
#         return results


# Interface de Controle
col1, col2 = st.columns([1, 5])
with col1:
    if st.button('🔄 Atualizar Dados'):
        st.rerun()


# Busca e Exibição de Dados
try:
    with Session(engine) as session:
        statement = select(Order)
        orders = session.exec(statement).all()

        if orders:
            df = pd.DataFrame([o.model_dump() for o in orders])

            st.divider()
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric('Total de Pedidos', len(df))
            kpi2.metric('Aguardando Envio', len(df[df['status'] != 'SHIPPED']))
            kpi3.metric('Despachados', len(df[df['status'] == 'SHIPPED']))

            col_chart, col_table = st.columns([1, 1])

            # Gráfico de Status
            with col_chart:
                st.subheader('📊 Pedidos por Status')
                status_count = df['status'].value_counts()
                st.bar_chart(status_count)

            # Tabela Detalhada
            st.subheader('📑 Listagem Detalhada de Pedidos')

            # Formatando a exibição
            cols_to_show = [
                'order_id',
                'customer_name',
                'total_value',
                'status',
                'tracking_code',
                'created_at',
            ]

            # Garante que as colunas existem antes de filtrar
            existing_cols = [c for c in cols_to_show if c in df.columns]
            st.dataframe(
                df[existing_cols], use_container_width=True, hide_index=True
            )

        else:
            st.info(
                '📭 Nenhum pedido encontrado no banco de dados até o momento.'
            )

except Exception as e:
    st.error(f'❌ Erro ao conectar no banco de dados: {e}')
