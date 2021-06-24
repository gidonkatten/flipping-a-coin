import sys
from pyteal import *


def contract_account(app_id):

    linked_with_app_call = And(
        Gtxn[0].type_enum() == TxnType.ApplicationCall,
        Gtxn[0].application_id() == Int(app_id)
    )

    return Int(1)


if __name__ == "__main__":
    arg = int(sys.argv[1])
    print(compileTeal(contract_account(arg), Mode.Signature, version=3))
