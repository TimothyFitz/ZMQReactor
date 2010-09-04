from twisted.trial import unittest
from twisted.internet import reactor, defer
import zmq

"""
TODO: 

Test coverage around different types of port?
"""

class EchoProtocol(object):
    def messageReceived(self, message):
        print "RECV", message
        self.transport.sendMessage("ECHO:" + message)
        
class RecorderProtocol(object):
    def __init__(self):
        self.messages = []
        self.next = defer.Deferred()
        
    def messageReceived(self, message):
        print "Mr"
        self.messages.append(message)
        last = self.next
        self.next = defer.Deferred()
        last.callback(message)

class TestZeroMQ(unittest.TestCase):

    def test_req_rep_roundtrip(self):
        echo = reactor.bindZeroMQ("tcp://127.0.0.1:9999", zmq.REP, EchoProtocol)
        recorder = reactor.connectZeroMQ("tcp://127.0.0.1:9999", zmq.REQ, RecorderProtocol)
        recorder.transport.sendMessage("DONE")
        
        def assertOnMessages(messages):
            self.assertEquals("ECHO:DONE", messages)
            recorder.transport.loseConnection()
            echo.transport.loseConnection()
        
        recorder.next.addCallback(assertOnMessages)
        return recorder.next