#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

PYTHON=python3
gcmd="goal -d ../net1/Primary"
FLIPPER=$(${gcmd} account list|awk '{ print $3 }'|tail -1)
GUESSER=$(${gcmd} account list|awk '{ print $3 }'|head -1)

TEAL_APPROVAL_PROG="../contracts/stateful.teal"
TEAL_ESCROW="../contracts/escrow.teal"
APP_ID=1

# get escrow address
ESCROW_ADDRESS=$(
  ${gcmd} clerk compile -n "$TEAL_ESCROW" \
  | awk '{ print $2 }' \
  | head -n 1
)
echo "Escrow Address = $ESCROW_ADDRESS"

AMOUNT=4000000 # 4 Algo bet
TAILS=0
HEADS=1
NONCE="test"
SECRET=`$PYTHON -c "import hashlib;import base64;print(base64.b64encode(hashlib.sha256(str('${TAILS}${NONCE}').encode('utf-8')).digest()).decode('utf-8'))"`
# create transactions
${gcmd} app call --app-id "$APP_ID" --app-arg "str:flip" --app-arg "b64:$SECRET" -f "$FLIPPER" -o unsignedtx0.tx
${gcmd} clerk send -a "$AMOUNT" -f "$FLIPPER" -t "$ESCROW_ADDRESS" -o unsignedtx1.tx
# combine transactions
cat unsignedtx0.tx unsignedtx1.tx > combinedtransactions.tx
# group transactions
${gcmd} clerk group -i combinedtransactions.tx -o groupedtransactions.tx
# split transactions
${gcmd} clerk split -i groupedtransactions.tx -o split.tx
# sign transactions
${gcmd} clerk sign -i split-0.tx -o signout-0.tx
${gcmd} clerk sign -i split-1.tx -o signout-1.tx
# assemble transaction group
cat signout-0.tx signout-1.tx > signout.tx
# submit
${gcmd} clerk rawsend -f signout.tx

# DEBUG
#${gcmd} clerk dryrun -t signout.tx --dryrun-dump -o dr.json
#tealdbg debug "$TEAL_APPROVAL_PROG" -d dr.json --group-index 0

# read global state
${gcmd} app read --app-id "$APP_ID" --guess-format --global --from "$FLIPPER"

# clean up files
rm -f *.tx
rm -f *.rej
rm -f *.json