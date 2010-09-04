from twisted.application.reactors import Reactor

zmqr = Reactor(
    'zmq', 'zmqr.zmqreactor',
    'ZeroMQReactor')
