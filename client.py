import hashlib as hl
import socket
import pickle
import time

IP = "127.0.0.1"
PORT = 1234

def hashed(password):
  text = pickle.dumps(password)
  h = hl.md5(text)
  h = h.hexdigest()
  return h

def get_balance(login):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'get balance'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps(login))
    re = rec(client_socket)
    client_socket.close()
    return re

def do_star(command, what, login, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    if what: client_socket.send(pickle.dumps([what,login,hashed(password)]))
    else: client_socket.send(pickle.dumps([login,hashed(password)]))
    if what: re = True
    else:
      re = rec(client_socket)
      ret = []
      for i in range(re):
        client_socket.send(pickle.dumps('ok'))
        ret.insert(i, rec(client_socket))
      re = ret
    client_socket.close()
    return re

def add_star(what, login, password):
    return do_star('add star', what, login, password)

def remove_star(what, login, password):
    return do_star('remove star', what, login, password)

def get_stars(login, password):
    return do_star('get stars', False, login, password)
  

def known_user(login, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'known user'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    if password: password = hashed(password)
    client_socket.send(pickle.dumps([login, password]))
    re = rec(client_socket)
    client_socket.close()
    return re

def get_history(login, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'get history'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([login, hashed(password)]))
    re = rec(client_socket)
    ret = []
    for i in range(re):
        client_socket.send(pickle.dumps('ok'))
        ret.insert(i, rec(client_socket))
    client_socket.close()
    return ret

def get_id(login):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'get id'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps(login))
    re = rec(client_socket)
    client_socket.close()
    return re
  
def rec(client_socket):
  start = time.time()
  while True:
    if time.time()-start >= 1: return False
    try:
      temp = pickle.loads(client_socket.recv(1024))
      return temp
    except Exception as exception:
      pass

def exe(str):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'get'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps(str))
    re = rec(client_socket)
    ret = []
    for i in range(re):
        client_socket.send(pickle.dumps('ok'))
        ret.insert(i, rec(client_socket))
    client_socket.close()
    return ret

def process(req, login, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'process'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([req, login, hashed(password)]))
    re = rec(client_socket)
    client_socket.close()
    return re

def register(login, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'register'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([login, hashed(password)]))
    re = rec(client_socket)
    client_socket.close()
    return re

def stats(req, time_start, time_end, type):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'stats'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([req, time_start, time_end, type]))
    re = rec(client_socket)
    ret = []
    for i in range(re):
        client_socket.send(pickle.dumps('ok'))
        ret.insert(i, rec(client_socket))
    client_socket.close()
    return ret

def update():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'update'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    re = rec(client_socket)
    client_socket.close()
    return re

def bug_log(text):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'bug'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps(text))
    return True

def delete(login, id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'delete'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([login, id]))

def box_graph(product, buy_sell, start, end):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'box'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([product, buy_sell, start, end]))
    re = rec(client_socket)
    ret = []
    for i in range(re):
        client_socket.send(pickle.dumps('ok'))
        ret.insert(i, rec(client_socket))
    client_socket.close()
    return ret

def my_assets(login, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    command = 'my assets'
    client_socket.send(pickle.dumps(command))
    rec(client_socket)
    client_socket.send(pickle.dumps([login, hashed(password)]))
    re = rec(client_socket)
    ret = []
    for i in range(re):
        client_socket.send(pickle.dumps('ok'))
        ret.insert(i, rec(client_socket))
    client_socket.close()
    return ret

#print(get_stars('TEST', '1234'))
#print(get_stars('TEST', '1234'))
#print(register("TEST2", "1234"))
#print(bug_log("Nice. EPIC TEST"))
#print(process( ['Na', 'Limit', 'sell', '1234', '20', '1'] , "TEST", "1234" ))
#print(process( ['Noice', 'Limit', 'buy', '1234', '20', '1'] , "TEST2", "1234" ))

#print(register('pasham999', '1234'))
#print(get_balance('Nigga9'))
#print(known_user("TEST", False))
#print(my_assets("TEST", "1234"))
#print(get_history("TEST", "1234"))

    
'''
IP = socket.gethostname()
    PORT = 1234
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    client_socket.connect((IP, PORT))
    
    client_socket.setblocking(False)
    
    command = input("Input the command: ")
    client_socket.send(pickle.dumps(command))
    
    if command != 'get':  a = input().split()
    else: a = input()
    
    client_socket.send(pickle.dumps(a))
    print(rec())
    client_socket.close()
'''
#SELECT * FROM orders WHERE request = 'buy' AND price <= 12
