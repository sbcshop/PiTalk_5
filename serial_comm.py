#!/usr/bin/python3

import serial, re, threading, logging


class SerialComm(object):
    """ Low level serial operations """
    log = logging.getLogger('pitalk.serial.SerialComm')
    # End of response
    RESPONSE = re.compile(r'^OK|ERROR|(\+CM[ES] ERROR: \d+)|(COMMAND NOT SUPPORT)$')
    # Default timeout for serial reading(seconds)
    timeout = 5

    def __init__(self, port, baudrate = 115200, handlerNotification=None, *args, **kwargs):
        """ Constructor """
        self.alive = False
        self.port = port
        self.timeout = 5
        self.baudrate = baudrate
        self._responseEvent = None
        self._expectResponse = None
        self._response = None
        self._notification = []
        self._txLock = threading.Lock()
        self.handlerNotification = handlerNotification

        #self.notifyCallback = self.notifyCallbackFunc

    def connect(self):
        """ Connects to the device """
        self.serial = serial.Serial(port=self.port,baudrate=self.baudrate,timeout=self.timeout)
        self.alive = True
        self.rxThread = threading.Thread(target=self._readLoop)
        self.rxThread.daemon = True
        self.rxThread.start()

    def close(self):
        """ Stops read thread, waits for it to exit cleanly and close serial port """
        self.alive = False
        self.rxThread.join()
        self.serial.close()

    def _handleLineRead(self, line, checkResponse=True):
        if self._responseEvent and not self._responseEvent.is_set():
            self._response.append(line)
            if not checkResponse or self.RESPONSE.match(line):
                # End of response reached; notify waiting thread
                self.log.debug('response: %s', self._response)
                self._responseEvent.set()
        else:
            # Nothing was waiting for this - treat it as notification
            self._notification.append(line)
            if self.serial.inWaiting() == 0:
                # No more chars for this notification
                self.log.debug('notification: %s', self._notification)
                self.handlerNotification(self._notification)
                self._notification = []

    def _readLoop(self):
        """ Read thread main loop """
        try:
            while self.alive:
                line = self.serial.readline().decode()
                if line != '':
                    if self._expectResponse:
                        if line == self._expectResponse:
                            self._expectResponse = False
                            self._handleLineRead(line, checkResponse = False)
                    else:
                        self._handleLineRead(line)
                       
                    
        except serial.SerialException as err:
            self.alive = False
            try:
                self.serial.close()
            except Exception:
                pass

    def write(self, data, waitForResponse=True, timeout=5, response=None):
        with self._txLock:
            if waitForResponse:
                if response:
                    self._expectResponse = list(response)
                self._response = []
                self._responseEvent = threading.Event()
                self.serial.write(data.encode())
                if self._responseEvent.wait(timeout):
                    self._responseEvent = None
                    self._expectResponse = False
                    return self._response
                else:
                    self._responseEvent = None
                    self._expectResponse = False
                    # raise Timeout Exception
            else:
                self.serial.write(data.encode())
            
            
    
        
    
