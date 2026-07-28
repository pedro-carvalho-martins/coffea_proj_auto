import time
import uuid
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import qrcode

import rwServerPairingSettings
import rwSystemId
from app_paths import PIX_QRCODE_FILE, ensure_parent_dir
from server_api_client import DeviceApiError, get_json, post_json


PIX_CREATE_RETRIES = 3
PIX_CREATE_RETRY_DELAY_SECONDS = 1
PIX_STATUS_RETRIES = 3
PIX_STATUS_RETRY_DELAY_SECONDS = 1
PIX_STATUS_INTERVAL_SECONDS = 5
PIX_STATUS_TIMEOUT_SECONDS = 300


def _price_to_centavos(price):
    try:
        normalized = str(price).strip().replace(",", ".")
        value = Decimal(normalized).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Valor Pix invalido") from exc
    if value <= 0:
        raise ValueError("Valor Pix deve ser maior que zero")
    return int(value * 100)


def PixRequest(price_selected):
    if not rwServerPairingSettings.is_online_mode_enabled():
        raise DeviceApiError("Operacao off-line ativada")

    system_id = rwSystemId.readSystemId()
    token = rwServerPairingSettings.read_pairing_token()
    request_id = str(uuid.uuid4())
    payload = {
        "sistema_pag_id": system_id,
        "request_id": request_id,
        "valor_centavos": _price_to_centavos(price_selected),
    }

    last_error = None
    for attempt in range(PIX_CREATE_RETRIES):
        try:
            response = post_json("/pix/charges", payload, token, timeout=30)
            return response["pix_copia_cola"], response["txid"]
        except DeviceApiError as exc:
            last_error = exc
            if attempt + 1 < PIX_CREATE_RETRIES:
                time.sleep(PIX_CREATE_RETRY_DELAY_SECONDS)
    raise last_error


def generate_img_QR_Code_Pix(pixCopiaECola):
    directory_filename_pix_img = PIX_QRCODE_FILE
    img_qrcode = qrcode.make(pixCopiaECola)
    ensure_parent_dir(directory_filename_pix_img)
    img_qrcode.save(directory_filename_pix_img)
    return directory_filename_pix_img


def get_status_cobranca(txid):
    last_error = None
    for attempt in range(PIX_STATUS_RETRIES):
        try:
            return get_json(
                f"/pix/charges/{txid}",
                {"sistema_pag_id": rwSystemId.readSystemId()},
                rwServerPairingSettings.read_pairing_token(),
            )
        except DeviceApiError as exc:
            last_error = exc
            if attempt + 1 < PIX_STATUS_RETRIES:
                time.sleep(PIX_STATUS_RETRY_DELAY_SECONDS)
    raise last_error


def verify_payment_pix(txid):
    elapsed = 0
    while elapsed < PIX_STATUS_TIMEOUT_SECONDS:
        time.sleep(PIX_STATUS_INTERVAL_SECONDS)
        elapsed += PIX_STATUS_INTERVAL_SECONDS
        payment_status = get_status_cobranca(txid)["status"]
        if payment_status == "pendente":
            continue
        if payment_status == "concluida":
            return 0
        return -1
    return -1
