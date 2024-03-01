import argparse
import bitcoin
from bitcoin.wallet import CBitcoinSecret, CBitcoinAddress, P2PKHBitcoinAddress
from bitcoin.core import COIN, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction, Hash160, lx
from bitcoin.core.script import CScript, OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoinlib.services.services import Service

def main():
    parser = argparse.ArgumentParser(description='Create a Bitcoin transaction.')
    parser.add_argument('--private_key', help='Your private key', required=True)
    parser.add_argument('--txid', help='Transaction ID to spend', required=True)
    parser.add_argument('--output_idx', type=int, help='Output index', required=True)
    parser.add_argument('--sent_amount', type=float, help='Amount of BTC to send', required=True)
    parser.add_argument('--kept_amount', type=float, help='Amount of BTC to keep', required=True)
    parser.add_argument('--destination_address', help='Destination Bitcoin address', required=True)
    args = parser.parse_args()

    bitcoin.SelectParams('testnet')

    private_key = CBitcoinSecret(args.private_key)
    public_key = private_key.pub
    txid = lx(args.txid)
    vout = args.output_idx
    txin = CMutableTxIn(COutPoint(txid, vout))

    param = [OP_DUP, OP_HASH160, Hash160(public_key), OP_EQUALVERIFY, OP_CHECKSIG]
    txin_scriptPubKey = CScript(param)
    
    txout_1 = CMutableTxOut(int(args.sent_amount * COIN), CBitcoinAddress(args.destination_address).to_scriptPubKey())
    address = P2PKHBitcoinAddress.from_pubkey(public_key)
    txout_2 = CMutableTxOut(int(args.kept_amount * COIN), address.to_scriptPubKey())

    tx = CMutableTransaction([txin], [txout_1, txout_2])
    sighash = SignatureHash(txin_scriptPubKey, tx, 0, SIGHASH_ALL)
    sig = private_key.sign(sighash) + bytes([SIGHASH_ALL])
    txin.scriptSig = CScript([sig, public_key])

    VerifyScript(txin.scriptSig, txin_scriptPubKey, tx, 0, (SCRIPT_VERIFY_P2SH,))

    serialized_tx = tx.serialize().hex()
    print(f"Raw transaction: {serialized_tx}")

    service = Service(network='testnet')
    txid = service.sendrawtransaction(serialized_tx)
    print(txid)

if __name__ == "__main__":
    main()
