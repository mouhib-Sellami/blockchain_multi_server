from urllib.parse import urlparse
import requests
from Block import *
from Transation import Transaction
import json


class BLockChain:
    diff = 4

    def __init__(self):
        self.server = ""
        self.master_server = ""
        self.chain = []
        self.pending = []
        self.nodes = set()

    def init_server(self, server):
        self.server = server

    def add_node(self, node_url):
        parsed_url = urlparse(node_url)
        if parsed_url.netloc and not self.server == parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
            return True
        elif parsed_url.path and not self.server == parsed_url.path:
            self.nodes.add(parsed_url.path)
            return True
        else:
            return False

    def signtomaster(self):
        try:
            if self.server != self.master_server:
                req = {
                    "nodes": "http://{}".format(self.server)
                }
                sign_up = requests.post(
                    "http://{}/addnode".format(self.master_server), data=json.dumps(req))
                if sign_up.status_code == 200:
                    print("sign to master")
        except:
            pass

    def exsiste(self, node):
        for item in self.nodes:
            if node == item:
                return False
        return True

    def resolve_nodes(self):

        print("resolving nodes")
        j = 0
        my_node = list(self.nodes)
        while j < len(my_node):
            node = my_node[j]
            try:
                res = requests.get("http://"+node+"/getnode")
                if res.status_code == 200:
                    nodes = res.json()["nodes"]
                    nodes = list(nodes)
                    nodes.remove(self.server)
                    nodes = set(nodes)
                    # self.nodes = nodes
                    for new_node in nodes:
                        if new_node not in self.nodes:
                            print(new_node)
                            self.nodes.add(new_node)
                    req = {
                        "nodes": "http://{}".format(self.server)
                    }

            except Exception:
                pass
            j += 1
        try:
            sign_up = requests.post(
                "http://{}/addnode".format(self.master_server), data=json.dumps(req))
            if sign_up.status_code == 200:
                print("master recovery {}".format(self.master_server))
        except Exception:
            pass

    def submit_transaction(self, fromArdess, toAdress, amount, sig):
        new_transaction = Transaction(fromAdress=fromArdess, toAdress=toAdress,
                                      amount=amount, sig=sig)
        if True:  # changed later
            self.pending.append(new_transaction.toJson())
            return True
        else:
            return False

    def add_block(self, block):
        print("adding_block")
        if self.is_valide():
            self.chain.append(block.toJson())

    def present_block(self):
        if self.pending == []:
            return False
        else:
            new_block = Block(self.pending)
            self.pending = []
            return new_block.toJson()

    def resolve_confilcts(self):
        max_len = len(self.chain)
        new_chain = None
        nodes = list(self.nodes)
        i = 0
        while i < len(nodes):
            node = nodes[i]
            try:
                print("http://"+node+"/chain")
                res = requests.get("http://"+node+"/chain")
                if res.status_code == 200:
                    chain = res.json()["chain"]
                    if len(chain) > max_len:
                        if self.valide(chain):
                            max_len = len(chain)
                            new_chain = chain
            except Exception as e:
                print("removing node ")
                self.nodes.remove(node)
                pass
            finally:
                i += 1

        if new_chain:
            self.chain = new_chain
            print("resolved")
            return True
        else:
            print("not resolved")
            return False

    def hash(self, block):
        header = (str(block['index']) + str(block['transaction']) + str(
            block['prevHash']) + str(block['nonce']) + str(block['timestamp'])).encode()
        return hashlib.sha256(header).hexdigest()

    def is_valide(self):
        for i in range(1, len(self.chain)):
            if self.chain[i]['prevHash'] != self.hash(self.chain[i-1]) or self.chain[i-1]['hash'][:self.diff] != "0"*self.diff:
                return False
        return True

    def valide(self, chain):
        for i in range(1, len(chain)):
            if chain[i]['prevHash'] != self.hash(chain[i-1]) or chain[i-1]['hash'][:self.diff] != "0"*self.diff:
                return False
        return True

    def mine(self, block):
        print("Mining ...")
        try:
            block.prevHash = self.chain[-1]['hash']
        except IndexError:
            print("exception")

        try:
            while True:
                if block.get_hash()[:self.diff] == "0"*self.diff:
                    block.hash = block.get_hash()
                    self.add_block(block)
                    break
                else:
                    block.nonce += 1

        except Exception as e:
            print(e)

    def get_block_from_network(self):
        new_block = None
        print("try to get new block to mine...")
        self.resolve_confilcts()
        for node in self.nodes:
            try:
                res = requests.get("http://"+node+"/new_block")
                if res.status_code == 200:
                    data = res.json()
                    new_block = Block(data['transaction'])
                    new_block.index = data['index']
                    new_block.prevHash = data['prevHash']
                    new_block.timestamp = data['timestamp']
                    new_block.hash = data['hash']
                    new_block.nonce = int(data['nonce'])
                    self.mine(new_block)
            except Exception:
                pass

    def balance(self, clientAdress, cardAdress):
        self.resolve_confilcts()
        balance = 0.0
        for block in self.chain:
            for tx in block['transaction']:
                if tx['fromAdress'] == clientAdress and tx['toAdress'] == cardAdress:
                    balance -= tx['amount']
                elif tx['toAdress'] == clientAdress and tx['fromAdress'] == cardAdress:
                    balance += tx['amount']
        return balance

    def get_card_transaction(self, clientAdress, cardAdress):
        self.resolve_confilcts()
        cardTx = []
        for block in self.chain:
            for tx in block['transaction']:
                if tx['fromAdress'] == clientAdress and tx['toAdress'] == cardAdress:
                    cardTx.append(tx)
                elif tx['toAdress'] == clientAdress and tx['fromAdress'] == cardAdress:
                    cardTx.append(tx)
        return cardTx

    def get_card_list(self, clientAdress):
        card_list = set()
        for block in self.chain:
            for tx in block['transaction']:
                if tx['toAdress'] == clientAdress:
                    card_list.add(tx['fromAdress'])
        return list(card_list)
