import socket
import sys
import json


def my_config_parser(config_filename):
    config_file = open(config_filename)
    dic = {}
    for line in config_file:
        lin = line.strip()
        if lin.startswith("#"):
            continue
        spl = lin.split("=")
        dic[spl[0].strip()] = spl[1].strip()
    config_file.close()
    return dic


infile = sys.argv[1]
outfile = sys.argv[2]

config = my_config_parser("configs/ner_service.conf")
port = int(config["port"])

dic = {"input": infile, "output": outfile}
msg = json.dumps(dic)

client = socket.socket()
client.connect(('127.0.0.1', port))
client.send(msg.encode("utf-8"))
# msg = client.recv(1024)
print(msg)

