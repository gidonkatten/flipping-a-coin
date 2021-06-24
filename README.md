# flipping-a-coin

This project **hasn't been security audited** and should not be used in a production environment.

## Requirements

* Linux or macOS
* Python 3. The scripts assumes the Python executable is called `python3`.
* The [Algorand Node software](https://developer.algorand.org/docs/run-a-node/setup/install/). A private network is used, hence there is no need to sync up MainNet or TestNet. `goal` is assumed to be in the PATH.

## Setup

To install all required packages, run: 
```bash
python3 -m pip install -r requirements.txt
```

## Usage

There are a number of bash script files which execute the goal commands for you.

They should be run in the following order:
1. **startnet.sh**: Sets up private network
2. **createapp.sh**: Compiles the PyTeal files to TEAL and deploys the stateful smart contract 
3. **fundescrow.sh**: Send Algos to escrow account
4. **linkapptoescrow.sh**: Adds the escrow address to the application's global state
5. **flip.sh**: Flip the coin - specify hashed coin flip result and amount bet
6. **guess.sh**: Guess the coin flip - specify HEADS (1) or TAILS (0) and match amount bet
7. **reveal.sh**: Reveal the coin flip - specify HEADS (1) or TAILS (0) and nonce used
8. **claim.sh**: Winner can claim the combined amount bet
8. **stopnet.sh**: Delete private network

Note that the scripts assume the application has ID `APP_ID=1`.
In particular, no transactions should be made before calling `createapp.sh`.

Scripts `5-8` can be continuosly run in cycles, specifying different flips and different guesses.
