from nose.tools import raises
from crank.dispatcher import *

class TestDispatcher:

    def setup(self):
        self.dispatcher = Dispatcher()

    def test_create(self):
        pass

    @raises(NotImplementedError)
    def test_dispatch(self):
        self.dispatcher._dispatch(1,2)

