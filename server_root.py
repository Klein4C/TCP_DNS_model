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


def check_url(url):
    #print('url[len(url) - 3:] = '+url[len(url) - 3:])
    if url[len(url) - 3:] == 'com':
        authid = 1
    elif url[len(url) - 3:] == 'gov':
        authid = 2
    elif url[len(url) - 3:] == 'org':
        authid = 3
    else:
        authid = None

    return authid


def forward_req(req):#req is a list with ID, URL and I/R
    clientID = req[0]
    tgt_url = req[1]
    ck = check_url(tgt_url)
    if ck is not None:
        port = ck + 10054
        print('recursive port='+str(port))
        DNS_mtd = req[2]
        fwd_msg = '<' + clientID + ',' + tgt_url + ',' + DNS_mtd + '>'
        print('=>Forwarding DNS request: '+fwd_msg)

        fwd_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_tuple = ('127.0.0.1', port)
        fwd_skt.connect(conn_tuple)
        fwd_skt.send(fwd_msg.encode('utf-8'))
        return fwd_skt
    else:
        return None


def keep_accepting():
    while True:
        sock, addr = skt.accept()
        online_clients.enq(sock)
        new_th = threading.Thread(target=root_recv, args=(sock, addr))
        new_th.start()


def root_recv(sock, addr):
    try:
        print('==>New TCP link from: %s' % str(addr))
        data = sock.recv(1024)
        recv_str = data.decode('utf-8')
        print('        ' + recv_str + '\n')
        conf_msg = analyse_msg(recv_str)  # 0:id 1:url

        if conf_msg[1] is not None:
            if conf_msg[2] == 'R':
                print('==>forwarded'+ str(conf_msg) + '\n')
                fwd_skt = forward_req(conf_msg)
                if fwd_skt is not None:
                    fwd_skt.settimeout(15)
                    while True:
                        try:
                            receive = str(fwd_skt.recv(1024), encoding="utf-8")
                            print(receive)
                            reply_msg = receive
                            break
                        except socket.timeout as tout:
                            print('timeout')
                            reply_msg = '<0xFF,ROOT,"Host not found">'
                            break
                        except:
                            print('other error')
                            reply_msg = '<0xFF,ROOT,"Host not found">'
                            break
                else:
                    reply_msg = '<0xFF,ROOT,"Host not found">'
            elif conf_msg[2] == 'I':
                url_ck = check_url(conf_msg[1])
                if url_ck is not None:
                    iterate_port = url_ck + 10054
                    print('iterate_port='+str(iterate_port))
                    reply_msg = '<0x01,ROOT,127.0.0.1,' + str(iterate_port) + '>'
                else:
                    reply_msg = '<0xEE,ROOT,"Invalid Format">'
            else:
                reply_msg = '<0xEE,ROOT,"Invalid Format">'
        else:
            reply_msg = '<0xEE,ROOT,"Invalid Format">'
        sock.sendall(bytes(reply_msg, encoding='utf-8'))
        online_clients.deq()
        print('==>replied: ' + reply_msg + '\n')
    except socket.timeout as tout:
        print('==>TIMEOUT ' + str(addr))


if __name__ == '__main__':
    #dict = open(os.getcwd() + '/com.dat', 'r')
    #dict_lines = dict.readlines()
    try:
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #establish a socket
        skt.setblocking(0)
        skt.settimeout(120)
        bind_tuple = ('127.0.0.1', 10054)
        skt.bind(bind_tuple)
        skt.listen(5)
        print('=>Waiting for conn (max link: 5)...')

        acpt = threading.Thread(target=keep_accepting)
        acpt.setDaemon(True)
        acpt.start()

        while True:
            pass

    except socket.timeout as tout:
        print('----TIMEOUT----\nSHUTTING')
        shutting = True
        while not online_clients.isEmpty():
            shut_sock = online_clients.deq()
            try:
                print('==>Send SHUT remaining' + str(online_clients.size()))
                shut_sock.sendall(bytes('shut', encoding='utf-8'))
            except:
                pass
        exit()
    except KeyboardInterrupt:
        print('Keyboard Interrupt------------')
        shutting = True
        while not online_clients.isEmpty():
            shut_sock = online_clients.deq()
            try:
                print('==>Send SHUT remaining' + str(online_clients.size()))
                shut_sock.sendall(bytes('shut', encoding='utf-8'))
            except:
                pass
    except:
        pass





