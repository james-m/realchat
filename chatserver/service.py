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

'''
chatserver/service.py 

The server side code for a given chat service instance. 

'''

import sys
import os
import signal

import wsgiref.simple_server
import conf
import common.start
import chatroom

def serve_wsgiref(log, logdir, args, here, **kwargs):
    '''The realmain serve method, called by common.start.main()
    with nice newly minted log and the here dictionary, which is
    locked by common.serverlock.lock_server().

    The here has the host and port name, which we use to construct our
    wsgiref httpd to expose our bottle wsgi app. 
    '''
    host = here['host']
    httpport = here['httpport']
    log.info('chat service starting. host: %s port: %s' % (
        host, httpport))
    app = chatroom.APP()
    httpd = wsgiref.simple_server.make_server(host, httpport, app)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt, e:
        pass
    log.info('chat service done')

def main():
    srvs = conf.get('chatservers')
    parser = common.start.generic_parser('chatserver')
    args = parser.parse_args()
    return common.start.main(
        serve_wsgiref, args, srvs, 
        logname = 'chatserver',
        monkey_log = True,
        )

if __name__ == '__main__':
    v = main()
    sys.exit(v)
