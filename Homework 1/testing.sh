#!/bin/bash

echo The name of this cryptocurrency is:
./cryptomoney.sh name
echo Creation of the genesis block
./cryptomoney.sh genesis
echo Creating a wallet for alice into alice.wallet.txt
./cryptomoney.sh generate alice.wallet.txt
export alice=`./cryptomoney.sh address alice.wallet.txt`
echo alice.wallet.txt wallet signature: $alice
echo funding alice wallet with 1000
./cryptomoney.sh fund $alice 1000 01-alice-funding.txt

echo Creating a wallet for bob into bob.wallet.txt
./cryptomoney.sh generate bob.wallet.txt
export bob=`./cryptomoney.sh address bob.wallet.txt`
echo bob.wallet.txt wallet signature: $bob
echo funding bob wallet with 1000
./cryptomoney.sh fund $bob 1000 02-bob-funding.txt

echo Creating a wallet for charlie into charlie.wallet.txt
./cryptomoney.sh generate charlie.wallet.txt
export charlie=`./cryptomoney.sh address charlie.wallet.txt`
echo charlie.wallet.txt wallet signature: $charlie
echo funding charlie wallet with 1000
./cryptomoney.sh fund $charlie 1000 03-charlie-funding.txt

echo Creating a wallet for dani into dani.wallet.txt
./cryptomoney.sh generate dani.wallet.txt
export dani=`./cryptomoney.sh address dani.wallet.txt`
echo dani.wallet.txt wallet signature: $dani
echo funding dani wallet with 1000
./cryptomoney.sh fund $dani 1000 04-dani-funding.txt

./cryptomoney.sh verify alice.wallet.txt 01-alice-funding.txt
./cryptomoney.sh verify bob.wallet.txt 02-bob-funding.txt
./cryptomoney.sh verify charlie.wallet.txt 03-charlie-funding.txt
./cryptomoney.sh verify dani.wallet.txt 04-dani-funding.txt

echo mining the block with prefix of 2
./cryptomoney.sh mine 2

for i in {0..8}
do
	a=$(($((i*3))+5));
	b=$(($((i*3))+6));
	c=$(($((i*3))+7));
	echo transfering 3 from bob to alice
	./cryptomoney.sh transfer bob.wallet.txt $alice 3 "${a}-bob-to-alice.txt"
	echo transfering 3 from charlie to alice
	./cryptomoney.sh transfer charlie.wallet.txt $alice 3 "${b}-charlie-to-alice.txt"
	echo transfering 3 from dani to alice
	./cryptomoney.sh transfer dani.wallet.txt $alice 3 "${c}-dani-to-alice.txt"
	./cryptomoney.sh verify bob.wallet.txt "${a}-bob-to-alice.txt"
	./cryptomoney.sh verify charlie.wallet.txt "${b}-charlie-to-alice.txt"
	./cryptomoney.sh verify dani.wallet.txt "${c}-dani-to-alice.txt"
done

echo mining the block with prefix of 2
./cryptomoney.sh mine 2
sha256sum block_2.txt

echo checking the balances
./cryptomoney.sh balance $alice
./cryptomoney.sh balance $bob
./cryptomoney.sh balance $charlie
./cryptomoney.sh balance $dani

echo validating the cryptocurrency chain
./cryptomoney.sh validate