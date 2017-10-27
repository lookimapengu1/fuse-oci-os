#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import os
import logging
import requests

from sys import argv, exit
from time import time
from fuse import FUSE, Operations, LoggingMixIn

import signing_sample_python as ssp

class Rest(LoggingMixIn, Operations):
    '''
    A simple REST API filesystem. Requires requests HTTP module.
    '''

    def __init__(self, host):
        self.host = host;

    def getattr(self, path, fh=None):
        # fake stat for now
        st = os.lstat('/tmp')
        ssp.debug_message('get attr for ' + path)
        if path == '/':
            return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        else:
            url = "%s%s" % (self.host, path)
            url = url.rstrip('/')
            #ssp.debug_message(url)
            res = ssp.get_object_metadata(url)
            print(res)
            temp = dict(st_atime=st[7], st_ctime=st[9], st_gid=st[5], st_mode=33206, 
                        st_mtime=res['lastmod'], st_nlink=1, st_size=res['size'], st_uid=st[4])
            return temp
            
        #atime: last access time, ctime: last change time, gid: group id of owner, mode: protection,
        #mtime: last modify time, nlink: num hard links, size: size in bytes, uid: user id of own
        #return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
            #'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
        
    def read(self, path, size, offset, fh):
        url = "%s/%s" % (self.host, path)
        r = requests.get(url)
        return r.json()

    def readdir(self, path, fh):
        url = "%s%s" % (self.host, path)
        url = url.rstrip('/')
        result = ssp.get_objects(url)
        return ['.', '..'] + [name["name"]
                              for name in result]
    
    def rename(self, path, newpath):
        print("hi")

    def create (self, path, mode, fi=None):
        print ("copying file")

if __name__ == '__main__':
    if len(argv) != 3:
        print('usage: %s <api endpoint> <mountpoint>' % argv[0])
        exit(1)

    logging.basicConfig(level=logging.DEBUG)

    fuse = FUSE(Rest(argv[1]), argv[2], foreground=True, nothreads=True)

