import sys
from dwave.cloud import config

with open("dwave.conf", 'w') as archivo:
    archivo.write("[defaults]\n")
    archivo.write("token = " + str(sys.argv[1]))

config.load_config()