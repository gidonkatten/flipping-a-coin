import sys
from pyteal import *


def contract_account(app_id):

    rekey_check = Txn.rekey_to() == Global.zero_address()
    fee_check = Txn.fee() <= Int(1000)
    close_remainder_to_check = Txn.close_remainder_to() == Global.zero_address()
    linked_with_app_call = And(
        Gtxn[0].type_enum() == TxnType.ApplicationCall,
        Gtxn[0].application_id() == Int(app_id)
    )

    return Seq([
        Assert(Txn.group_index() == Int(1)),
        Assert(rekey_check),
        Assert(fee_check),
        Assert(Txn.type_enum() == TxnType.Payment),
        Assert(close_remainder_to_check),
        Assert(linked_with_app_call),
        Int(1)
    ])


if __name__ == "__main__":
    arg = int(sys.argv[1])
    print(compileTeal(contract_account(arg), Mode.Signature, version=3))
