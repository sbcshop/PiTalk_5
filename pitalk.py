#!/usr/bin/python3

import re, logging, time, threading

from serial_comm import SerialComm


class PiTalk(SerialComm):
    """ Class for pitalk modem interaction """
    # parsing AT command errors
    CM_ERROR_REGEX = re.compile(r'^\+(CM[ES]) ERROR: (\d+)$')
    # parsing signal strength query response\
    CSQ_REGEX = re.compile(r'^\+CSQ:\s*(\d+),')
    # parsing caller ID  for incoming calls
    CLIP_REGEX = re.compile(r'^\+CLIP:\s*"(\+(0,1)\d+)",(\d+).*$')
    # parsing New SMS indications
    CMTI_REGEX = re.compile(r'^\+CMTI:\s*"([^"]+)",(\d+)$')
    # parsing Network Name
    COPS_REGEX = re.compile(r'^\+COPS: (\d),(\d),"(.+)",(\d+).*$')
    # parsing module status
    CPAS_REGEX = re.compile(r'^\+CPAS: (\d).*$')
    # parsing incoming caller ID
    CLIP_REGEX = re.compile(r'^\+CLIP:\s*"(\+{0,1}\d+)",(\d+).*$')
    # parsing new sms indication
    CMTI_REGEX = re.compile(r'^\+CMTI:\s*"([^"]+)",(\d+).*$')
    # parsing new sms details
    CMGR_SMS_REGEX = re.compile(r'^\+CMGR: "([^"]+)","([^"]+)",[^,]*,"([^"]+)".*$')
    # parsing ADC value
    QADC_REGEX = re.compile(r'^\+QADC: (\d{1,3}(,\d{1,3})).*$')
    # parsing Call Forwarding number
    CCFC_REGEX = re.compile(r'^\+CCFC: (\d),(\d),"(.+)",(\d+).*$')
    # parsing SIM ICCID
    QCCID_REGEX = re.compile(r'^\+QCCID: (\d+).*$')
    # parsing SIM IMSI
    IMSI_REGEX = re.compile(r'^(\d+).*$')
    # parsing Call Registration Status
    CREG_REGEX = re.compile(r'^\+CREG: (\d),(\d).*$')
    CGREG_REGEX = re.compile(r'^\+CGREG: (\d),(\d).*$')
    #parsing Module coordiantes
    QCELLLOC_REGEX = re.compile(r'^\+QCELLLOC: (\d+.\d+),(\d+.\d+).*$')

    def __init__(self, port, baudrate=115200):
        super(PiTalk, self).__init__(port, baudrate, handlerNotification=self._handlerNotification)
        self.outgoingCall = False
        self.alive = False
        self.incomingCall = False
        self.callDisconnected = False
        self.callConnected = False
        self.flag_newSMS = False
        self.recievedNumberSMS = None
        self.recievedTextSMS = None
        self.recievedTimeSMS = None
        self.callerID = None
        self.messageList = []

    def _handlerNotification(self, notification):
        """ Handle notification from PiTalk """
        threading.Thread(target=self._threadNotification, kwargs={'notification': notification}).start()

    def _threadNotification(self, notification):
        for line in notification:
            if 'RING\r\n' in line:
                # Incoming Call
                self.incomingCall = True
                print('incoming call true')
                self._handlerIncomingCall(notification)
                print(notification)
                return
            elif line.startswith('+CMTI'):
                self._hanlderSMSRecieved(line)
                return
            elif 'NORMAL POWER DOWN' in line:
                self.alive = False
                return

    def _handlerIncomingCall(self, notification):
        self.log.debug('Incoming Call Handling..')
        line = notification.pop()
        lineMatch = self.CLIP_REGEX.match(line)
        if lineMatch:
            self.callerID = lineMatch.group(1)
            print(self.callerID)
        threading.Thread(target=self._pollCallStatus).start()

    def _hanlderSMSRecieved(self, smsLine):
        self.log.debug('New SMS Received')
        self.messageList = []
        lineMatch = self.CMTI_REGEX.match(smsLine)
        if lineMatch:
            smsMemory = lineMatch.group(1)
            smsIndex = lineMatch.group(2)
            dataSMS = self.write('AT+CMGR={0}'.format(smsIndex))
            dataMatch = self.CMGR_SMS_REGEX.match(dataSMS[1])
            if dataMatch:
                msgStatus, self.recievedNumberSMS, self.recievedTimeSMS = dataMatch.groups()
                self.recievedTextSMS = '\n'.join(dataSMS[2:-1])
                self.flag_newSMS = True
                print(msgStatus)
                self.messageList.append(self.recievedNumberSMS)
                self.messageList.append(self.recievedTimeSMS)
                self.messageList.append(self.recievedTextSMS.rstrip())
                print(self.recievedNumberSMS)
                print(self.recievedTimeSMS)
                print(self.recievedTextSMS.rstrip())

    def connect(self):
        """ Open the port and connect """
        self.log.info('Connecting to PiTalk on Port %s & baudrate %d', self.port, self.baudrate)
        super(PiTalk, self).connect()

        # Initialize commands
        status = self.write('AT')
        if status is None:
            self.alive = False
            self.log.info('PiTalk Initialization Failed')
        elif status[1] == 'OK\r\n':
            self.alive = True
            self.write('AT+CLIP=1') # Incoming Call line identification
            self.write('AT+CMGF=1')
            self.write('AT+QURCCFG=\"urcport\",\"uart1\"')
            self.write('ATS0=0')
            self.write('AT+CCFC=0,4')
            self.log.info('PiTalk is Initialized')
        
    def imei(self):
        """ @return: IMEEI number """
        return self.write('AT+CGSN')[1]

    def signalStrength(self):
        """ @return: Signal Strength """
        value = self.CSQ_REGEX.match(self.write('AT+CSQ')[1])
        if value:
            return(int(value.group(1)))

    def networkName(self):
        """ @return: Netwrok Name"""
        operator = self.COPS_REGEX.match(self.write('AT+COPS?')[1])
        if operator:
            return operator.group(3)

    def _pollCallStatus(self):
        """ checking status of call """
        while self.outgoingCall or self.incomingCall:
            value = self.CPAS_REGEX.match(self.write('AT+CPAS')[1])
            value = int(value.group(1))
            print(value)
            if value == 0:
                self.callDisconnected = True
                self.outgoingCall = False
                self.incomingCall = False
                self.callConnected = False
            elif value == 4:
                self.callConnected = True
            time.sleep(2)

    def dial(self, number):
        """ Outgoing Call and create thread for call status
        @ param: Dialled number
        """
        self.outgoingCall = True
        self.write('ATD{0};'.format(number))
        threading.Thread(target=self._pollCallStatus).start()

    def hangup(self):
        """ Call Disconnect """
        self.write('ATH')

    def connectCall(self):
        """ Call Connect """
        self.write('ATA')

    def muteCall(self, args):
        """Call Mute"""
        self.write("AT+CMUT="+str(args))

    def jackMode(self):
        """ jack Mode """
        self.write('AT+QAUDPATH=1')
        
    def speakerMode(self):
        """ Speaker Mode """
        self.write('AT+QAUDPATH=0')

    def readADC0(self):
        """Read voltage on ADC0"""
        value = self.QADC_REGEX.match(self.write('AT+QADC=0')[1])
        print(value)
        return value.group(1)
        
    def readADC1(self):
        """Read voltage on ADC1"""
        value = self.QADC_REGEX.match(self.write('AT+QADC=1')[1])
        return value.group(1)

    def autoRing(self, ring_count):
        """Sets the auto ring to the number specified"""
        self.write('ATS0='+str(ring_count))

    def deleteSMS(self):
        """deletes all messages stored in memory"""
        self.write('AT+CMGD=1,4')

    def sendSMS(self, reciever, text):
        self.write('AT+CMGS="{0}"'.format(reciever), timeout=2, expectedResponse='> ')
        result = self.write(text, timeout=15, writeTerm=chr(26))
        print(result)
        return result

    def shutdown(self):
        """shuts down the hardware"""
        self.write("AT+QPOWD")

    def speaker_gain(self, value):
        """Used to select the volume of the internal loudspeaker"""
        self.write("AT+CLVL="+str(value))

    def enableCallForwarding(self,number = 0):
        """ Enable Call forwaring to number """
        if "CME ERROR" in str(self.write("AT+CCFC=0,3,"+'"'+str(number)+'"')):
            return False
        else:
            return True
        
    def disableCallForwarding(self):
        """ Disable Call Forwarding """
        self.write("AT+CCFC=0,4")

    def statusCallForwarding(self):
        """ Querry call forwarding """
        value = self.write("AT+CCFC=0,2")
        if "145" in str(value):
            cfw_number = self.CCFC_REGEX.match(value[3])
            return int(cfw_number.group(3))
        elif "255" in str(value):
            return False
        
    def write(self, data, waitForResponse=True, writeTerm = '\r',timeout=5, expectedResponse=None):
        """ Write Data to pitalk Modem """
        self.log.debug('write: %s', data)
        responseLines = SerialComm.write(self, data + writeTerm, waitForResponse=waitForResponse, timeout=timeout, response=expectedResponse)
        return responseLines
    
    def get_location(self):
        """ read coordinates of module """
        coordinate_list = []
        coordinates = self.QCELLLOC_REGEX.match(self.write('AT+QCELLLOC=1')[1])
        coordinate_list.append(coordinates.group(2)) #lattitude
        coordinate_list.append(coordinates.group(1)) #longitude
        return coordinate_list
        
