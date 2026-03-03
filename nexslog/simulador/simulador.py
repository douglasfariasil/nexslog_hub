import random
import time

import requests

BASE_URL = 'http://localhost:8000'

probabilidade_wms = 0.3
probabilidade_tms = 0.6

clientes = [
    'Logítica Express',
    'Varejo Total',
    'Indústria Norte',
    'Distribuidora Sul',
    'E-commerce Brasil',
]

produtos_valor = [50.0, 150.0, 500.0, 1200.0, 2500.0]


def simular_pedidos(quantidade=50):
    print(f'🚀 Iniciando simulação de {quantidade} pedidos...')

    for i in range(1, quantidade + 1):
        order_id = f'PED-SIM-{random.randint(1000, 9999)}-{i}'

        payload_erp = {
            'order_id': order_id,
            'customer_name': random.choice(clientes),
            'total_value': random.choice(produtos_valor),
        }

        try:
            requests.post(f'{BASE_URL}/ingerir/erp', json=payload_erp)

            time.sleep(0.1)

            decisao = random.random()

            if decisao > probabilidade_wms:
                requests.patch(
                    f'{BASE_URL}/ingerir/wms/atualizar',
                    params={'order_id': order_id, 'new_status': 'PICKING'},
                )

            if decisao > probabilidade_tms:
                tracking = f'TRK-{random.randint(10000, 99999)}'
                params = {'order_id': order_id, 'tracking': tracking}
                requests.patch(f'{BASE_URL}/ingerir/tms/dispatch', params=params)

            if i % 10 == 0:
                print(f'✅ {i} pedidos processados...')

        except Exception as e:
            print(f'❌ Erro ao conectar na API: {e}')
            break

    print('\n✨ Simulação finalizada! Verifique o seu Dashboard.')


if __name__ == '__main__':
    simular_pedidos(50)
