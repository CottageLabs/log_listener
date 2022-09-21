#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Red Dove Consultants Limited. BSD-3-Clause licensed.
#
import argparse
import logging
import logging.handlers
import os
import pickle
import socketserver
import struct
import sys

PRINT_EXC_TYPE = False


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort


def main():
    adhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=adhf)
    aa = parser.add_argument
    aa('-p', '--port', help='Which TCP socket port', default=9020)
    aa('-fn', '--filename', help='Path to log file', default='log_file')
    aa('-l', '--level', help='Logging level', default='DEBUG')
    aa('-f', '--format', help='Logging string format',
       default="%(asctime)s [%(name)-15s] [%(levelname)-8s] %(message)s")

    options = parser.parse_args()
    # print(options.port)

    # Replace this next line with however you want to configure local logging
    # (e.g. with a RotatingFileHandler rather than a FileHandler)
    logging.basicConfig(level=options.level, format=options.format, filename=options.filename)
    logging.getLogger().info('Log listener started.')
    tcpserver = LogRecordSocketReceiver(port=int(options.port))
    print(f'Starting TCP server on port {options.port} ...')
    tcpserver.serve_until_stopped()


if __name__ == '__main__':
    try:
        rc = main()
    except KeyboardInterrupt:
        rc = 2
    except Exception as e:
        if PRINT_EXC_TYPE:
            s = ' %s:' % type(e).__name__
        else:
            s = ''
        sys.stderr.write('Failed:%s %s\n' % (s, e))
        if 'PY_DEBUG' in os.environ:
            import traceback
            traceback.print_exc()
        rc = 1
    sys.exit(rc)
