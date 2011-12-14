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

"""common/start.py

Common utility module for starting up daemonized processes. Utilizes 
the code in common/serverlock.py to make sure the correct number of
configured processes run at once. 

Much of the code herein helps with stuff like setting up logs, writing 
pidfiles, and forking processes.

Also, defines useful common arguments related to daemonizing. 
"""

import os
import sys
import stat
import signal
import time

import argparse
import logging
import logging.handlers

import conf
import serverlock

def generic_parser(description):
    """creates a generic argparse ArgumentParser, providing a base set of
    arguments any process/daemon would find useful.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--daemon', 
        default=False, 
        action='store_true', 
        help='Daemonize the process. Will close stdout/stderr in favor of logging' 
                'both to the log file specified in logfile')
    parser.add_argument(
        '-L',
        '--logfile', 
        default = None, 
        help='Logfile, written in either the base directory the the logdir field'
            'defined in the service dictionary. ')
    progname = os.path.split(sys.argv[0])[-1]
    default_pidfile = '%s.pid' % progname.split('.')[0]
    parser.add_argument(
        '--pidfile',
        default = default_pidfile, 
        help = 'Overwrite the name of the pid file when --daemon is specified.' 
            'Default is: %(default)s')
    parser.add_argument(
        '-v', 
        '--verbose',
        default = False, 
        action = 'store_true', 
        help = 'Verbose on (loglevel=DEBUG).',
        )
    return parser

##########
# LOGGING
##########

LOG_SIZE_MAX  = 16*1024*1024
LOG_COUNT_MAX = 50
LOG_FRMT      = '[%(name)s|%(asctime)s|%(levelname)s] %(message)s'

class LogStreamWrap(object):
    
    def __init__(self, log, *args, **kwargs):
        self._log = log
        self._prefix = ''

    def write(self, s):
        if s[-1] == '\n':
            s = s[:-1]
        self._output(self._prefix + s)

    def _output(self, s):
        raise NotImplemented() 

    def flush(self):
        pass

class StdOutWrap(LogStreamWrap):

    def __init__(self, *args, **kwargs):
        super(StdOutWrap, self).__init__(*args, **kwargs)
        self._prefix = '>> '

    def _output(self, s):
        self._log.info(s)

class StdErrWrap(LogStreamWrap):

    def __init__(self, *args, **kwargs):
        super(StdErrWrap, self).__init__(*args, **kwargs)
        self._perfix = '!> '

    def _output(self, s):
        self._log.error(s)

def setup_logdir(logdir):
    """setup the logdir. os.makedirs() it if it doesn't exist. 
    creates with full writes for all users to read and write to it. 
    """
    # if the logdir is not there, create it
    #
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
    # for simlicity we make it readable globally. can probably change this. if
    # we want.
    #
    os.chmod(logdir, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)

def setup_logging(logname, logdir, args, monkey = False):
    """Given an existing logdir (setup with setup_logdir above), sets up the
    logging streams for this process. 
    """
    log = logging.getLogger(logname)
    log.setLevel(logging.INFO)
    log_fmt = logging.Formatter(LOG_FRMT)
    if args.verbose:
        log.setLevel(logging.DEBUG)
    # always have a stream handler to stdout
    #
    if args.logfile is None:
        stream_hndlr = logging.StreamHandler(sys.stdout)
        stream_hndlr.setFormatter(log_fmt)
        log.addHandler(stream_hndlr)

    else:
        logfile = os.path.join(logdir, args.logfile)
        file_hndlr = logging.handlers.RotatingFileHandler(
            logfile, 'a', LOG_SIZE_MAX, LOG_COUNT_MAX)
        file_hndlr.setFormatter(log_fmt)
        log.addHandler(file_hndlr)

    if monkey:
        logging.root = log
        logging.Logger.root = logging.root 
        logging.manaer = logging.Manager(logging.Logger.root)
    return log

##########
# DAEMON
##########

def write_pid(pidfile):
    fd = file(pidfile, 'w')
    fd.write('%d' % os.getpid())
    fd.flush()
    fd.close()

class IAmParent(Exception):
    pass

class PidFileWriteException(Exception):
    pass

def daemonize(pidfile=None):
    """daemonize the process with os.fork(). If pidfile is provied, writed
    the pid of the child process to the file.

    """
    pid = os.fork()
    if pid:
        # we're the parent, bow out
        #
        raise IAmParent() 

    # write the pid file
    #
    try:
        if pidfile is not None:
            write_pid(pidfile) 
    except IOError, e:
        print 'Unable to write pid file, exititng'
        raise PidFileWriteException()

    # FUTURE POSTFORK optimizations
    # Often times it's good to setup process context before we fork. These
    # tasks can include stuff like:
    #  a) up the maximum # of file descriptors. 
    #  b) set user and group to nobody
    #  c) make the process dumpable
    #

########
# MAIN
########

def main(realmain, args, confs, logname = 'logger', **kw):
    """main start method. 
    
    The function will setup the process's logging, and fork if sepcified,
    and then call the realmain method.

    Takes the following parameters:

    realmain: a callable which is executed after all the logging and 
        daemon (forking) work has been done. 
    args: the parsed arguments (argparse.Namespace instnace).
    confs: The service configuration (a list of dicts or dict-like objects), 
        see the conf module for more information.
    """
    # lock the node
    #
    here = serverlock.lock_server(confs)
    if here is None:
        return 1
    # setup the log 
    #
    logdir = here.get('logdir', 'logs')
    setup_logdir(logdir)
    log = setup_logging(
        logname, logdir, args, monkey=kw.get('monkey_log', False)) 

    # fork
    #
    if args.daemon:
        try:
            pidfile = os.path.join(logdir, args.pidfile)
            daemonize(pidfile)
        except IAmParent:
            return 0
        except PidFileWriteException, e:
            return 1

        # close standard file descriptors
        #
        os.close(sys.stdin.fileno())
        os.close(sys.stdout.fileno())
        os.close(sys.stderr.fileno())
        # place our log stream wrapper in place of the std file desciptors
        #
        sys.stdout = StdOutWrap(log)
        sys.stderr = StdErrWrap(log)


    # execute realmain
    #
    realmain(log, logdir,  args, here, **kw)
    return 0


