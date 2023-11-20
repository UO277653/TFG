from qiskit import IBMQ

# Cargar tu cuenta de IBM Quantum Experience desde el archivo de configuración
IBMQ.load_account()

# Verificar si hay una cuenta almacenada
if IBMQ.stored_account():
    print("Qiskit: logeado correctamente")
    # Resto del código para trabajos cuánticos con Qiskit
else:
    print("Qiskit: no logeado")