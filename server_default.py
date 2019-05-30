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
shutting = False


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


def forward_req(req):#req is a list with ID, URL and I/R
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

'''def send_shut(address):
    shut_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #conn_tuple = (address)
    shut_skt.connect(address)
    shut_skt.send('shut'.encode('utf-8'))
    '''


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


mkdir('./logs')
mapping = open('./logs/mapping.logs', 'a')
default_log = open('./logs/server_default.log', 'w')


def tcp_rec(sock, addr, online_queue):
    try:
        print('==>New TCP link from: %s' % str(addr))
        count = 0
        sock.settimeout(14)
        data = sock.recv(1024)
        time.sleep(0.1)

        recv_msg = data.decode('utf-8')
        print('        ' + recv_msg + '\n')
        default_log.write(recv_msg[1:-1]+'\n')
        conf_msg = analyse_msg(recv_msg)

        online_queue.enq(sock)
        reply_msg = 'shut'
        if not shutting:
            if conf_msg[1] is not None:
                print('==>forwarded'+ str(conf_msg) + '\n')
                #reply_msg = '<0x00,' + conf_msg[0] + ',' + 'sample>'
                fwd_skt = forward_req(conf_msg)
                fwd_skt.settimeout(15)
                while True:
                    try:
                        receive = str(fwd_skt.recv(1024), encoding="utf-8")
                        print(receive)
                        if receive == 'shut':
                            print('=>SHUTTING')
                            skt.close()
                            exit()
                        reply_msg = receive
                        break
                    except socket.timeout as tout:
                        print('timeout')
                        reply_msg = '<0xEE,DEFAULT,"Host not found">'
                        break
                    except:
                        print('other error')
                        reply_msg = '<0xEE,DEFAULT,"Host not found">'
                        break
                online_queue.deq()
            else:
                reply_msg = '<0xEE,DEFAULT,"Invalid format">'
        else:
            reply_msg = 'shut'
        default_log.write(reply_msg[1:-1] + '\n')
        if reply_msg.startswith('<0x00'):
            mapping.write(conf_msg[1]+' '+reply_msg[10:-1]+'\n')
        sock.sendall(bytes(reply_msg, encoding='utf-8'))
        print('==>replied: ' + reply_msg + '\n')
        #exit()
        default_log.write('\n')
    except socket.timeout as tout:
        print('==>TIMEOUT ' + str(addr))
        default_log.write('\n')


def keep_accepting():
    while not shutting:
        try:
            sock, addr = skt.accept()
            online_clients.enq(sock)
            print('new tcp_rec')
            new_th = threading.Thread(target=tcp_rec, args=(sock, addr, online_clients))
            new_th.start()
        except:
            pass


if __name__ == '__main__':
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #establish a socket
    skt.setblocking(0)

    bind_tuple = ('127.0.0.1', 10053)
    skt.bind(bind_tuple)
    skt.listen(5)
    skt.settimeout(60)
    print('=>Waiting for conn (max link: 5)...')
    acpt = threading.Thread(target=keep_accepting)
    acpt.setDaemon(True)
    acpt.start()
    print('started accepting')

    try:
        while True:
            pass
    except KeyboardInterrupt:
        mapping.close()
        default_log.close()
        print('KeyboardInterrupt')
        shutting = True
        while not online_clients.isEmpty():
            shut_sock = online_clients.deq()
            try:
                print('==>Send SHUT remaining:' + str(online_clients.size()))
                shut_sock.sendall(bytes('shut', encoding='utf-8'))
            except:
                pass
