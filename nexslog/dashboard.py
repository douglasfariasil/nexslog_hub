import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from sqlmodel import Session, create_engine, select

from nexslog.analytics.engine import check_system_health, predict_bottleneck
from nexslog.database.models import Order

API_URL = os.getenv('API_URL', 'http://localhost:8000')


st.set_page_config(
    page_title='NEXSLOG Hub - Intelligence', layout='wide', page_icon='🚚'
)

sqlite_url = 'sqlite:///./banco.db'
engine = create_engine(sqlite_url, connect_args={'check_same_thread': False})

st.markdown(
    """
    <style>
    /* Cartões com fundo semi-transparente para ler no Dark Mode */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05); /* Um
        toque de brilho no fundo */ padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* Forçar a cor do rótulo e do valor para branco/claro */
    [data-testid="stMetricLabel"] {
        color: #e0e0e0 !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title('🚀 NEXSLOG Control')
pagina = st.sidebar.radio(
    'Navegar para:', ['📊 Dashboard BI', '📥 Importar Arquivos']
)

if pagina == '📊 Dashboard BI':
    st.title('🚚 NEXSLOG Hub: Inteligência Logística')
    st.markdown('Monitoramento estratégico de integração ERP ➔ WMS ➔ TMS')

    try:
        with Session(engine) as session:
            statement = select(Order)
            orders = session.exec(statement).all()

            if orders:
                df = pd.DataFrame([o.model_dump() for o in orders])
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['updated_at'] = pd.to_datetime(
                    df.get('updated_at', df['created_at'])
                )

                # Filtros na Sidebar
                st.sidebar.divider()
                st.sidebar.header('🔍 Filtros de Auditoria')
                search_query = st.sidebar.text_input('Cliente ou Pedido', '')
                status_filter = st.sidebar.multiselect(
                    'Status do Fluxo',
                    df['status'].unique(),
                    default=df['status'].unique(),
                )

                df_filtered = df[df['status'].isin(status_filter)]
                if search_query:
                    mask = df_filtered['customer_name'].str.contains(
                        search_query, case=False
                    ) | df_filtered['order_id'].str.contains(
                        search_query, case=False
                    )
                    df_filtered = df_filtered[mask]

                st.subheader('🎯 Meta de Faturamento do Dia')
                faturamento_atual = df_filtered['total_value'].sum()
                meta_diaria = 100000.0
                progresso = min(faturamento_atual / meta_diaria, 1.0)
                col_prog, col_perc = st.columns([4, 1])
                col_prog.progress(progresso)
                col_perc.markdown(
                    f'**{progresso * 100:.1f}%** (R$ {meta_diaria:,.0f})'
                )

                st.divider()

                col1, col2, col3, col4 = st.columns(4)
                now = datetime.now()
                atrasados = len(
                    df_filtered[
                        (df_filtered['status'] == 'RECEIVED')
                        & (df_filtered['created_at'] < now - timedelta(hours=4))
                    ]
                )

                shipped = df_filtered[df_filtered['status'] == 'SHIPPED']
                if not shipped.empty:
                    mean_hours = (
                        shipped['updated_at'] - shipped['created_at']
                    ).dt.total_seconds().mean() / 3600
                    lead_time = f'{mean_hours:.1f}h'
                else:
                    lead_time = 'N/A'

                col1.metric('Volume Total', len(df_filtered))
                col2.metric(
                    'Aguardando WMS',
                    len(df_filtered[df_filtered['status'] == 'RECEIVED']),
                    f'{atrasados} Críticos',
                    delta_color='inverse',
                )
                col3.metric('Lead Time Médio', lead_time)
                col4.metric('Faturamento Gerido', f'R$ {faturamento_atual:,.2f}')

                c1, c2 = st.columns(2)

                with c1:
                    st.subheader('📊 Gargalos por Status')
                    st.bar_chart(
                        df_filtered['status'].value_counts(), horizontal=True
                    )
                with c2:
                    st.subheader('💰 Concentração de Receita')
                    revenue = (
                        df_filtered
                        .groupby('customer_name')['total_value']
                        .sum()
                        .sort_values(ascending=False)
                        .head(10)
                    )
                    st.bar_chart(revenue)

                st.divider()
                st.subheader('📈 Tendência de Entrada')
                df_trend = df_filtered.copy().set_index('created_at')
                st.line_chart(df_trend.resample('h').size(), color='#29b5e8')

                st.divider()
                col_h, col_p = st.columns([1, 2])

                with col_h:
                    st.subheader('📡 Saúde do Hub')
                    health = check_system_health(df)
                    for sys, status in health.items():
                        color = '🟢' if status else '🔴'
                        label = 'Ativo' if status else 'Sem Dados (24h)'
                        st.write(f'{color} **{sys}**: {label}')

                with col_p:
                    st.subheader('🔮 Análise Preditiva')
                    msg = predict_bottleneck(df)
                    st.info(msg)

                st.divider()
                st.subheader(
                    '🗺️ Capilaridade de Entregas (Distribuição Geográfica)'
                )

                coords = {
                    'São Paulo': [-23.5505, -46.6333],
                    'Rio de Janeiro': [-22.9068, -43.1729],
                    'Curitiba': [-25.4284, -49.2733],
                    'Belo Horizonte': [-19.9167, -43.9345],
                }

                map_data = df_filtered[
                    df_filtered['city'].isin(coords.keys())
                ].copy()
                if not map_data.empty:
                    map_data['lat'] = map_data['city'].map(lambda x: coords[x][0])
                    map_data['lon'] = map_data['city'].map(lambda x: coords[x][1])
                    st.map(map_data[['lat', 'lon']])
                else:
                    st.write(
                        "Adicione cidades como 'São Paulo' ou"
                        "'Rio de Janeiro' nos pedidos para visualizar o mapa."
                    )

                st.subheader('📑 Rastreabilidade Total')
                st.dataframe(
                    df_filtered[
                        [
                            'order_id',
                            'customer_name',
                            'total_value',
                            'status',
                            'created_at',
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            else:
                st.info('📭 Aguardando integração de pedidos...')
    except Exception as e:
        st.error(f'❌ Erro: {e}')

else:
    st.title('📥 Importação Massiva de Dados')
    st.markdown('Suba arquivos Excel ou CSV para alimentar o Hub sem usar a API.')

    arquivo = st.file_uploader('Arraste sua planilha aqui', type=['csv', 'xlsx'])

    if arquivo:
        df_imp = (
            pd.read_csv(arquivo)
            if arquivo.name.endswith('.csv')
            else pd.read_excel(arquivo)
        )
        st.write('🔍 Prévia dos dados:')
        st.dataframe(df_imp.head())

        if st.button('🚀 Confirmar Carga no Banco'):
            with Session(engine) as session:
                for _, row in df_imp.iterrows():
                    session.add(
                        Order(
                            order_id=str(row['order_id']),
                            customer_name=row['customer_name'],
                            total_value=row['total_value'],
                            status='RECEIVED',
                        )
                    )
                session.commit()
            st.success(f'✅ {len(df_imp)} pedidos importados!')
