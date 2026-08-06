"""Determine whether startup has at least one usable payment method."""


CARD_METHODS = ("Débito", "Crédito", "Voucher")


def classify_server_connection(pairing_state):
    status = pairing_state.get("status")
    if status == "paired":
        return "check"
    if status == "pending":
        return "pending"
    if status == "offline":
        return "disabled"

    error_message = str(pairing_state.get("last_error", "")).casefold()
    if "network is unreachable" in error_message:
        return "no_internet"
    return "connection_problem"


def evaluate_connection_outcome(settings, moderninha_status, pix_status):
    cards_enabled = any(
        settings.get(payment_method) == "enabled"
        for payment_method in CARD_METHODS
    )
    pix_enabled = settings.get("QR Code (Pix)") == "enabled"

    cards_available = cards_enabled and moderninha_status == "check"
    pix_available = pix_enabled and pix_status == "check"

    if not cards_available and not pix_available:
        return -1

    enabled_connection_failed = (
        cards_enabled and moderninha_status != "check"
    ) or (
        pix_enabled and pix_status != "check"
    )
    return 1 if enabled_connection_failed else 0
