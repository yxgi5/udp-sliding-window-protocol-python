#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import swp
from time import ctime


TGT_HOST = '127.0.0.1'
#TGT_HOST = '192.168.0.102'
'''
pc:192.168.0.102
pi:192.168.0.103 ##
'''
TGT_PORT = 21568
TGT_ADDR = (TGT_HOST, TGT_PORT)
LC_HOST = ''
LC_PORT = 21567
LC_ADDR = (LC_HOST, LC_PORT)

rcvSock = swp.ReceiverOpen(LC_HOST, LC_PORT)

while True:
    print('waiting for message...')
    data, addr = rcvSock.recv()
    print(data.decode(), 'received from:', addr)

rcvSock.close()
