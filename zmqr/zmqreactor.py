from zmqr.pollreactor import PollReactor

from zmq import Poller, ZMQError
import zmq

class Constants(object):
    POLLIN = zmq.POLLIN
    POLLOUT = zmq.POLLOUT
    POLLERR = zmq.POLLERR
    POLLHUP = 0
    POLLNVAL = 0

class ZeroMQReactor(PollReactor):
    pollerFactory = Poller
    constants = Constants
    
    def __init__(self):
        PollReactor.__init__(self)
        self.zmqContext = zmq.Context()
    
    def bindZeroMQ(self, endpoint, type, factory):
        # TODO: "bind_to_random_port" support, especially needed for tests.
        return self._createTransport(zmq.Socket.bind, endpoint, type, factory)
        
    def connectZeroMQ(self, endpoint, type, factory):
        return self._createTransport(zmq.Socket.connect, endpoint, type, factory)
        
    def _createTransport(self, method, endpoint, type, factory):
        socket = zmq.Socket(self.zmqContext, type)
        method(socket, endpoint)
        protocol = factory()
        transport = ZeroMQTransport(self, socket, protocol)
        return protocol

class ZeroMQTransport(object):    
    def __init__(self, reactor, socket, protocol):
        self.reactor = reactor
        self.socket = socket
        self.outboundQueue = []
        self.protocol = protocol
        protocol.transport = self
        self.logstr = protocol.__class__.__name__
        self.reactor.addReader(self)
        
    def fileno(self):
        return self.socket
        
    def doRead(self):
        """Calls self.protocol.dataReceived with all available data.

        This reads up to self.bufferSize bytes of data from its socket, then
        calls self.dataReceived(data) to process it.  If the connection is not
        lost through an error in the physical recv(), this function will return
        the result of the dataReceived call.
        """
        message = self.socket.recv(flags=zmq.NOBLOCK, copy=True)
        if message is None:
            return
        return self.protocol.messageReceived(message)
        
    def sendMessage(self, message):
        #if self.outboundQueue:
        #    self.queueMessage(message)
        #else:
        try:
            self.socket.send(message, flags=zmq.NOBLOCK, copy=True)
        except ZMQError, z:
            # EAGAIN?
            print z, z.args
            raise
            #self.queueMessage(message)

    def queueMessage(self, message):
        self.outboundQueue.append(message)
        self.reactor.addWriter(self)
        
    def logPrefix(self):
        return self.logstr
        
    def loseConnection(self):
        self.reactor.removeWriter(self)
        self.reactor.removeReader(self)

def install():
    """Install the poll() reactor."""
    zmqr = ZeroMQReactor()
    from twisted.internet.main import installReactor
    installReactor(zmqr)

__all__ = ['ZmqReactor', 'install']