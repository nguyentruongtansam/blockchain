import argparse
import requests

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', type=str, default='http://localhost', help='Blockchain server address')
    parser.add_argument('--port', type=int, default=8000, help='Blockchain server port')
    parser.add_argument('-m', '--mine', action='store_true', help='Mine a new block')
    parser.add_argument('-v', '--view', action='store_true', help='View the blockchain')
    parser.add_argument('-a', '--add', type=str, help='Add a new transaction in JSON format')
    parser.add_argument('--validate', action='store_true', help='Validate blockchain integrity')
    parser.add_argument('--verify', type=str, help='Verify a transaction in JSON format')
    return parser.parse_args()

def view_chain(server):
    response = requests.get(f'{server}/chain')
    print(response.json())

def add_transaction(server, transaction):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{server}/add_transaction', json=transaction, headers=headers)
    print()
    print(response.json())

def mine_block(server):
    response = requests.post(f'{server}/mine')
    print(response.json())

def validate_chain(server):
    response = requests.get(f'{server}/validate')
    print(response.json())

def verify_transaction(server, transaction):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{server}/verify_transaction', json=transaction, headers=headers)
    print(response.json())

def main():
    args = get_arguments()
    server = f"{args.server}:{args.port}"

    if args.view:
        view_chain(server)

    if args.add:
        try:
            transaction = eval(args.add)
            add_transaction(server, transaction)
        except SyntaxError:
            print("Invalid transaction format. Please provide a valid JSON string.")

    if args.mine:
        mine_block(server)

    if args.validate:
        validate_chain(server)

    if args.verify:
        try:
            transaction = eval(args.verify)
            verify_transaction(server, transaction)
        except SyntaxError:
            print("Invalid transaction format. Please provide a valid JSON string.")


if __name__ == "__main__":
    main()