
from random import random
from urllib import response
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from blockChain import *
from Wallet import *
import json
app = Flask(__name__)
block_chain = BLockChain()
CORS(app)


@app.route("/chain", methods=['GET'])
def get_chain():
    response = {
        'chain': block_chain.chain,
        'pending': len(block_chain.pending),
        'length': len(block_chain.chain),
    }
    return jsonify(response), 200


@app.route("/new_block", methods=['GET'])
def get_new_block():
    new_block = block_chain.present_block()
    if new_block == False:
        response = {'message': 'nothing to mine'}
        return jsonify(response), 201
    else:
        return jsonify(new_block), 200


@app.route("/newtransaction", methods=["POST"])
def post_transaction():
    data = json.loads(request.data)
    fromAdress = data['fromAdress']
    toAdress = data['toAdress']
    amount = data['amount']
    sig = data['sig']
    if not block_chain.submit_transaction(fromAdress, toAdress, amount, sig):
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:
        response = {'message': 'Transaction will be added to Block'}
        return jsonify(response), 200


@app.route("/addnode", methods=["POST"])
def post_node():
    data = json.loads(request.data)
    nodes = data["nodes"].replace(" ", "").split(',')
    if nodes is None:
        return "Error", 400
    for node in nodes:
        block_chain.add_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in block_chain.nodes],
    }
    print(block_chain.nodes)
    return jsonify(response), 200


@app.route("/getnode", methods=['GET'])
def get_nodes():
    nodes = [node for node in block_chain.nodes]
    nodes.append(block_chain.server)
    response = {
        'nodes': nodes
    }
    return jsonify(response), 200


@app.route("/partener/get", methods=["GET"])
def get_partener_list():
    wallet_client_adress = request.args.get('client')
    card_adress_list = block_chain.get_card_list(wallet_client_adress)
    print(card_adress_list)
    response = {
        'client': wallet_client_adress,
        'card_list': card_adress_list
    }
    return jsonify(response), 200


@app.route("/partener/transactions", methods=["GET"])
def get_partener_transactions():
    wallet_client_adress = request.args.get('client')
    wallet_card_adress = request.args.get("card")
    card_Tx_list = block_chain.get_card_transaction(
        wallet_client_adress, wallet_card_adress)
    response = {
        'client': wallet_client_adress,
        'card': wallet_card_adress,
        'tx': card_Tx_list
    }
    return jsonify(response), 200


@app.route("/wallet/new", methods=["GET"])
def new_wallet():
    new_wallet = Wallet()
    response = {
        "pub_key": new_wallet.get_public_key(),
        "priv_key": new_wallet.get_private_key(),
        "wallet_adress": None
    }
    return jsonify(response), 200


@app.route("/balance", methods=["GET"])
def balance():
    wallet_client_adress = request.args.get('client')
    wallet_card_adress = request.args.get("card")
    balance = block_chain.balance(wallet_client_adress, wallet_card_adress)
    response = {
        'client': wallet_client_adress,
        'card': wallet_card_adress,
        'balance': balance

    }
    return jsonify(response), 200


@app.route("/valide", methods=['GET'])
def valide():
    response = {
        'node_valide': block_chain.is_valide()
    }
    return jsonify(response), 200

import random
def searching():
    while True:
        block_chain.get_block_from_network()
        time.sleep(random.randint(0, 20))

def connect_nodes():
    while True:
        block_chain.resolve_nodes()
        time.sleep(5)
if __name__ == '__main__':
    import time
    import threading
    th_resolve_confilct = threading.Thread(target=searching)
    th_resolve_node = threading.Thread(target=connect_nodes)

    th_resolve_confilct.start()
    th_resolve_node.start()

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-host', '--host', default="127.0.0.1",
                        type=str, help='ip to host on')
    parser.add_argument('-p', '--port', default=5000,
                        type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    host = args.host
    block_chain.init_server("{}:{}".format(host, port))
    block_chain.add_node("http://{}:{}".format(host, 5000))
    block_chain.master_server = "{}:{}".format(host, 5000)
    block_chain.signtomaster()
    app.run(host=host, port=port)
