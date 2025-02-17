from pyteal import *

def dex_lsig():
    # check no rekeying, close remainder to, asset close to
    common_fields = And(
        Gtxn[0].rekey_to() == Global.zero_address(),
        Gtxn[1].rekey_to() == Global.zero_address(),
        Gtxn[2].rekey_to() == Global.zero_address(),
        Gtxn[0].close_remainder_to() == Global.zero_address(),
        Gtxn[1].close_remainder_to() == Global.zero_address(),
        Gtxn[2].close_remainder_to() == Global.zero_address(),
        Gtxn[0].asset_close_to() == Global.zero_address(),
        Gtxn[1].asset_close_to() == Global.zero_address(),
    )

    # verify that buyer deposits old tokens
    first_tx = And(
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].xfer_asset() == Tmpl.Int("TMPL_OLD_BOND"),
        Gtxn[0].asset_amount() == Gtxn[1].asset_amount()
    )

    # verify dex sends new bond tokens to buyer
    second_tx = And(
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].xfer_asset() == Tmpl.Int("TMPL_NEW_BOND"),
    )

    # verify dex pays coupon value to buyer
    # coupon value amount is verified by the app.
    third_tx = And(
        Gtxn[2].type_enum() == TxnType.Payment,  # coupon value payment
        Gtxn[3].type_enum() == TxnType.ApplicationCall,
        Gtxn[3].application_id() == Tmpl.Int("TMPL_APPLICATION_ID"),
        Gtxn[3].application_args[0] == Bytes("redeem_coupon")
    )

    # Opt-in transaction. We need to opt-in to OLD and NEW bond.
    # Note: we are checking that first transaction is payment with amount 0
    # and sent by store manager, because we don't want another
    # user to opt-in too many asa/app and block this address
    opt_in = And(
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() == Int(0),
        Gtxn[0].sender() == Tmpl.Addr("TMPL_APP_MANAGER"),
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0)
    )

    # verify redeem bond token exchange transaction (B_i -> B_i+1)
    # User sends B_i to DEX_i lsig.
    # DEX_i sends B_{i+1} to the user.
    # Dex pays coupon value
    verify_exchange = And(common_fields, first_tx, second_tx, third_tx)

    program = program = Cond(
        [Global.group_size() == Int(4), verify_exchange],
        [Global.group_size() == Int(2), opt_in],
    )

    return program

if __name__ == "__main__":
    print(compileTeal(dex_lsig(), Mode.Signature, version = 4))
