import socket
import pickle
import sqlite3
import csv
import time

ENABLE_OUTPUT = True

global stats
global conn, conn1
global c, s, b
global buffer
global last_delete
last_delete = time.time()
buffer = []

IP = "127.0.0.1"
PORT = 1234

def snd(what):
  try:
    client_socket.send(what)
  except:
    return False
  return True

def box_graph(product, buy_sell):
  c.execute(f"SELECT * FROM orders WHERE product = '{product}' AND request = '{buy_sell}'")
  prices = []
  for i in c.fetchall():
      prices.append(i[6])
  for i in prices:
    b.execute(f"INSERT INTO box VALUES('{product}', {i}, {time.time()}, '{buy_sell}')")

def return_box_graph(product, buy_sell, start, end):
  b.execute(f"SELECT * FROM box WHERE product = '{product}' AND type = '{buy_sell}' AND time >= {start} AND time <= {end} ORDER BY price")
  ret = []
  for i in b.fetchall():
    ret.append(i[1])
  return ret

def create_table():
  c.execute("CREATE TABLE IF NOT EXISTS orders(reqid REAL, name TEXT, type TEXT, request TEXT, product TEXT, amount REAL, price REAL, uid REAL)")

def stars_table():
  st.execute("CREATE TABLE IF NOT EXISTS stars(login TEXT, what TEXT)")

def debts_table():
  d.execute("CREATE TABLE IF NOT EXISTS debts(login TEXT, debt REAL, id REAL)")

def history_table():
  h.execute("CREATE TABLE IF NOT EXISTS history(login TEXT, product TEXT, amount REAL, price REAL, type TEXT)")

def stats_table():
  s.execute("CREATE TABLE IF NOT EXISTS stats (product TEXT, price REAL, time REAL, type TEXT)")

def create_table_users():
  u.execute("CREATE TABLE IF NOT EXISTS users(id REAL, login TEXT, password TEXT, balance REAL)")

def box_table():
  b.execute("CREATE TABLE IF NOT EXISTS box(product TEXT, price REAL, time REAL, type TEXT)")

def assets_table():
  a.execute("CREATE TABLE IF NOT EXISTS assets(uid REAL, product TEXT, amount REAL)")

def send_many(num, li):
  snd(pickle.dumps(num))
  for i in range(num):
    rec(client_socket)
    go = li[i]
    se = pickle.dumps(go)
    if not snd(se): break

def return_history(login):
  h.execute(f"SELECT * FROM history WHERE login = '{login}'")
  return h.fetchall()

def get_stars(login, password):
  if not find(login, password):
    return [False]
  st.execute(f"SELECT * FROM stars WHERE login = '{login}'")
  ret = []
  for i in st.fetchall():
    ret.append(i[1])
  return ret

def add_star(what, login, password):
  if not find(login, password):
    return False
  if type(what) == list:
    for i in what:
      st.execute(f"INSERT INTO stars VALUES('{login}', '{i}')")
    return True
  st.execute(f"INSERT INTO stars VALUES('{login}', '{what}')")

def remove_star(what, login, password):
  if not find(login, password):
    return False
  if type(what) == list:
    for i in what:
      st.execute(f"DELETE FROM stars WHERE login = '{login}' AND what = '{i}'")
    return True
  st.execute(f"DELETE FROM stars WHERE login = '{login}' AND what = '{what}'")

def calc_average(product, new, buy_sell):
  prod = product
  if buy_sell == 'sell':
    prod += '^sell^'
  if prod in stats:
    if new < 0:
      stats[prod][0] -= new
      stats[prod][1] -= 1
    else:
      stats[prod][0] += new
      stats[prod][1] += 1
    temp = stats[prod][1]
    if temp <= 0:
      temp = 1
    ret = stats[prod][0]/temp
    s.execute(f"INSERT INTO stats VALUES('{product}', {ret}, {time.time()}, '{buy_sell}')")
    return ret
  try:
    c.execute(f"SELECT * FROM orders WHERE product = '{product}' AND request = '{buy_sell}'")
  except Exception as ex:
    print("EXCEPTION:", ex)
    return 0
  summ = 0
  alll = c.fetchall()
  for i in alll:
    summ += i[6]
  a = len(alll)
  stats[prod] = [summ, a]
  if a <= 0:
    a = 1
  ret = summ/a
  s.execute(f"INSERT INTO stats VALUES('{product}', {ret}, {time.time()}, '{buy_sell}')")
  return ret

def return_stats(product, time_start, time_end, type):
  try:
    s.execute(f"SELECT * FROM stats WHERE product = '{product}' AND type = '{type}' AND time >= {time_start} AND time <= {time_end}")
  except Exception as ex:
    print(ex)
    return [{}]
  return s.fetchall()

def show_selected(ss):
  data = ss.fetchall()
  for i in data:
    print(i)
  print()

def return_debt(login, id):
  d.execute(f"SELECT * FROM debts WHERE id = {id}")
  substract(False, d.fetchall()[0][1], login)
  d.execute(f"DELETE FROM debts WHERE id = {id}")

def sub_from_debt(id, sub):
  d.execute(f"SELECT * FROM debts WHERE id = {id}")
  try:
    fet = d.fetchall()[0][1]
  except:
    return
  if fet - sub <= 0: d.execute(f"DELETE FROM debts WHERE id = {id}")
  else: d.execute(f"UPDATE debts SET debt = {fet - sub}")

def add_debt(login, id, add):
  d.execute(f"INSERT INTO debts VALUES('{login}', {add}, {id})")

def find(login, password):
    if not password:
      u.execute(f"SELECT * FROM users WHERE login = '{login}'") 
    else: u.execute(f"SELECT * FROM users WHERE login = '{login}' AND password = '{password}'")
    if len(u.fetchall()) == 0:
        return False
    return True

def register(login, password):
    u.execute(f"SELECT * FROM users WHERE login = '{login}'")
    if len(u.fetchall()) != 0:
        return False
    u.execute(f"INSERT INTO users VALUES({time.time()}, '{login}', '{password}', 1000)")
    conn3.commit()
    return True

def get_balance (login):
    u.execute(f"SELECT * FROM users WHERE login = '{login}'")
    if not find:
        return False
    fetch = u.fetchall()
    if len(fetch) == 0: return False
    for i in fetch:
        return i[3];

def add_to_buffer(ad):
  global last_delete
  global buffer
  if time.time() - last_delete > 10:
    buffer = []
    last_delete = time.time()
  buffer.insert(len(buffer), ad)


def print_table():
  if not ENABLE_OUTPUT: return
  c.execute("SELECT * FROM orders")
  show_selected(c)
  print(stats)
  #s.execute("SELECT * FROM stats")
  #show_selected(s)


def delete(login, id):
  try:
    c.execute("DELETE FROM orders WHERE reqid =" + "\'" + str(id) + "\'")
    return_debt(login, id)
  except:
    pass

def bug_log(text):
    f = open("bug_log.txt", "a")
    f.write(text +"\n")
    f.close()

def get_id(login):
  u.execute(f"SELECT * FROM users WHERE login = '{login}'")
  try:
    return u.fetchall()[0][0]
  except: pass

def add_history(login, product, amount, price, type):
  h.execute(f"INSERT INTO history VALUES('{login}', '{product}', {amount}, {price}, '{type}')")  

def substract(buy, total, login):
  if total == 0: return
  if buy: total *= -1
  u.execute(f"SELECT * FROM users WHERE login = '{login}'")
  bal = 0
  for i in u.fetchall(): bal = i[3]
  u.execute(f"UPDATE users SET balance = {bal+total} WHERE login = '{login}'")

def does_have(id, product, amount):
  a.execute(f"SELECT * FROM assets WHERE product = '{product}' AND uid = {id}")
  if len(c.fetchall()) != 0:
    return True
  return False

def add_asset(id, product, amount):
  a.execute(f"SELECT * FROM assets WHERE product = '{product}' and uid = {id}")
  fet = a.fetchall()
  a.execute(f"SELECT * FROM assets")
  print("GOT: ", id, product, amount)
  print(a.fetchall())
  print(fet)
  print("LEN: ", len(fet))
  #if amount <= 0: time.sleep(200)
  if len(fet) == 0:
    a.execute(f"INSERT INTO assets VALUES({id}, '{product}', '{amount}')")
  else:
    a.execute(f"UPDATE assets SET amount = {float(fet[0][2]) + float(amount)} WHERE uid = {id} and product = '{product}'")

def my_assets(login, password):
  if not find(login, password):
    return False
  a.execute(f"SELECT * FROM assets WHERE uid = {get_id(login)}")
  return a.fetchall()

def process(b, login, password):
  mm = False
  if password == 'c35312fb3a7e05b7a44db2326bd29040':
    mm = True
  b[5] = float(b[5])
  def delete_all():
    c.execute("DELETE FROM orders")

  # delete_all()
  # fill_demo()
  # print_table()

  reqid = float(time.time())
  '''
  with open('input.csv', 'r') as i:
    a = csv.reader(i)
    b = list(a)[0]
  '''
  # print(reqid, b)
  # print()
  from_u = login
  uid = get_id(login)
  if b[1].lower() == 'limit':
    limit = True
  else:
    limit = False
  if b[2] == 'buy':
    buy = True
  else:
    buy = False
  product = b[3]
  amount = b[4]
  price = b[5]

  transaction_list = []
  list_counter = 0
  total = 0
  q = float(amount)

  if buy:
    c.execute("SELECT * FROM orders WHERE request = 'sell' AND product = " + "\'" + product + "\'" + " AND price <= " + str(price) + " ORDER BY price")
    for i in c.fetchall():
      if from_u == i[1] : continue
      if q == 0:
        break
      if i[5] > q:
        total += q * i[6]
        transaction_list.insert(list_counter, [reqid, i[0], float(uid), i[7], q, q * i[6]])
        add_to_buffer(['update', reqid, i[5]-q])
        c.execute("UPDATE orders SET amount = '" + str(i[5] - q) + "' WHERE reqid =" + "\'" + str(i[0]) + "\'")
        if not mm: add_asset(uid, product, float(amount))
        add_asset(i[7], product, -1*float(amount))
        add_history(login, product, q, q*i[6], "buy")
        q = 0
        list_counter += 1
        break
      else:
        q -= i[5]
        total += i[5] * i[6]
        transaction_list.insert(list_counter, [reqid, i[0], float(uid), i[7], i[5], i[5] * i[6]])
        add_to_buffer(['delete', reqid])
        c.execute("DELETE FROM orders WHERE reqid =" + "\'" + str(i[0]) + "\'")
        if not mm: add_asset(uid, product, i[5])
        add_asset(i[7], product, -1*i[5])
        add_history(login, product, i[5], i[5]*i[6], "buy")
        calc_average(product, -1*i[6], 'sell')   #Do we ned that?
        box_graph(product, 'sell')
        list_counter += 1
    if q != 0 and limit:
      if not mm: add_debt(login, reqid, q*price)
      if not mm: substract(True, q*price, login)
      add_to_buffer(['add', reqid, from_u, b[1] ,b[2], product, str(q), price, uid])
      c.execute("INSERT INTO orders VALUES(" + str(reqid) + ", '" + str(from_u) + "', '" + b[1] + "', '" + b[2] + "', '" + product + "', " + str(q) + ", " + str(price) + ", " + str(uid) + ")")
      calc_average(product, price, 'buy')    #Do we need that?
      box_graph(product, 'buy')

  else:
    c.execute("SELECT * FROM orders WHERE request = 'buy' AND product = " + "\'" + product + "\'" + " AND price >= " + str(price) + " ORDER BY price DESC")
    for i in c.fetchall():
      if from_u == i[0] : continue
      if q == 0:
        break
      if i[5] > q:
        total += q * i[6]
        transaction_list.insert(list_counter, [i[0], reqid, i[7], float(uid), q, q * i[6]])
        add_to_buffer(['update', reqid, i[5]-q])
        c.execute("UPDATE orders SET amount = '" + str(i[5] - q) + "' WHERE reqid =" + "\'" + str(i[0]) + "\'")
        if not mm: add_asset(uid, product, -1*float(amount))
        add_asset(i[7], product, float(amount))
        add_history(login, product, q, q*i[6], "sell")
        sub_from_debt(i[0], q*i[6])
        q = 0
        list_counter += 1
        break
      else:
        q -= i[5]
        total += i[5] * i[6]
        transaction_list.insert(list_counter, [i[0], reqid, i[7], float(uid), i[5], i[5] * i[6]])
        add_to_buffer(['delete', reqid])
        c.execute("DELETE FROM orders WHERE reqid =" + "\'" + str(i[0]) + "\'")
        if not mm: add_asset(uid, product, -1*i[5])
        add_asset(i[7], product, i[5])
        add_history(login, product, i[5], i[5]*i[6], "sell")
        sub_from_debt(i[0], i[5]*i[6])
        calc_average(product, -1*i[6], 'buy')    #Do we need that?
        box_graph(product, 'buy')
        list_counter += 1

    if q != 0 and limit:
      c.execute(f"INSERT INTO orders VALUES({reqid}, '{from_u}', '{b[1]}', '{b[2]}', '{product}', {q}, {price}, {uid})")
      add_to_buffer(['add', reqid, from_u, b[1] ,b[2], product, str(q), price, uid])
      calc_average(product, price, 'sell')    #Do wee need that?
      box_graph(product, 'sell')
  if not mm: substract(buy, total, login)
  # print()
  # print("Total Cost:" ,total, '\n')
  #if ENABLE_OUTPUT: print("Resulting data base:")
  #if ENABLE_OUTPUT: print_table()
  # print("\nFINISHED\n")
  #c.close()
  #conn.close()
  if (len(transaction_list) == 0):
    return [str(reqid)]
  return transaction_list

def update():
  return buffer


def rec(client_socket):
  start = time.time()
  while True:
    if time.time()-start >= 0.95:
      print("Too much time wasted...")
      return False
    try:
      temp = pickle.loads(client_socket.recv(1024))
      return temp
    except Exception as exception:
      pass

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

global u, conn3, a, conn4, d, conn5, h, conn6, st, conn7
conn3 = sqlite3.connect('users.db')
u = conn3.cursor()
create_table_users()
conn = sqlite3.connect('orders.db')
c = conn.cursor()
conn1 = sqlite3.connect('stats.db')
s = conn1.cursor()
conn2 = sqlite3.connect('box.db')
b = conn2.cursor()
conn4 = sqlite3.connect('assets.db')
a = conn4.cursor()
conn5 = sqlite3.connect('debts.db')
d = conn5.cursor()
conn6 = sqlite3.connect('history.db')
h = conn6.cursor()
conn7 = sqlite3.connect('stars.db')
st = conn7.cursor()

stars_table()
debts_table()
history_table()
stats_table()
create_table()
box_table()
assets_table()
stats = {}
print(f'Listening for connections on {IP}:{PORT}...')

while True:
  server_socket.listen(5)
  client_socket, client_adress = server_socket.accept()
  command = rec(client_socket)
  if not command: continue
  start = time.time()

  if command == 'mm_process':
    if ENABLE_OUTPUT: print("Working on \"mm_process\" command.....")
    snd(pickle.dumps('ok'))
    got = rec(client_socket)
    if not got: continue
    got, login, key = got
    if ENABLE_OUTPUT: print("Got request: ", got, key)
    if key != 'c35312fb3a7e05b7a44db2326bd29040':
      if ENABLE_OUTPUT: print("Wrong key.....")
      snd(pickle.dumps([False]))
      continue
    ret = process(got, login, key)
    snd(pickle.dumps(ret))

  elif command == 'get':
    if ENABLE_OUTPUT: print("Working on \"get\" command.....")
    snd(pickle.dumps('ok'))
    rr = rec(client_socket)
    if not rr: continue
    if ENABLE_OUTPUT: print("Got request: ", rr)
    c.execute(rr)
    ret = c.fetchall()
    send_many(len(ret), ret)

  elif command == 'process':
    if ENABLE_OUTPUT: print("Working on \"process\" command.....")
    snd(pickle.dumps('ok'))
    got = rec(client_socket)
    if not got: continue
    got, login, password = got
    if ENABLE_OUTPUT: print("Got request: ", got, login, password)
    if not find(login, password):
      if ENABLE_OUTPUT: print("Wrong login/password combination.....")
      snd(pickle.dumps([False]))
      continue
    if float(got[4])*float(got[5]) > get_balance(login):
      if ENABLE_OUTPUT: print("Not enough money.....")
      snd(pickle.dumps([False]))
      continue
    if got[3] == 'sell' and not does_have(get_id(login), got[3], got[4]):
      if ENABLE_OUTPUT: print("Not enough assets.....")
      snd(pickle.dumps([False]))
      continue
    ret = process(got, login, password)
    snd(pickle.dumps(ret))

  elif command == 'update':
    if ENABLE_OUTPUT: print("Working on \"update\" command.....")
    snd(pickle.dumps('ok'))
    ret = update()
    if ENABLE_OUTPUT: print("To update: ", ret)
    snd(pickle.dumps(ret))

  elif command == 'delete':
    if ENABLE_OUTPUT: print("Working on \"delete\" command.....")
    snd(pickle.dumps('ok'))
    login, id = rec(client_socket)
    if not id: continue
    delete(login, id)

  elif command == 'box':
    if ENABLE_OUTPUT: print("Working on \"box\" command.....")
    snd(pickle.dumps('ok'))
    try: product, buy_sell, strt, end = rec(client_socket)
    except: continue
    ret = return_box_graph(product, buy_sell, strt, end)
    send_many(len(ret), ret)

  elif command == 'my assets':
    if ENABLE_OUTPUT: print("Working on \"my assets\" command.....")
    snd(pickle.dumps('ok'))
    try: login, password = rec(client_socket)
    except: continue
    ret = my_assets(login, password)
    send_many(len(ret), ret)

  elif command == 'bug':
    if ENABLE_OUTPUT: print("Working on \"bug\" command.....")
    snd(pickle.dumps('ok'))
    try: ret = rec(client_socket)
    except: continue
    bug_log(ret)

  elif command == 'register':
        if ENABLE_OUTPUT: print("Working on \"register\" command.....")
        snd(pickle.dumps("ok"))
        login, password = rec(client_socket)
        snd(pickle.dumps(register(login, password)))
  elif command == 'get balance':
        if ENABLE_OUTPUT: print("Working on \"get balance\" command.....")
        snd(pickle.dumps("ok"))
        login = rec(client_socket)
        snd(pickle.dumps(get_balance(login)))

  elif command == 'get id':
        if ENABLE_OUTPUT: print("Working on \"get id\" command.....")
        snd(pickle.dumps("ok"))
        login = rec(client_socket)
        snd(pickle.dumps(get_id(login)))

  elif command == 'known user':
        if ENABLE_OUTPUT: print("Working on \"known user\" command.....")
        snd(pickle.dumps("ok"))
        login, password = rec(client_socket)
        snd(pickle.dumps(find(login, password)))

  elif command == 'get history':
        if ENABLE_OUTPUT: print("Working on \"get history\" command.....")
        snd(pickle.dumps("ok"))
        login, password = rec(client_socket)
        if not find(login, password): snd(pickle.dumps(False))
        ret = return_history(login)
        send_many(len(ret), ret)

  elif command == 'stats':
    if ENABLE_OUTPUT: print("Working on \"stats\" command.....")
    snd(pickle.dumps('ok'))
    try:
      got, time_start, time_end, type = rec(client_socket)
    except : continue
    if ENABLE_OUTPUT: print("Got request: ", got, time_start, time_end)
    ret = return_stats(got, time_start, time_end, type)
    send_many(len(ret), ret)

  elif command == 'add star':
    if ENABLE_OUTPUT: print("Working on \"add star\" command.....")
    snd(pickle.dumps("ok"))
    what, login, password = rec(client_socket)
    add_star(what, login, password)
    
  elif command == 'remove star':
    if ENABLE_OUTPUT: print("Working on \"remove star\" command.....")
    snd(pickle.dumps("ok"))
    what, login, password = rec(client_socket)
    remove_star(what, login, password)

  elif command == 'get stars':
    if ENABLE_OUTPUT: print("Working on \"get stars\" command.....")
    snd(pickle.dumps("ok"))
    login, password = rec(client_socket)
    ret = get_stars(login, password)
    send_many(len(ret), ret)
  else:
    print("Unknown command.....")
    continue
  conn.commit()
  conn1.commit()
  conn2.commit()
  conn3.commit()
  conn4.commit()
  conn5.commit()
  conn6.commit()
  conn7.commit()
  print(f"Request completed in {time.time() - start} seconds.....  {len(update())}")
