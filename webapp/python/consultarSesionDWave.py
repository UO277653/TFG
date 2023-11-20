import dwave.cloud
from dwave.cloud import config

# Verificar si hay una configuración válida para Leap
try:
    config.load_config()
    print("D-Wave: logeado correctamente")
    # Resto del código para trabajos en D-Wave
except Exception:
    print("D-Wave: no logeado")