# 🚚 NEXSLOG Hub: Inteligência e Interoperabilidade Logística

O **NEXSLOG Hub** é uma solução de integrabilidade projetada para conectar os três pilares da cadeia de suprimentos: **ERP, WMS e TMS**. O sistema centraliza dados de pedidos, monitora o fluxo de processamento e fornece indicadores estratégicos (KPIs) em tempo real para gestores de logística.

## 🚀 Tecnologias Utilizadas

- **FastAPI:** Framework moderno e de alta performance para a construção da API.
- **SQLModel:** Interação simplificada com o banco de dados, unindo o poder do SQLAlchemy e Pydantic.
- **Streamlit:** Dashboard interativo para visualização de dados e BI.
- **Pydantic v2:** Validação rigorosa de dados e contratos de API.
- **SQLite:** Banco de dados relacional para persistência de pedidos e rastreabilidade.

## 📊 Funcionalidades do Dashboard

- **Meta de Faturamento:** Monitoramento em tempo real do progresso das vendas diárias.
- **Análise de SLA:** Alertas automáticos para pedidos parados há mais de 4 horas (Gargalos de Operação).
- **Lead Time Médio:** Cálculo automático do ciclo de vida do pedido (da criação ao despacho).
- **Tendência de Entrada:** Gráfico temporal para identificação de picos de demanda.
- **Rastreabilidade Total:** Tabela detalhada com filtros dinâmicos por cliente, pedido ou status.

## 🛠️ Como Executar o Projeto

1. Clone o repositório.
2. Ative o ambiente virtual: `source .venv/bin/activate`
3. Inicie a API: `python -m nexslog.app.main`
4. Inicie o Dashboard: `streamlit run nexslog/dashboard.py`
