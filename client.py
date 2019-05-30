import socket
import time
import os

cid = input('Please enter ID of this client: ')
url = input('Please enter target URL: ')
mtd = input('Please enter DNS method(I/R): ')


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def send_new_req(clientID=None, tgt_url=None, DNS_mtd=None, conn_tuple = ('127.0.0.1', 10053)):
    #return a socket; need receive and closing outside the function

    if clientID is None:
        #clientID = input('Please enter ID of this client: ')
        clientID = cid
    if (clientID == 'Q') or (clientID == 'q'):
        exit()
    if tgt_url is None:
        #tgt_url = input('Please enter target URL: ')
        tgt_url = url
    if (tgt_url == 'Q') or (tgt_url == 'q'):
        exit()
    if DNS_mtd is None:
        #DNS_mtd = input('Please enter DNS method(I/R): ')
        DNS_mtd = mtd
    if (DNS_mtd == 'Q') or (DNS_mtd == 'q'):
        exit()

    mkdir('./logs')
    dir = './logs/' + clientID + '.log'
    client_log = open(dir, 'w')


    #forming message to default DNS server
    req_msg = '<' + clientID + ',' + tgt_url + ',' + DNS_mtd + '>'

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('=>Sending DNS request: ' + req_msg)
    client_log.write('\n'+req_msg[1:-1])
    #skt.setblocking(False)


    try:
        skt.connect(conn_tuple)
    except socket.timeout as tout:
        print('=>TIMEOUT CONN')
        exit()
    '''except:
        print('=>CONN FAILURE')
        exit()'''
    skt.send(req_msg.encode('utf-8'))#send message to default DNS server
    return skt


def analyse_msg(recv_msg):
    reply_slices = list(range(4))

    comma_loc1 = recv_msg.find(',', 1, -1)
    reply_slices[0] = recv_msg[1: comma_loc1]#status

    comma_loc2 = recv_msg.find(',', comma_loc1 + 1, -1)
    reply_slices[1] = recv_msg[comma_loc1 + 1: comma_loc2]#ID

    comma_loc3 = recv_msg.find(',', comma_loc2 + 1, -1)
    if comma_loc3:
        reply_slices[2] = recv_msg[comma_loc2 + 1: comma_loc3]
        reply_slices[3] = recv_msg[comma_loc3 + 1: -1]
    else:
        reply_slices[2] = recv_msg[comma_loc2 + 1: -1]
        reply_slices[3] = None
    return reply_slices


client_skt = send_new_req()
client_skt.settimeout(15)
dir = './logs/' + cid + '.log'
client_log = open(dir, 'a')

while True:
    try:
        receive = str(client_skt.recv(1024), encoding="utf-8")
        print(receive)
        if receive == 'shut':
            print('=>SHUTTING')
            client_skt.close()
            client_log.close()
            exit()
        reply = analyse_msg(receive)
        print('=>Receive from DNS server:\n        ' + str(receive))

        while True:
            print('reply = ' + str(reply))
            client_log.write('\n' + receive[1:-1])
            if reply[0] == '0x00':
                print('=>Result from DNS server:\n        ' + reply[2] + '\n')
                break
            elif reply[0] == '0x01':
                print('=>New DNS server:\n        ' + reply[2] + ':' + reply[3] + '\n')
                client_skt.close()
                iter = send_new_req(reply[1], url, 'I', ('127.0.0.1', int(reply[3])))
                iter.settimeout(15)
                while True:
                    try:
                        iter_recv = str(iter.recv(1024), encoding="utf-8")
                        if iter_recv == 'shut':
                            iter.close()
                            exit()
                        reply = analyse_msg(iter_recv)
                        print('=>Receive from NEW DNS server:\n        ' + str(iter_recv))
                        client_log.write('\n' + iter_recv[1:-1])
                    except socket.timeout as tout:
                        print('=>Iter Socket Timeout, closing')
                        iter.close()
                        exit()
                continue
            elif reply[0] == '0xEE':
                print('=>Invalid format:\n        ' + reply[2] + '\n')
                break
            elif reply[0] == '0xFF':
                print('=>Host not found:\n        ' + reply[2] + '\n')
                break
            else:
                print('=>receive msg error\n')
                break
    except socket.timeout as tout:
        print('=>Socket Timeout, closing')
        client_skt.close()
        client_log.close()
        exit()

