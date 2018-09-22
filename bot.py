#!/usr/bin/python3

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="teamlinearalgebra"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

holdings = []

order_id = 42

orders = []

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def hello(exchange):
    write_to_exchange(exchange,json.loads('{"type": "hello", "team": "TEAMLINEARALGEBRA"}'))
    json_output = read_from_exchange(exchange)

    holdings = json_output['symbols']
    print(holdings)

def buy(exchange, symbol, price, size):
    keyvals = [("type","add"),("order_id",order_id),("symbol",symbol),("dir","BUY"),("price",price),("size":size)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))
    orders.append(order_id)
    order_id += 1

def sell(exchange, symbol, price, size):
    keyvals = [("type","add"),("order_id",order_id),("symbol",symbol),("dir","SELL"),("price",price),("size":size)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))
    orders.append(order_id)
    order_id += 1

def convert(exchange, buy, order_id, symbol, size):
    keyvals = [("type","convert"),("order_id",order_id),("symbol",symbol),("dir",buy),("price",price),("size":size)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))

def cancel(exchange, order_id):
    keyvals = [("type","cancel"),("order_id",order_id)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))
    orders.remove(order_id)

def write_json(keyvallist):
    string = "{"
    for (a,b) in keyvallist:
        if isinstance(b, str):
            b = '"'+b+'"'
        string += ('"' + a +'" : '+str(b)+', ')
    string = string[:-2]
    string += "}"
    return string

def listen_for_responses(exchange):
    
    

# ~~~~~============== MAIN LOOP ==============~~~~~



def main():
    exchange = connect()
    hello(exchange)

if __name__ == "__main__":
    main()

def trade_bond(mp_bid, mp_offer, exchange):
    if mp_offer['price'] > 1000:
        sell(exchange, 'BOND', mp_offer['price'], mp_offer['size'])
    if mp_bid['price'] < 1000:
        buy(exchange, 'BOND', mp_bid['price'], mp_bid['size'])
