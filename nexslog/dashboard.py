import pandas as pd
import streamlit as st
from sqlmodel import Session, create_engine, select

from nexslog.database.models import Order

# Configuração da página
st.set_page_config(page_title='NEXSLOG Hub - Dashboard', layout='wide')

# Conexão com Banco (Usa a mesma lógica do app)
sqlite_url = 'sqlite:///./banco.db'
engine = create_engine(sqlite_url, connect_args={'check_same_thread': False})


st.title('🚚 NEXSLOG Hub: Monitor de Interoperabilidade')
st.markdown(
    'Visualização em tempo real dos pedidos integrados entre ERP, WMS e TMS.',
)


# Interface de Controle
col_btn, col_search = st.columns([1, 3])
with col_btn:
    if st.button('🔄 Atualizar Dados'):
        st.rerun()

with col_search:
    # Filtro de busca por cliente
    search_query = st.text_input('🔍 Filtrar por Cliente', '')


# Busca e Exibição de Dados
try:
    with Session(engine) as session:
        statement = select(Order)
        orders = session.exec(statement).all()

        if orders:
            df = pd.DataFrame([o.model_dump() for o in orders])

            # Garante que a coluna existe para o Streamlit não reclamar
            if 'tracking' not in df.columns:
                df['tracking'] = None

            if search_query:
                df = df[
                    df['customer_name'].str.contains(search_query, case=False)
                ]

            st.divider()
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric('Total de Pedidos', len(df))
            kpi2.metric('Aguardando Envio', len(df[df['status'] != 'SHIPPED']))
            kpi3.metric('Despachados', len(df[df['status'] == 'SHIPPED']))

            st.divider()
            col_chart1, col_chart2 = st.columns(2)

            # 📊 Gráfico 1: Pedidos por Status (O que já tínhamos)
            with col_chart1:
                st.subheader('📊 Volume por Status')
                st.bar_chart(df['status'].value_counts())

            # 💰 Gráfico 2: Faturamento por Cliente
            with col_chart2:
                st.subheader('💰 Faturamento por Cliente')
                # Agrupa os valores somando o total_value por cliente
                revenue = (
                    df
                    .groupby('customer_name')['total_value']
                    .sum()
                    .sort_values(ascending=False)
                )
                st.bar_chart(revenue)

            st.divider()

            # Ajuste de colunas para bater com o simulador (usando 'tracking')
            cols_to_show = [
                'order_id',
                'customer_name',
                'total_value',
                'status',
                'tracking',
                'created_at',
            ]

            # Garante que as colunas existem antes de filtrar
            existing_cols = [c for c in cols_to_show if c in df.columns]

            # 💾 Função para converter o DataFrame em CSV (cache para performance)
            @st.cache_data
            def convert_df(df_to_convert):
                return df_to_convert.to_csv(index=False).encode('utf-8-sig')

            csv_data = convert_df(df[existing_cols])

            # Cria o botão de download
            st.download_button(
                label='📥 Baixar Relatório (CSV)',
                data=csv_data,
                file_name='relatorio_pedidos_nexslog.csv',
                mime='text/csv',
                help='Clique para baixar os dados filtrados em formato Excel/CSV',
            )

            # 📑 Tabela Detalhada (Abaixo dos gráficos para melhor leitura)
            st.subheader('📑 Listagem Detalhada de Pedidos')
            st.dataframe(
                df[existing_cols], use_container_width=True, hide_index=True
            )

        else:
            st.info(
                '📭 Nenhum pedido encontrado no banco de dados até o momento.'
            )

except Exception as e:
    st.error(f'❌ Erro ao conectar no banco de dados: {e}')
