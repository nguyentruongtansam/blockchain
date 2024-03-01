import argparse
import bitcoin
from bitcoin.wallet import CBitcoinSecret, P2SHBitcoinAddress, CBitcoinAddress
from bitcoin.core import COIN, lx, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction
from bitcoin.core.script import CScript, OP_2, OP_CHECKMULTISIG, SignatureHash, SIGHASH_ALL
from bitcoin.core.scripteval import VerifyScript, SCRIPT_VERIFY_P2SH
from bitcoinlib.services.services import Service

def main():
    parser = argparse.ArgumentParser(description='Create a P2SH Bitcoin transaction.')
    parser.add_argument('--private_key1', help='First private key for the P2SH address', required=True)
    parser.add_argument('--private_key2', help='Second private key for the P2SH address', required=True)
    parser.add_argument('--txid', help='Transaction ID to spend', required=True)
    parser.add_argument('--output_idx', type=int, help='Output index', required=True)
    parser.add_argument('--sent_amount', type=float, help='Amount of BTC to send', required=True)
    parser.add_argument('--kept_amount', type=float, help='Amount of BTC to keep', required=True)
    parser.add_argument('--destination_address', help='Destination Bitcoin address', required=True)
    args = parser.parse_args()

    bitcoin.SelectParams('testnet')

    private_key1 = CBitcoinSecret(args.private_key1)
    private_key2 = CBitcoinSecret(args.private_key2)
    public_key1 = private_key1.pub
    public_key2 = private_key2.pub
    redeem_script = CScript([OP_2, public_key1, public_key2, OP_2, OP_CHECKMULTISIG])
    p2sh_address = P2SHBitcoinAddress.from_redeemScript(redeem_script)

    txid = lx(args.txid)
    vout = args.output_idx
    txin = CMutableTxIn(COutPoint(txid, vout))

    # Output to the destination address
    txout1 = CMutableTxOut(int(args.sent_amount * COIN), CBitcoinAddress(args.destination_address).to_scriptPubKey())

    # Change output back to the P2SH address
    txout2 = CMutableTxOut(int(args.kept_amount * COIN), p2sh_address.to_scriptPubKey())

    tx = CMutableTransaction([txin], [txout1, txout2])

    # Sign the transaction
    sighash = SignatureHash(redeem_script, tx, 0, SIGHASH_ALL)
    sig1 = private_key1.sign(sighash) + bytes([SIGHASH_ALL])
    sig2 = private_key2.sign(sighash) + bytes([SIGHASH_ALL])

    # The scriptSig should include a dummy element, followed by the signatures and the redeem script
    txin.scriptSig = CScript([b'', sig1, sig2, redeem_script])

    VerifyScript(txin.scriptSig, redeem_script.to_p2sh_scriptPubKey(), tx, 0, (SCRIPT_VERIFY_P2SH,))

    serialized_tx = tx.serialize().hex()
    print(f"Raw transaction: {serialized_tx}")

    service = Service(network='testnet')
    txid = service.sendrawtransaction(serialized_tx)
    print(txid)

if __name__ == "__main__":
    main()
