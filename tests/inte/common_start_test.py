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
import time
import sys
import os
import signal
import logging

from common.start import generic_parser
from common.start import main

if __name__ == '__main__':
    # a test environment to make common/start.py go. We set up a fake configuration,
    # specifying things needed to lock this process node and create log files.
    # Next we define a simple run function that just sleeps for a second then
    # prints to the log. Finally, we setup a signal handler on USR2 so we can
    # shutdown the "daemon" gracefully.
    #
    confs = [
        {'host' : 'localhost', 'lockport' : 8080, 'logdir' : 'log0',},
        {'host' : 'localhost', 'lockport' : 8090, 'logdir' : 'log1',},
        ]
    parser = generic_parser('testing start.py')
    args = parser.parse_args()
    # our test daemon
    #
    GO = True
    def test_go(log, logdir, args, here, **kwargs):
        global GO
        logging.info('starting test gostartgo')
        while GO:
            try:
                time.sleep(1)
                logging.info('beep here %s' % here)
                sys.stdout.write('beep again\n')
                sys.stdout.flush()
            except KeyboardInterrupt, e:
                GO = False

        logging.info('finished test gostartgo')
    def shutdown_handler(signum, frame):
        global GO
        GO = False
    signal.signal(signal.SIGUSR2, shutdown_handler)

    v = main(
        test_go, args, confs, 
        logname = 'start_test',
        monkey_log = True)
    sys.exit(v)

