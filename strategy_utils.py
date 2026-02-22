import time
import datetime
import json

import requests


def esperar_al_siguiente_cuarto():
    ahora = datetime.datetime.now()
    minutos_faltantes = 15 - (ahora.minute % 15)

    proxima_ejecucion = ahora + datetime.timedelta(minutes=minutos_faltantes)
    proxima_ejecucion = proxima_ejecucion.replace(second=1, microsecond=0)

    segundos_a_esperar = (proxima_ejecucion - ahora).total_seconds()

    print(
        f"[{ahora.strftime('%H:%M:%S')}] Esperando {segundos_a_esperar:.2f} segundos hasta las {proxima_ejecucion.strftime('%H:%M:%S')}..."
    )
    time.sleep(segundos_a_esperar)


def send_webhook(url: str, action: str, uuid: str, symbol: str):
    payload = {"action": action, "uuid": uuid, "symbol": symbol}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url=url, data=json.dumps(payload), headers=headers, timeout=5
        )

        if response.status_code == 200:
            print(f"Webhook enviado correctamente: {action} {symbol}")
        else:
            print(f"Error al enviar webhook: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Error al enviar webhook: {e}")
