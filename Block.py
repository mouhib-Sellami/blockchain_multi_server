from uuid import uuid4
import time
import hashlib
from collections import OrderedDict


class Block:
    def __init__(self, transaction=[], prevHash="0"*64):
        self.index = str(uuid4()).replace("-", "")
        self.transaction = transaction
        self.prevHash = prevHash
        self.nonce = 0
        self.timestamp = time.time()
        self.hash = self.get_hash()

    def get_hash(self) -> str:
        return hashlib.sha256(self.get_header()).hexdigest()

    def get_header(self) -> bytes:
        return (str(self.index) + str(self.transaction) + str(self.prevHash) + str(self.nonce) + str(self.timestamp)).encode()

    def __str__(self) -> str:
        return str(self.__dict__)

    def toJson(self) -> dict:
        return self.__dict__
