0.1 ALPHA
=========

Description
-----------

Twisted Reactor using zmq_poll. This is sub-optimal, and once 0MQ 2.0.9 lands I'll switch to ZMQ_FD/ZMQ_EVENTS (use existing poll/epoll/kqueue reactor with ZMQ's filedescriptiors, instead of zmq_poll).

Known Bugs
----------

* Does NOT pass all twisted tests on OS X. From what I can tell, this is reflecting the underlying bugs in OS X's poll(2) implementation.