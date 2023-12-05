import logging
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer

from common.address import Address
from controller import Controller

class Server:
    def __init__(self, listen_address: Address):
        self.address = listen_address
        self.controller = Controller.instance()

        self._server = SimpleXMLRPCServer(listen_address.tuple(), allow_none=True, logRequests=False)
        self._server.register_function(self.controller.get_vote, "get_vote")
        self._server.register_function(self.controller.append_entries, "append_entries")
        self._server.register_function(self.controller.set, "set")

    def serve(self):
        Thread(target=self._server.serve_forever).start()
        logging.info(f"Server listening on {self.address}")
