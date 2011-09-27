# -*- Mode: Python; tab-width: 4 -*-

# Copyright (c) 2011 James McKernan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the author nor the names of other
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''common/serverlock.py

Common util module for server process locking. We use sockets because
only a single process can bind to one port at a time (lock them) and when 
the process goes away so does the lock. 

The idea is to have a pool of ports on any given host that we try in turn
when doing process initialization. If we can't bind to a given port
we move on to the next in our service list. If we run out then we stop.
'''
import socket

def servers_by_hostname(confs):
    '''given a server filter out the name ones for this host name'''
    name = socket.gethostname()
    result = []
    for c in confs:
        if c.get('host', 'localhost') in [name, 'localhost']:
            result.append(c)
    return result

def _bindlock(srv):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((srv.get('host', ''), srv['lockport']))
    s.listen(1024)
    return s

def lock_server(confs):
    for c in servers_by_hostname(confs):
        c = dict(c)
        try:
            s = _bindlock(c)
            c['lock'] = s
            return c
        except socket.error:
            pass
    return None
