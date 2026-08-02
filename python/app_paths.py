import os


BASE_DIR = "/home/pi/coffeapag"
APP_DIR = os.path.join(BASE_DIR, "coffea_proj_auto")
PYTHON_DIR = os.path.join(APP_DIR, "python")

SETTINGS_DIR = os.path.join(BASE_DIR, "settings")
LOGS_DIR = os.path.join(BASE_DIR, "log_files")
RUNTIME_DIR = os.path.join(BASE_DIR, "runtime_files")

VERSION_FILE = os.path.join(PYTHON_DIR, "settings_files", "version.txt")

PRICE_LIST_FILE = os.path.join(SETTINGS_DIR, "listaPrecos.txt")
HELLO_SETTING_FILE = os.path.join(SETTINGS_DIR, "helloScreenSetting.txt")
PAYMENT_METHODS_FILE = os.path.join(SETTINGS_DIR, "paymentMethods.txt")
MAC_ADDRESS_FILE = os.path.join(SETTINGS_DIR, "enderecoMAC.txt")
CONN_CHECK_FILE = os.path.join(SETTINGS_DIR, "connCheck.txt")
PULSE_COIN_FILE = os.path.join(SETTINGS_DIR, "pulseCoinValue.txt")
SYSTEM_ID_FILE = os.path.join(SETTINGS_DIR, "systemId.txt")
SYSTEM_NAME_FILE = os.path.join(SETTINGS_DIR, "systemName.txt")
SERVER_PAIRING_TOKEN_FILE = os.path.join(SETTINGS_DIR, "serverPairingToken.txt")
SERVER_PAIRING_MODE_FILE = os.path.join(SETTINGS_DIR, "serverPairingMode.txt")
REMOTE_COMMAND_RESULT_FILE = os.path.join(SETTINGS_DIR, "remoteCommandResult.json")
UPDATE_INPUT_FILE = os.path.join(SETTINGS_DIR, "update_input.txt")
ULTIMO_PAGAMENTO_FILE = os.path.join(SETTINGS_DIR, "ultimoPagamento.txt")

DIAGNOSTIC_OUTBOX_FILE = os.path.join(LOGS_DIR, "diagnostic_outbox.sqlite3")
PIX_QRCODE_FILE = os.path.join(RUNTIME_DIR, "qrCodePix.png")


def ensure_directory(path):
    os.makedirs(path, exist_ok=True)


def ensure_parent_dir(file_path):
    ensure_directory(os.path.dirname(file_path))


def ensure_runtime_layout():
    ensure_directory(SETTINGS_DIR)
    ensure_directory(LOGS_DIR)
    ensure_directory(RUNTIME_DIR)
