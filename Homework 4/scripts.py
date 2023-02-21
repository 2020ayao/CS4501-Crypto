#!/usr/bin/python3

# This is the homework submission file for the BTC Scripting homework, which
# can be found at http://aaronbloomfield.github.io/ccc/hws/btcscript.  That
# page describes how to fill in this program.


from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin import SelectParams
from bitcoin.core import CMutableTransaction
from bitcoin.core.script import *
from bitcoin.core import x


#------------------------------------------------------------
# Do not touch: change nothing in this section!

# ensure we are using the bitcoin testnet and not the real bitcoin network
SelectParams('testnet')

# The address that we will pay our tBTC to -- do not change this!
tbtc_return_address = CBitcoinAddress('mv4rnyY3Su5gjcDNzbMLKBQkBicCtHUtFB') # https://coinfaucet.eu/en/btc-testnet/

# The address that we will pay our BCY to -- do not change this!
bcy_dest_address = CBitcoinAddress('mgBT4ViPjTTcbnLn9SFKBRfGtBGsmaqsZz')

# Yes, we want to broadcast transactions
broadcast_transactions = True

# Ensure we don't call this directly
if __name__ == '__main__':
    print("This script is not meant to be called directly -- call bitcoinctl.py instead")
    exit()


#------------------------------------------------------------
# Setup: your information

# Your UVA userid
userid = 'aly3ye'

# Enter the BTC private key and invoice address from the setup 'Testnet Setup'
# section of the assignment.  
my_private_key_str = "cPa4NtNoigcafoVtxar2tmvF1FJhznYqXYp4rzUWWuPVHrnpGr1K"
my_invoice_address_str = "mzajXQKtMBBj44XRoZSmGZnEM8zKe3ZdnG"

# Enter the transaction ids (TXID) from the funding part of the 'Testnet
# Setup' section of the assignment.  Each of these was provided from a faucet
# call.  And obviously replace the empty string in the list with the first
# one you obtain..
txid_funding_list = ["762a0ab786e5ed6521d0a8a2fe092db2f5ec33dcabb5fe04cf879a014ae423c3"]

# These conversions are so that you can use them more easily in the functions
# below -- don't change these two lines.
if my_private_key_str != "":
    my_private_key = CBitcoinSecret(my_private_key_str)
    my_public_key = my_private_key.pub


#------------------------------------------------------------
# Utility function(s)

# This function will create a signature of a given transaction.  The
# transaction itself is passed in via the first three parameters, and the key
# to sign it with is the last parameter.  The parameters are:
# - txin: the transaction input of the transaction being signed; type: CMutableTxIn
# - txout: the transaction output of the transaction being signed; type: CMutableTxOut
# - txin_scriptPubKey: the pubKey script of the transaction being signed; type: list
# - private_key: the private key to sign the transaction; type: CBitcoinSecret
def create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, private_key):
    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    return private_key.sign(sighash) + bytes([SIGHASH_ALL])


#------------------------------------------------------------
# Testnet Setup: splitting coins

# The transaction ID that is to be split -- the assumption is that it is the
# transaction hash, above, that funded your account with tBTC.  You may have
# to split multiple UTXOs, so if you are splitting a different faucet
# transaction, then change this appropriately. It must have been paid to the
# address that corresponds to the private key above
txid_split = txid_funding_list[0]

# After all the splits, you should have around 10 (or more) UTXOs, all for the
# amount specified in this variable. That amount should not be less than
# 0.0001 BTC, and can be greater.  It will make your life easier if each
# amount is a negative power of 10, but that's not required.
# split_amount_to_split = 0.01077763
split_amount_to_split = 0.001

# How much BTC is in that UTXO; look this up on https://live.blockcypher.com
# to get the correct amount.
# split_amount_after_split = 0.001
split_amount_after_split = 0.00001

# How many UTXO indices to split it into -- you should not have to change
# this!  Note that it will actually split into one less, and use the last one
# as the transaction fee.
split_into_n = int(split_amount_to_split/split_amount_after_split)

# The transaction IDs obtained after successfully splitting the tBTC.
# txid_split_list = ["cb5b9a7460b95771120b1ac347755aed7de5c8084319e14958bb18fb6d21fbbe"]
txid_split_list = ["5a6e69ed40592a13ad4effbf8cc7644ff0dc8691697c88809c20e54a78093278"]

#------------------------------------------------------------
# Global settings: some of these will need to be changed for EACH RUN

# The transaction ID that is being redeemed for the various parts herein --
# this should be the result of the split transaction, above; thus, the
# default is probably sufficient.
txid_utxo = txid_split_list[0]

# This is likely not needed.  The bitcoinctl.py will take a second
# command-line parmaeter, which will override this value.  You should use the
# second command-line parameter rather than this variable. The index of the
# UTXO that is being spent -- note that these indices are indexed from 0.
# Note that you will have to change this for EACH run, as once a UTXO index
# is spent, it can't be spent again.  If there is only one index, then this
# should be set to 0.
utxo_index = -1

# How much tBTC to send -- this should be LESS THAN the amount in that
# particular UTXO index -- if it's not less than the amount in the UTXO, then
# there is no miner fee, and it will not be mined into a block.  Setting it
# to 90% of the value of the UTXO index is reasonable.  Note that the amount
# in a UTXO index is split_amount_to_split / split_into_n.
send_amount = split_amount_after_split * 0.9


#------------------------------------------------------------
# Part 1: P2PKH transaction

# This defines the pubkey script (aka output script) for the transaction you
# are creating.  This should be a standard P2PKH script.  The parameter is:
# - address: the address this transaction is being paid to; type:
#   P2PKHBitcoinAddress
def P2PKH_scriptPubKey(address):
    return [ 
            OP_DUP,
            OP_HASH160,
            address, 
            OP_EQUALVERIFY,
            OP_CHECKSIG
           ]

# This function provides the sigscript (aka input script) for the transaction
# that is being redeemed.  This is for a standard P2PKH script.  The
# parameters are:
# - txin: the transaction input of the UTXO being redeemed; type:
#   CMutableTxIn
# - txout: the transaction output of the UTXO being redeemed; type:
#   CMutableTxOut
# - txin_scriptPubKey: the pubKey script (aka output script) of the UTXO being
#   redeemed; type: list
# - private_key: the private key of the redeemer of the UTXO; type:
#   CBitcoinSecret
def P2PKH_scriptSig(txin, txout, txin_scriptPubKey, private_key):
    # print("txin: ", txin)
    # print("txout: " txout)
    # print("txin_scriptPubKey: ", txin_scriptPubKey)
    # print("private_key: ", private_key)

    tx = CMutableTransaction([txin], [txout])
    sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    sig = private_key.sign(sighash) + bytes([SIGHASH_ALL])

    priv_key = CBitcoinSecret(str(private_key))
    public_key = priv_key.pub


    return [ 
             sig, 
             public_key
           ]

# The transaction hash received after the successful execution of this part
txid_p2pkh = "b48f39b664edd51ca6c0e0a25d7e670a036cb595c2fea26259effaf01ae05bb9"


#------------------------------------------------------------
# Part 2: puzzle transaction

# These two values are constants that you should choose -- they should be four
# digits long.  They need to allow for only integer solutions to the linear
# equations specified in the assignment.
puzzle_txn_p = 4231
puzzle_txn_q = 6953

# These are the solutions to the linear equations specified in the homework
# assignment.  You can use an online linear equation solver to find the
# solutions.
puzzle_txn_x = 1509
puzzle_txn_y = 2722

# This function provides the pubKey script (aka output script) that requres a
# solution to the above equations to redeem this UTXO.
def puzzle_scriptPubKey():
    return [ 
                OP_2DUP,
                OP_ADD,
                puzzle_txn_p,
                OP_EQUALVERIFY,
                OP_DUP,
                OP_ADD,
                OP_ADD,
                puzzle_txn_q,
                OP_EQUAL
           ]

# This function provides the sigscript (aka input script) for the transaction
# that you are redeeming.  It should only provide the two values x and y, but
# in the order of your choice.
def puzzle_scriptSig():
    return [ 
             puzzle_txn_x,
             puzzle_txn_y
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 2a)
txid_puzzle_txn1 = "023f328c41bb423f60a0347812cb8eae599e31f1d0af5a6d7f4860537589c22e"

# The transaction hash received after successfully submitting the second
# transaction above (part 2b)
txid_puzzle_txn2 = "dbea7aa0e4f49e72e2c646e194a62c767582911438e7932e29323ae823ba0784"


#------------------------------------------------------------
# Part 3: Multi-signature transaction

# These are the public and private keys that need to be created for alice,
# bob, and charlie
alice_private_key_str = "cT9KD8WJGmRqpFQ2mhvv7ZjeWXp4D3YNx4bEohFXmxeepL63WP9V"
alice_invoice_address_str = "n4cDyydKfbziiZTV7g8twRGQSULdGRumob"
bob_private_key_str = "cNrFbrk7RuSYAwFCaXDL5KmJdTLCMv2GkKUqFCj87qmeroXK1Vx9"
bob_invoice_address_str = "msb7kQUgCuQVuvy5FUSj5kBMTibjLwnQ9a"
charlie_private_key_str = "cVPMnRzZ3pHMqhAazgY4ZBYbSS3qBLYCFTD5Fhu5gxXem43pTekZ"
charlie_invoice_address_str = "n4cjVnnEmKekTLJimQhVLhat1vgLGZMqFC"

# These three lines convert the above strings into the type that is usable in
# a script -- you should NOT modify these lines.
if alice_private_key_str != "":
    alice_private_key = CBitcoinSecret(alice_private_key_str)
if bob_private_key_str != "":
    bob_private_key = CBitcoinSecret(bob_private_key_str)
if charlie_private_key_str != "":
    charlie_private_key = CBitcoinSecret(charlie_private_key_str)

# This function provides the pubKey script (aka output script) that will
# require multiple different keys to allow redeeming this UTXO.  It MUST use
# the OP_CHECKMULTISIGVERIFY opcode.  While there are no parameters to the
# function, you should use the keys above for alice, bob, and charlie, as
# well as your own key.
def multisig_scriptPubKey():
    return [
            # OP_DUP,
            # OP_HASH160,
            # my_invoice_address_bcy_str, 
            # OP_EQUALVERIFY,
            # OP_CHECKSIGVERIFY,
            my_private_key.pub,
            OP_CHECKSIGVERIFY,
            alice_private_key.pub,
            bob_private_key.pub,
            charlie_private_key.pub,
            OP_3,
            OP_CHECKMULTISIGVERIFY,
            OP_1            
           ]

# This function provides the sigScript (aka input script) that can redeem the
# above transaction.  The parameters are the same as for P2PKH_scriptSig
# (), above.  You also will need to use the keys for alice, bob, and charlie,
# as well as your own key.  The private key parameter used is the global
# my_private_key.
def multisig_scriptSig(txin, txout, txin_scriptPubKey):
    bank_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, my_private_key)
    alice_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, alice_private_key)
    bob_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, bob_private_key)
    charlie_sig = create_CHECKSIG_signature(txin, txout, txin_scriptPubKey, charlie_private_key)
    


    # tx = CMutableTransaction([txin], [txout])
    # sighash = SignatureHash(CScript(txin_scriptPubKey), tx, 0, SIGHASH_ALL)
    # sig = my_private_key.sign(sighash) + bytes([SIGHASH_ALL])
    return [ 
            OP_0, 
            alice_sig, 
            bob_sig,
            OP_2, 
            bank_sig
           ]

# The transaction hash received after successfully submitting the first
# transaction above (part 3a)
txid_multisig_txn1 = "26ee1fbf4b71ceedf5b0556e7b6b4d002bec80e95d42c9c1d428c3ecfec5c90f"

# The transaction hash received after successfully submitting the second
# transaction above (part 3b)
txid_multisig_txn2 = "86531e0bfeb4891f5b289811e3e75301534fd425f1a61ac694026ea941d8dad6"


#------------------------------------------------------------
# Part 4: cross-chain transaction

# This is the API token obtained after creating an account on
# https://accounts.blockcypher.com/.  This is optional!  But you may want to
# keep it here so that everything is all in once place.
blockcypher_api_token = "7bd7459f6b17467e8c957bd7d4ffff82"

# These are the private keys and invoice addresses obtained on the BCY test
# network.
my_private_key_bcy_str = "427700c38876c5884bf278656511e8854e2be129ccf1df5d5517190fe0f6a675"
my_public_key_bcy_str = "02360119a74be891172ddba150a3d25d04746db12caacb49e83788084a25bb3c91"
my_invoice_address_bcy_str = "CDhgFrtP1hzWuRastYPLfwYC4Rc3Y8XRfd"
my_wif_bcy_str = "BqZEHCMcEQKzkyTbjYFcwtSFiUfoDAvKrbr3ZDpGb9Fo6avLbNVH"

bob_private_key_bcy_str = "63662e2c4854db62d0181f01f96b75fb6f14ddf6314df6fb980bc65a8ac4b45d"
bob_public_key_bcy_str = "02c48110e2a24602897314a7dc58363591c2387bd0e54abfa11d3128cd4c1bac01"
bob_invoice_address_bcy_str = "CAovP4qeJh46r4CXUvWb7spqrxjvA5zBbq"
bob_wif_bcy_str = "BrfFSJkjyDb2JzviZNDZZUziDocSxAi1nmxewE7kJRditB3RZtEq"

# This is the transaction hash for the funding transaction for Bob's BCY
# network wallet.
txid_bob_bcy_funding = "e0068a7f630e71b6352302bac8e7bb414d933ff76109c0410a153bfe01d96984"

# This is the transaction hash for the split transaction for the trasnaction
# above.
txid_bob_bcy_split = "5a6e69ed40592a13ad4effbf8cc7644ff0dc8691697c88809c20e54a78093278"

# This is the secret used in this atomic swap.  It needs to be between 1 million
# and 2 billion.
atomic_swap_secret = 1566038372

# This function provides the pubKey script (aka output script) that will set
# up the atomic swap.  This function is run by both Alice (aka you) and Bob,
# but on different networks (tBTC for you/Alice, and BCY for Bob).  This is
# used to create TXNs 1 and 3, which are described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.
def atomicswap_scriptPubKey(public_key_sender, public_key_recipient, hash_of_secret):
    return [ 
            OP_IF,
            OP_HASH160,
            hash_of_secret,
            OP_EQUALVERIFY,
            public_key_recipient,
            OP_CHECKSIG,

            OP_ELSE,
            public_key_sender,
            OP_CHECKSIGVERIFY,
            public_key_recipient,
            OP_CHECKSIG,
            OP_ENDIF
           ]

# This is the ScriptSig that the receiver will use to redeem coins.  It's
# provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This creates the "normal" redeeming script, shown in steps 5 and 6 at 
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/atomicsteps.
def atomcswap_scriptSig_redeem(sig_recipient, secret):
    return [
        sig_recipient, secret, OP_TRUE,
    ]

# This is the ScriptSig for sending coins back to the sender if unredeemed; it
# is provided in full so that you can write the atomicswap_scriptPubKey()
# function, above.  This is used to create TXNs 2 and 4, which are
# described at
# http://aaronbloomfield.github.io/ccc/slides/bitcoin.html#/xchainpt1.  In
# practice, this would be time-locked in the future -- it would include a
# timestamp and call OP_CHECKLOCKTIMEVERIFY.  Because the time can not be
# known when the assignment is written, and as it will vary for each student,
# that part is omitted.
def atomcswap_scriptSig_refund(sig_sender, sig_recipient):
    return [
        sig_recipient, sig_sender, OP_FALSE,
    ]

# The transaction hash received after successfully submitting part 4a
txid_atomicswap_alice_send_tbtc = "6eaaa3a0d303e35311345cbf026d2f82b85d2f43bb75837e5bae5c83e64fa39a"

# The transaction hash received after successfully submitting part 4b
txid_atomicswap_bob_send_bcy = "fc723cfe95df8b530ae73acc2ddd066a475c1d96d9d969f3a6fea9f21dc6e3c3"

# The transaction hash received after successfully submitting part 4c
txid_atomicswap_alice_redeem_bcy = "9e5db35132c69887a20ef8c6e2ded884f6d9054629406ccb0d0ed7d5fccd8fbc"

# The transaction hash received after successfully submitting part 4d
txid_atomicswap_bob_redeem_tbtc = "c2881b6f50f7a866cc77f24bb64857745d1561137b576b9f2ca2eb4f6cb3e710"


#------------------------------------------------------------
# part 5: return everything to the faucet

# nothing to fill in here, as we are going to look at the balance of
# `my_invoice_address_str` to verify that you've completed this part.
