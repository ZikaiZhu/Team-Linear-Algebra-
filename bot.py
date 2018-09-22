import socket
import json

def hello():
    s.send("HELLO " + team_name + "\n")
    response = s.recv(BUFFER_SIZE)
    json_data = json.JSONDecoder.decode(response)
    holdings = json_data['symbols']
    print holdings

team_name = "TEAMLINEARALGEBRA"

test_ip = "10.0.80.173"

prod_port = 25000
slower_port = 25001
empty_port = 25002

BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((test_ip,prod_port))

holdings = []

hello()


    
    
