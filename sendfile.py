#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import io
import getopt
from socket import *
from threading import *
import time
#import common
import re
import swp
MAX_DATA_SIZE =1024

def Usage():
    usage_str = '''说明：
    \trecvfile.py -f <filename> -w <window_size> -b <buffer_size> -d <destination_ip> -p <port>
    \trecvfile.py -h 显⽰本帮助信息，也可以使⽤--help选项
    '''
    print(usage_str)
    
def check_ip(ipAddr):
    compile_ip=re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ipAddr):
        return True 
    else:  
        return False
    
def args_proc(argv):
    '''处理命令⾏参数'''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:w:b:d:p:', ['help', 'filename=', 'window_size=', 'buffer_size=', 'destination_ip=','port='])
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
            if os.path.isfile(value) == False:
                print('错误！指定的参数值⽆效。\n')
                Usage()
                sys.exit(2)
            else:
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
                
        elif op in ('-d', '--destination_ip'):
            if check_ip(value) == False:
                print('错误！指定的参数值⽆效。\n')
                Usage()
                sys.exit(2)
            else:
                usr_argvs['-d'] = value
                
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
    
    if((('-f') or ('--filename')) and (('-w') or ('--window_size')) and (('-b') or ('--buffer_size')) and (('-d') or ('--destination_ip')) and (('-p') or ('--port'))) in usr_argvs:
        return usr_argvs
    else:
        print('缺少命令⾏参数。\n')
        Usage()
        sys.exit(255)
        
def main(usr_argvs):
    max_buffer_size = MAX_DATA_SIZE * usr_argvs['-b']
    dest_port=usr_argvs['-p']
    fname=usr_argvs['-f']
    window_len = usr_argvs['-w']
    dest_ip = usr_argvs['-d']
    LC_HOST = ''
    LC_PORT = 8001
    try:
        file=open(fname, 'rb')
    except Exception as ret:
        print(ret);

    read_done = False
    buffer_num = 0
    while (read_done is False):
        buffer=file.read(max_buffer_size)
        buffer_size=len(buffer)
        if (buffer_size == max_buffer_size):
            temp = file.read(1)
            next_buffer_size = len(temp)
            if (next_buffer_size == 0):
                read_done = True
                pass
            file.seek(-1, io.SEEK_CUR)
            pass
        elif (buffer_size < max_buffer_size):
            read_done = True
            pass
        swp.Transmitter(LC_HOST, LC_PORT, buffer, dest_ip, dest_port, window_len, read_done)
        
        if (read_done is True):
           break
        buffer_num=buffer_num+1
        print(buffer_num)
    file.close()
    
    print("[SENT %ld BYTES]"% (buffer_num * max_buffer_size + buffer_size) );
    print("All done :)");

if __name__ == '__main__':
    usr_argvs = {}
    usr_argvs = args_proc(sys.argv)
    #print(usr_argvs)

    main(usr_argvs)
