from uuid import uuid4
import time
from collections import OrderedDict


class Transaction:
    def __init__(self, fromAdress="", toAdress="", amount=0.0, sig=""):
        self.index = str(uuid4()).replace("-", "")
        self.fromAdress = fromAdress
        self.toAdress = toAdress
        self.amount = amount
        self.timestamp = time.time()
        self.sig = sig

    def data_core(self) -> bytes:
        return (str(self.index) + str(self.fromAdress) + str(self.toAdress) + str(self.amount) + str(self.timestamp)).encode()

    def __str__(self) -> str:
        return str(self.__dict__)

    def toJson(self) -> dict:
        return self.__dict__
    
    def verfiy(self):
        return True
