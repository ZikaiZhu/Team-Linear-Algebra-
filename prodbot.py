#!/usr/bin/python3

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

import sys
import socket
import json
import time
import threading

# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="teamlinearalgebra"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=2
prod_exchange_hostname="production"

port=25000 #+ (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

holdings = {}

order_id = 42

orders = []

book = {}

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

def buy(exchange, symbol, price, size):
    global order_id

    keyvals = [("type","add"),("order_id",order_id),("symbol",symbol),("dir","BUY"),("price",price),("size",size)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))
    orders.append(order_id)
    order_id += 1

def sell(exchange, symbol, price, size):
    global order_id

    keyvals = [("type","add"),("order_id",order_id),("symbol",symbol),("dir","SELL"),("price",price),("size",size)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))
    orders.append(order_id)
    order_id += 1

def convert(exchange, buy, symbol, size):
    global order_id
    keyvals = [("type","convert"),("order_id",order_id),("symbol",symbol),("dir",buy),("size",size)]
    write_to_exchange(exchange,json.loads(write_json(keyvals)))

    order_id += 1

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

def open_response(json_data):
    print("open symbols:",json_data['symbols'])

def close_response(json_data):
    print("closed symbols:",json_data['symbols'])

def error_response(json_data):
    print("ERROR:",json_data['error'])

def book_response(json_data):
    book[json_data['symbol']] = (json_data['buy'], json_data['sell'])

def trade_response(json_data):
    #print("trade made:",json_data['symbol'],"|",json_data['price'],"|",json_data['size'])
    pass

def ack_response(json_data):
    print("acknowledged:", json_data['order_id'])

def reject_response(json_data):
    print("rejected:", json_data['order_id'], "|", json_data['error'])

def fill_response(json_data):
    print("filled:", json_data['order_id'], "|", json_data['symbol'],"|",json_data['price'],"|",json_data['size'])

def out_response(json_data):
    print("out:", json_data['order_id'])

def hello_response(json_data):
    holds = json_data['symbols']
    for hold in holds:
        holdings[hold['symbol']] = hold['position']
    print(holdings)

def listen_for_responses():

    global exchange

    while True:

        f = exchange.readline()

        if not f:
            time.sleep(1)
            continue

        data = json.loads(f)

        if data['type'] == "open":
            open_response(data)
        if data['type'] == "close":
            close_response(data)
        if data['type'] == "error":
            error_response(data)
        if data['type'] == "book":
            book_response(data)
        if data['type'] == "trade":
            trade_response(data)
        if data['type'] == "ack":
            ack_response(data)
        if data['type'] == "reject":
            reject_response(data)
        if data['type'] == "fill":
            fill_response(data)
        if data['type'] == "out":
            out_response(data)
        if data['type'] == "hello":
            hello_response(data)
    
    

# ~~~~~============== MAIN LOOP ==============~~~~~


exchange = None

def trade_bond(exchange):

    if not "BOND" in book:
        return

    if len(book['BOND'][0]) == 0 or len(book['BOND'][1]) == 0:
        return

    for bid in book["BOND"][0]:
        price = bid[0] 
        quantity = bid[1]
        if price > 1000:
            sell(exchange, 'BOND', price, quantity)

    for bid in book["BOND"][1]:
        price = bid[0] 
        quantity = bid[1]
        if price < 1000:
            buy(exchange, 'BOND', price, quantity)

def trade_babs(exchange):

    if not "BABZ" in book and not "BABA" in book:
        return

    if len(book['BABZ'][0]) or len(book['BABZ'][1]) == 0:
        return

    babz_bid = book['BABZ'][0][0]
    babz_sell = book['BABZ'][1][0]

    baba_bid = book['BABA'][0][0]
    baba_sell = book['BABA'][1][0]

    if baba_bid[1] * baba_sell[0] + 10 < babz_bid[0] * babz_bid[1]:
        buy(exchange, 'BABA', baba_sell[0], min(10, baba_sell[1]))
        convert(exchange, "BUY", 'BABA', min(10, baba_sell[1]))
        sell(exchange, 'BABZ', babz_bid[0], min(10, babz_bid[1]))


def main():
    global exchange

    exchange = connect()
    hello(exchange)

    thread = threading.Thread(target=listen_for_responses)
    thread.start()

    print(thread.name)
    print(thread.is_alive())

    while True:
        trade_bond(exchange)
        trade_babs(exchange)
        time.sleep(0.3)

if __name__ == "__main__":
    main()
