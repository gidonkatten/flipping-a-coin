#!/bin/bash

date '+keyreg-teal-test start %Y%m%d_%H%M%S'

set -e
set -x
set -o pipefail
export SHELLOPTS

gcmd="goal -d ../net1/Primary"
FLIPPER=$(${gcmd} account list|awk '{ print $3 }'|tail -1)
GUESSER=$(${gcmd} account list|awk '{ print $3 }'|head -1)

TEAL_APPROVAL_PROG="../contracts/stateful.teal"

APP_ID=1
TAILS=0
HEADS=1
NONCE="test"
# reveal original coin flip
${gcmd} app call --app-id "$APP_ID" --app-arg "str:reveal" --app-arg "int:$TAILS" --app-arg "str:$NONCE" -f "$FLIPPER"

# DEBUG
#${gcmd} app call --app-id "$APP_ID" --app-arg "str:reveal" --app-arg "int:$REVEALED" --app-arg "str:$NONCE" -f "$FLIPPER" --dryrun-dump -o dr.json
#tealdbg debug "$TEAL_APPROVAL_PROG" -d dr.json --group-index 0

# read global state
${gcmd} app read --app-id "$APP_ID" --guess-format --global --from "$FLIPPER"
