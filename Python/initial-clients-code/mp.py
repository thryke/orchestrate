import os
from qgis.core import *
from multiprocessing import Process,Queue,Pipe

if __name__ == '__main__':
    parent_conn,child_conn = Pipe()
    print('test')
    from qgisclient import f
    p = Process(target=f, args=(child_conn,))
    p.start()
    print(parent_conn.recv())   # prints "Hello"