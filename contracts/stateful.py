from pyteal import *


def stateful():

    linked_with_escrow = Gtxn[1].sender() == App.globalGet(Bytes('escrow'))

    # set escrow address
    on_set_escrow = Seq([
        Assert(Txn.sender() == Global.creator_address()),
        App.globalPut(Bytes('escrow'), Txn.application_args[1]),
        Int(1)
    ])

    # flip coin
    # amount bet, hash of heads / tails with nonce
    on_flip = Int(1)

    # guess
    # heads / tails
    on_guess = Int(1)

    # reveal
    # heads / tail, nonce
    on_reveal = Int(1)

    # claim
    # winner can claim - if didn't reveal or opted out of application then guesser wins
    on_claim = Int(1)

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
