from uuid import uuid4
import time
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import binascii

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
        try:
            transactionHash = SHA256.new(self.data_core())
            pkcs1_15.new(RSA.import_key(binascii.unhexlify(self.fromAdress))).verify(
                transactionHash, binascii.unhexlify(self.sig))
            return True
        except (ValueError, TypeError) as e:
            return False
