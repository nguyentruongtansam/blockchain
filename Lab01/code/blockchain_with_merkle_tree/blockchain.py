import hashlib
import time
from typing import List
import hashlib

class Node:
    def __init__(self, left, right, value: str, content, is_copied=False, parent=None) -> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.content = content
        self.is_copied = is_copied
        self.parent = parent

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()

    def __str__(self):
        return (str(self.value))

    def copy(self):
        """
        class copy function
        """
        return Node(self.left, self.right, self.value, self.content, True)

class MerkleTree:
    def __init__(self, values: List[str]) -> None:
        self.__buildTree(values)

    def __buildTree(self, values: List[str]) -> None:

        leaves: List[Node] = [Node(None, None, Node.hash(e), e) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1].copy())  # duplicate last elem if odd number of elements
        self.root: Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes: List[Node]) -> Node:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1].copy())  # duplicate last elem if odd number of elements
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            return Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value), nodes[0].content+"+"+nodes[1].content)

        left: Node = self.__buildTreeRec(nodes[:half])
        right: Node = self.__buildTreeRec(nodes[half:])
        value: str = Node.hash(left.value + right.value)
        content: str = f'{left.content}+{right.content}'
        parent_node = Node(left, right, value, content)
        left.parent = parent_node
        right.parent = parent_node
        return parent_node

    def getRootHash(self) -> str:
      return self.root.value

    def verify_transaction(self, transaction_str: str) -> bool:
        # Find the node containing the transaction
        nodes = [node for node in self._get_leaves() if node.content == transaction_str]

        # Transaction not found in the leaves
        if not nodes:
            return False

        # Start with the found leaf node
        node = nodes[0]

        # Reconstruct the path up to the root
        while node.parent is not None:  # Check if the node is not the root
            parent = node.parent
            # Check which side the node is on and compute hash accordingly
            if node is parent.left:
                sibling = parent.right
                computed_hash = Node.hash(node.value + sibling.value)
            else:
                sibling = parent.left
                computed_hash = Node.hash(sibling.value + node.value)

            # If the computed hash at any point doesn't match the parent's value, return False
            if computed_hash != parent.value:
                return False

            node = parent

        # If the path was reconstructed up to the root successfully, return True
        return True

    def _get_leaves(self):
        leaves = []
        self._get_leaves_rec(self.root, leaves)
        return leaves

    def _get_leaves_rec(self, node, leaves):
        if node is not None:
            if node.left is None and node.right is None:  # It's a leaf
                leaves.append(node)
            else:
                self._get_leaves_rec(node.left, leaves)
                self._get_leaves_rec(node.right, leaves)

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0, merkle_root=''):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.merkle_root = merkle_root

    def compute_hash(self):
        block_string = f"{self.index}{self.merkle_root}{self.timestamp}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    difficulty = 5

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.chain[-1].hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        #block.merkle_root = self.get_merkle_root(block.transactions)
        block.hash = block.compute_hash()
        self.chain.append(block)
        return True

    def get_merkle_root(self, transactions):
        transaction_strings = [str(tx) for tx in transactions]
        merkle_tree = MerkleTree(transaction_strings)
        return merkle_tree.getRootHash()

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.chain[-1]
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        new_block.merkle_root = self.get_merkle_root(self.unconfirmed_transactions)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return new_block.index

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check hash integrity
            if current_block.hash != current_block.compute_hash():
                return False

            # Check continuity of the chain
            if current_block.previous_hash != previous_block.hash:
                return False

            # Validate Merkle Root
            if not self.validate_merkle_root(current_block):
                return False

        return True

    def validate_merkle_root(self, block):
        # Construct Merkle Tree from transactions in the block
        merkle_tree = MerkleTree([str(tx) for tx in block.transactions])

        # Check if the computed Merkle root matches the Merkle root in the block
        return merkle_tree.getRootHash() == block.merkle_root

    def verify_transaction(self, transaction):
        for block in self.chain:
            if transaction in block.transactions:
                # Construct Merkle Tree and check if the transaction is part of it
                merkle_tree = MerkleTree([str(tx) for tx in block.transactions])
                return merkle_tree.verify_transaction(str(transaction))
        return False