from pyteal import *


def stateful():
    # HEADS is non-zero - TAILS is zero

    # set escrow address
    escrow = App.globalGetEx(Int(0), Bytes('escrow'))
    on_set_escrow = Seq([
        Assert(Global.group_size() == Int(1)),
        Assert(Txn.sender() == Global.creator_address()),
        escrow,
        Assert(Not(escrow.hasValue())),
        App.globalPut(Bytes('escrow'), Txn.application_args[1]),
        Int(1)
    ])

    # flip coin
    on_flip = Seq([
        Assert(Global.group_size() == Int(2)),
        # check payment
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].sender() == Txn.sender()),
        Assert(Gtxn[1].receiver() == App.globalGet(Bytes('escrow'))),
        # store flip
        App.globalPut(Bytes('bet'), Gtxn[1].amount()),
        App.globalPut(Bytes('secret'), Txn.application_args[1]),
        App.globalPut(Bytes('flipper'), Txn.sender()),
        Int(1)
    ])

    # guess
    bet = App.globalGetEx(Int(0), Bytes('bet'))
    guess = App.globalGetEx(Int(0), Bytes('guess'))
    one_day = Int(86400)
    on_guess = Seq([
        Assert(Global.group_size() == Int(2)),
        # check there is an available bet
        bet,
        Assert(bet.hasValue()),
        guess,
        Assert(Not(guess.hasValue())),
        # check payment
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].sender() == Txn.sender()),
        Assert(Gtxn[1].receiver() == App.globalGet(Bytes('escrow'))),
        Assert(Gtxn[1].amount() == bet.value()),
        # store guess
        App.globalPut(Bytes('guess'), Btoi(Txn.application_args[1]) >= Int(1)),
        App.globalPut(Bytes('guesser'), Txn.sender()),
        App.globalPut(Bytes('expiry'), Global.latest_timestamp() + one_day),
        Int(1)
    ])

    # reveal
    # heads / tail, nonce
    revealed = Btoi(Txn.application_args[1]) >= Int(1)
    nonce = Txn.application_args[1]
    preimage = Concat(Substring(Bytes('01'), revealed, revealed + Int(1)), nonce)
    correct = Eq(App.globalGet(Bytes('secret')), Sha256(preimage))
    on_reveal = Seq([
        Assert(Global.group_size() == Int(1)),
        Assert(correct),
        App.globalPut(Bytes('result'), revealed),
        Int(1)
    ])

    # claim
    result = App.globalGetEx(Int(0), Bytes('result'))
    on_claim = Seq([
        Assert(Global.group_size() == Int(2)),
        # check there was a bet
        bet,
        Assert(bet.hasValue()),
        guess,
        Assert(guess.hasValue()),
        # check winner
        result,
        If(
            Not(result.hasValue()),
            # if no reveal can claim if guesser and past expiry
            Seq([
                Assert(Txn.sender() == App.globalGet(Bytes('guesser'))),
                Assert(Global.latest_timestamp() >= App.globalGet(Bytes('expiry')))
            ]),
            # if have revealed then verify if won
            Cond(
                [
                    Txn.sender() == App.globalGet(Bytes('flipper')),
                    Assert(result.value() != App.globalGet(Bytes('guess')))
                ],
                [
                    Txn.sender() == App.globalGet(Bytes('guesser')),
                    Assert(result.value() == App.globalGet(Bytes('guess')))
                ],
            )
        ),
        # check payment
        Assert(Gtxn[1].type_enum() == TxnType.Payment),
        Assert(Gtxn[1].sender() == App.globalGet(Bytes('escrow'))),
        Assert(Gtxn[1].receiver() == App.globalGet(Bytes('escrow'))),
        Assert(Gtxn[1].amount() == (bet.value() * Int(2))),
        # clean up global state for next coin flip
        App.globalDel(Bytes('bet')),
        App.globalDel(Bytes('secret')),
        App.globalDel(Bytes('flipper')),
        App.globalDel(Bytes('guess')),
        App.globalDel(Bytes('guesser')),
        App.globalDel(Bytes('expiry')),
        Int(1)
    ])

    program = Cond(
        [Txn.on_completion() == OnComplete.DeleteApplication, Int(0)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(0)],
        [Txn.on_completion() == OnComplete.CloseOut, Int(1)],
        [Txn.on_completion() == OnComplete.OptIn, Int(1)],
        # On app creation
        [Txn.application_id() == Int(0), Int(1)],
        # Must be a NoOp transaction
        [Txn.application_args[0] == Bytes("set_escrow"), on_set_escrow],
        [Txn.application_args[0] == Bytes("flip"), on_flip],
        [Txn.application_args[0] == Bytes("guess"), on_guess],
        [Txn.application_args[0] == Bytes("reveal"), on_reveal],
        [Txn.application_args[0] == Bytes("flip"), on_claim]
    )

    return And(Txn.group_index() == Int(0), program)


if __name__ == "__main__":
    print(compileTeal(stateful(), Mode.Application, version=3))
