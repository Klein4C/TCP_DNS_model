import socket
import threading
import time


class STACK:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        if not self.isEmpty():
            return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)


def tcp_rec(sock, addr):
    print('==>New TCP link from: %s' % str(addr))
    count = 0
    while True:
        print('-->msg ' + str(count) + ' start')
        data = sock.recv(1024)
        time.sleep(1)
        if data == 'exit' or not data:
            break
        conf_msg = '-->confirm msg: %s' % data.decode('utf-8')
        sock.sendall(bytes(conf_msg, encoding='utf-8'))
        print(conf_msg)
        print('-->msg ' + str(count) + ' ended')
        count += 1

    sock.close()
    print('==>TCP link from: "' + str(addr) + '" closed')
    exit()


skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #establish a socket
'''--------------------------
    socket.AF_INET ==> ipv4
    socket.AF_INET6 ==> ipv6
--------------------------'''
skt.settimeout(300);
bind_tuple = ('127.0.0.1', 10053)
skt.bind(bind_tuple)
skt.listen(5)
print('=>Waiting for conn (max link: 5)...')

while True:
    sock, addr = skt.accept()
    t = threading.Thread(target=tcp_rec, args=(sock, addr))

    t.start()
