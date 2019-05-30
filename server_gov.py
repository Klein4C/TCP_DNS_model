import socket
import threading
import time
from collections import deque
import re
import os


class QUEUE:
    def __init__(self, init_q=None): #here the None is to avoid mutable arg value
        if init_q is None:
            init_q = []
        self.items = deque(init_q)

    def isEmpty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def enq(self, item):
        self.items.append(item)

    def deq(self):
        return self.items.popleft()

    def peek(self):
        if not self.isEmpty():
            return self.items[0]


online_clients = QUEUE()


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def analyse_msg(recv_msg):
    msg_slices = list(range(3))
    comma_loc1 = recv_msg.find(',', 1, -1)
    msg_slices[0] = recv_msg[1:int(comma_loc1)]#ID

    msg_format = re.compile(r"^<[^,]*,"
                            r"(([a-zA-Z])|([a-zA-Z][a-zA-Z])|"
                            r"([a-zA-Z][0-9])|([0-9][a-zA-Z])|"
                            r"([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\."
                            r"([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})"
                            r",[IR]>$", re.IGNORECASE)
    if re.match(msg_format, recv_msg):
        comma_loc2 = recv_msg.find(',', comma_loc1 + 1, -1)
        msg_slices[1] = recv_msg[comma_loc1 + 1: comma_loc2]#URL
        msg_slices[2] = recv_msg[-2: -1]#method
    else:
        msg_slices[1] = None
        msg_slices[2] = None
    return msg_slices



def forward_req(req, result):#req is a list with ID, URL and I/R
    clientID = req[0]
    tgt_url = req[1]
    DNS_mtd = req[2]
    fwd_msg = '<' + clientID + ',' + tgt_url + ',' + DNS_mtd + '>'
    print('=>Forwarding DNS request: <'+fwd_msg+'>')

    fwd_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn_tuple = ('127.0.0.1', 10054)
    fwd_skt.connect(conn_tuple)
    fwd_skt.send(fwd_msg.encode('utf-8'))
    return fwd_skt


def com_recv(sock, addr):
    print('==>New TCP link from: %s' % str(addr))
    data = sock.recv(1024)
    recv_str = data.decode('utf-8')
    print('        ' + recv_str + '\n')
    conf_msg = analyse_msg(recv_str)#0:id 1:url

    exist = False
    for line in dict_lines:
        found = line.find(conf_msg[1])
        if found:
            space = line.find(' ')
            reply_msg = '<0x00,GOV,' + line[space + 1: -1] + '>'
            exist = True
            break
    if not exist:
        reply_msg = '<0xEE,GOV,"Host not found">'
    sock.sendall(bytes(reply_msg, encoding='utf-8'))
    online_clients.deq()
    print('==>replied: ' + reply_msg)
    #exit()
    #except socket.timeout as tout:
    #    print('==>TIMEOUT ' + str(addr))


def keep_accepting():
    while True:
        sock, addr = skt.accept()
        online_clients.enq(sock)
        new_th = threading.Thread(target=com_recv, args=(sock, addr))
        new_th.start()


if __name__ == '__main__':
    dict = open(os.getcwd() + '/gov.dat', 'r')
    dict_lines = dict.readlines()

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #establish a socket
    skt.setblocking(0)
    skt.settimeout(120)
    bind_tuple = ('127.0.0.1', 10056)
    skt.bind(bind_tuple)
    skt.listen(5)
    print('=>Waiting for conn (max link: 5)...')
    acpt = threading.Thread(target=keep_accepting)
    acpt.setDaemon(True)
    acpt.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('Keyboard Interrupt------------')
        while not online_clients.isEmpty():
            shut_sock = online_clients.deq()
            try:
                print('==>Send SHUT remaining' + str(online_clients.size()))
                shut_sock.sendall(bytes('shut', encoding='utf-8'))
            except:
                pass
    except:
        pass





