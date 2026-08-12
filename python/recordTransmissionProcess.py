"""Transmit queued Pi records after a safe, paired heartbeat."""

import localRecordQueue
import pixDeliveryConfirmation
import rwServerPairingSettings
import rwSystemId
import shared_resource
from app_paths import PENDING_EVENTS_FILE, PENDING_TRANSACTIONS_FILE
from server_api_client import post_json


BATCH_SIZE = 50


def _customer_interaction_blocks(allow_during_customer_interaction):
    return (
        shared_resource.customer_interaction_active.is_set()
        and not allow_during_customer_interaction
    )


def _send_batch(
    endpoint,
    records,
    id_field,
    file_path,
    fieldnames,
    allow_during_customer_interaction=False,
):
    if not records or _customer_interaction_blocks(
        allow_during_customer_interaction
    ):
        return 0

    response = post_json(
        endpoint,
        {
            "sistema_pag_id": rwSystemId.readSystemId(),
            "records": records,
        },
        rwServerPairingSettings.read_pairing_token(),
        timeout=15,
    )
    return localRecordQueue.acknowledge_records(
        file_path,
        fieldnames,
        id_field,
        response.get("accepted_ids", []),
    )


def transmit_pending_records(
    allow_during_customer_interaction=False,
    include_pix=True,
):
    """Send one bounded batch of each record type without affecting heartbeat state."""
    if _customer_interaction_blocks(allow_during_customer_interaction):
        return False

    try:
        if include_pix:
            pixDeliveryConfirmation.transmit_pending()

        if _customer_interaction_blocks(allow_during_customer_interaction):
            return True

        transactions = localRecordQueue.read_batch(
            PENDING_TRANSACTIONS_FILE,
            localRecordQueue.TRANSACTION_FIELDS,
            BATCH_SIZE,
        )
        _send_batch(
            "/transactions/batch",
            transactions,
            "record_id",
            PENDING_TRANSACTIONS_FILE,
            localRecordQueue.TRANSACTION_FIELDS,
            allow_during_customer_interaction,
        )

        if _customer_interaction_blocks(allow_during_customer_interaction):
            return True

        events = localRecordQueue.read_batch(
            PENDING_EVENTS_FILE,
            localRecordQueue.EVENT_FIELDS,
            BATCH_SIZE,
        )
        _send_batch(
            "/events/batch",
            events,
            "event_id",
            PENDING_EVENTS_FILE,
            localRecordQueue.EVENT_FIELDS,
            allow_during_customer_interaction,
        )
        return True
    except Exception:
        # Upload failures must never affect payments or create self-referential logs.
        return False
