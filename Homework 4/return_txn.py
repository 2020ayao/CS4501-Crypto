#!/usr/bin/env python
import sys
import bitcoinctl

a, b = input("How many transactions are unspent in your tbtc wallet? a, b -> a = which index, b = how many left: ").split(",")
a = int(a)
b = int(b)
for i in range(a, a+b): # 5, 4

    bitcoinctl.utxo = i
    bitcoinctl.handle_txn("part1")
