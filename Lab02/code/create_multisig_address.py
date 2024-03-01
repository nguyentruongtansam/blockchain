import os
from bitcoin import *
from bitcoin.wallet import CBitcoinSecret, P2SHBitcoinAddress
from bitcoin.core.script import CScript, OP_2, OP_CHECKMULTISIG

bitcoin.SelectParams('testnet')

# Generate two random private keys
private_key1 = CBitcoinSecret.from_secret_bytes(os.urandom(32))
private_key2 = CBitcoinSecret.from_secret_bytes(os.urandom(32))

# Derive the public keys
public_key1 = private_key1.pub
public_key2 = private_key2.pub

# Create a 2-of-2 multisig redeem script
redeem_script = CScript([OP_2, public_key1, public_key2, OP_2, OP_CHECKMULTISIG])

# Create a P2SH address from the redeem script
address = P2SHBitcoinAddress.from_redeemScript(redeem_script)
print("Private Key 1:", private_key1)
print("Private Key 2:", private_key2)
print("Redeem Script:", redeem_script.hex())
print("Multisig Address:", address)