from flask import Flask, request, jsonify
from blockchain import Blockchain
from argparse import ArgumentParser

app = Flask(__name__)

blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [{"index": block.index,
                   "transactions": block.transactions,
                   "timestamp": block.timestamp,
                   "previous_hash": block.previous_hash,
                   "nonce": block.nonce,
                   "hash": block.hash}
                   for block in blockchain.chain]
    return jsonify(chain_data), 200

@app.route('/mine', methods=['POST'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if result:
        return jsonify({"message": "Block #{} is mined.".format(result)}), 200
    else:
        return jsonify({"message": "No transactions to mine."}), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    transaction_data = request.json
    blockchain.unconfirmed_transactions.append(transaction_data)
    return jsonify({"message": "Transaction added to the unconfirmed transactions list."}), 201

@app.route('/validate', methods=['GET'])
def validate_chain():
    is_valid = blockchain.is_chain_valid()
    if is_valid:
        response = {"message": "The blockchain is valid."}
    else:
        response = {"message": "The blockchain is not valid."}
    return jsonify(response), 200

@app.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    transaction_data = request.json
    is_verified = blockchain.verify_transaction(transaction_data)
    if is_verified:
        response = {"message": "Transaction is verified."}
    else:
        response = {"message": "Transaction not found or invalid."}
    return jsonify(response), 200

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='Port to run the Flask server on')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)