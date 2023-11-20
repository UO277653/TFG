import sys
from qiskit import IBMQ

IBMQ.save_account(str(sys.argv[1]))