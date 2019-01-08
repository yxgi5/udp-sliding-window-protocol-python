#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import getopt
from socket import *
from threading import *
import time
import struct
import swp

#import common
#import stopThreading
STDBY_TIME = 3000
MAX_DATA_SIZE =1024
MAX_FRAME_SIZE= 1034
ACK_SIZE= 6

def Usage():
    usage_str = '''说明：
    \trecvfile.py -f <filename> -w <window_size> -b <buffer_size> -p <port>
    \trecvfile.py -h 显⽰本帮助信息，也可以使⽤--help选项
    '''
    print(usage_str)
    
def args_proc(argv):
    '''处理命令⾏参数'''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:w:b:p:', ['help', 'filename=', 'window_size=', 'buffer_size=', 'port='])
    except getopt.GetoptError as err:
        print('错误！请为脚本指定正确的命令⾏参数。\n')
        Usage()
        sys.exit(255)
        
    if len(opts) < 1:
        print('使⽤提⽰：缺少必须的参数。')
        Usage()
        sys.exit(255)
        
    usr_argvs = {}
    
    for op, value in opts:
        if op in ('-h', '--help'):
            Usage()
            sys.exit(1)
            
        elif op in ('-f', '--filename'):
            #if os.path.isfile(value) == False:
                #print('错误！指定的参数值⽆效。\n')
                #Usage()
                #sys.exit(2)
            #else:
            usr_argvs['-f'] = value
                
        elif op in ('-w', '--window_size'):
            if int(value)<=0:
                print('错误！指定的参数值⽆效。\n')
                Usage()
                sys.exit(2)
            else:
                usr_argvs['-w'] = int(value)

        elif op in ('-b', '--buffer_size'):
            if int(value)<=0:
                print('错误！指定的参数值⽆效。\n')
                Usage()
                sys.exit(2)
            else:
                usr_argvs['-b'] = int(value)
                
        elif op in ('-p', '--port'):
            if int(value)<=0:
                print('错误！指定的参数值⽆效。\n')
                Usage()
                sys.exit(2)
            else:
                usr_argvs['-p'] = int(value)
        else:
            print('unhandled option')
            sys.exit(3)
    
    if((('-f') or ('--filename')) and (('-w') or ('--window_size')) and (('-b') or ('--buffer_size')) and (('-p') or ('--port'))) in usr_argvs:
        return usr_argvs
    else:
        print('缺少命令⾏参数。\n')
        Usage()
        sys.exit(255)

def checksum(frame, count):
    sum = 0
    frame1=struct.unpack('b'*count,frame[0:count])
    for index in range(count):
        sum = sum+frame1[index]
        if (sum & 0xFFFF0000)!=0:
        #if (sum >0xFFFF):
            sum = sum & 0xFFFF
            sum = sum+1
    return (sum & 0xFF)

def read_frame(frame):
    if(frame[0]==0x0):
        eot = True
    else:
        eot = False
        
    data1=frame[1:5]
    net_seq_num = struct.unpack('I',data1)[0]
    seq_num = ntohl(net_seq_num)
    
    data1=frame[5:9]
    net_data_size = struct.unpack('I',data1)[0]
    data_size = ntohl(net_data_size)
    
    data = frame[9:9+data_size]
    if(frame[9+data_size]==checksum(frame, 9+data_size)):
        chksum = False
    else:
        chksum = True
    return chksum, seq_num, data, data_size, eot

def create_ack(seq_num, error):
    ack = []
    
    if error == True:
        ack.insert(0, 0x00)
    else:
        ack.insert(0, 0x01)
        
    net_seq_num = htonl(seq_num)
    
    ack.insert(1, net_seq_num&0xff)
    ack.insert(2, (net_seq_num>>8)&0xff)
    ack.insert(3, (net_seq_num>>16)&0xff)
    ack.insert(4, (net_seq_num>>24)&0xff)
    
    ack.insert(5, checksum(struct.pack('B'*len(ack), *ack), ACK_SIZE-1))
    
    return struct.pack('B'*len(ack), *ack)

def elapsed_time_ms(current_time, start_time):
    k=current_time-start_time
    return k.seconds*1000+round(k.microseconds/1000)
    pass
    
def main(usr_argvs):
    #print(usr_argvs)
    recv_buffer_size = usr_argvs['-b']
    max_buffer_size = MAX_DATA_SIZE*recv_buffer_size
    LC_PORT=usr_argvs['-p']
    fname=usr_argvs['-f']
    window_len = usr_argvs['-w']
    LC_HOST = ''
    try:
        file=open(fname, 'wb')
    except Exception as ret:
        print(ret);
        
    a=swp.Receiver(LC_HOST, LC_PORT)
    recv_done = False
    buffer_num = 0
    while (recv_done is False):
        recv_done, buffer=a.recv(window_len, recv_buffer_size)
        file.write(buffer)
        if (recv_done is True):
           break
        buffer_num=buffer_num+1
        print('#%d'%buffer_num)
    print("[RECEIVED %ld BYTES]"% (buffer_num * max_buffer_size + len(buffer)) );
    print("All done :)");

if __name__ == '__main__':
    usr_argvs = {}
    usr_argvs = args_proc(sys.argv)
    #print(usr_argvs)

    main(usr_argvs)
    
    
