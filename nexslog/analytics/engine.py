from datetime import datetime, timedelta


def check_system_health(df):
    """
    Verifica se os sistemas integraram dados nas últimas 24h
    """
    now = datetime.now()
    last_24h = now - timedelta(hours=24)

    # Filtra pedidos recentes
    recent_df = df[df['updated_at'] >= last_24h]

    health = {
        'ERP': not recent_df[recent_df['status'] == 'RECEIVED'].empty,
        'WMS': not recent_df[recent_df['status'] == 'PICKING'].empty,
        'TMS': not recent_df[recent_df['status'] == 'SHIPPED'].empty,
    }
    return health


def predict_bottleneck(df):
    """
    Analisa a tendência das últimas 3h para prever acúmulo
    """
    now = datetime.now()
    last_3h = now - timedelta(hours=3)

    # Pedidos que entraram nas últimas 3h
    recent_inbound = len(df[df['created_at'] >= last_3h])

    # Pedidos que saíram (SHIPPED) nas últimas 3h
    recent_outbound = len(
        df[(df['status'] == 'SHIPPED') & (df['updated_at'] >= last_3h)]
    )

    # Cálculo simples de vazão
    gap = recent_inbound - recent_outbound

    if gap > 0:
        return (
            f'⚠️ Tendência: Acúmulo de {gap * 4} pedidos em'
            ' PICKING nas próximas 12h se o ritmo persistir.'
        )
    return (
        '✅ Operação está fluindo: '
        'A vazão de saída está maior ou igual à de entrada.'
    )
