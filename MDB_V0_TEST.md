# MDB version-zero test

This branch adds a local-only `Pulso`/`MDB` choice to the Raspberry Pi's
advanced settings. It does not add or change any server setting or API.
`Pulso` is the safe default when the setting is absent or invalid.

## Install on the Raspberry Pi

1. Install the one new dependency with
   `python -m pip install -r requirements-mdb-v0.txt`.
2. Disable the Linux login console on the primary UART, but leave the UART
   hardware enabled. Confirm that `/dev/serial0` resolves to the GPIO UART and
   that no `serial-getty` service owns it.
3. Connect ESP GPIO10/TX to Pi GPIO15/RX (physical pin 10), ESP GPIO11/RX to
   Pi GPIO14/TX (physical pin 8), and connect grounds. Do not connect `3V3`,
   `VIN`, or `PULSE` between the boards.
4. Flash the sibling `mdb-pi-bridge-esp32s3` project.
5. Start the existing Pi application, open advanced settings, select `MDB`,
   save, and let the existing launcher restart the application.

The application is the sole `/dev/serial0` owner. It also takes a non-blocking
process lock at `/home/pi/coffeapag/runtime_files/mdb_serial0.lock`; a second
instance refuses ownership instead of competing for bytes.

## Test sequence

Start with low-value, operator-observed transactions.

1. Confirm the UI reaches `Selecione um produto na máquina` without a touch.
2. Select an item on the VMC and confirm the Pi displays the exact BRL price.
3. Cancel once before payment. Verify that the transcript contains correlated
   `DENY` before `CANCEL` and that no vend is approved.
4. Complete a payment. Verify that `ACK command=APPROVE` only changes the UI to
   `Aguardando ... liberar o produto`; it must not log sale success.
5. Verify success is logged only after the matching `MDB VEND_SUCCESS`.
6. Exercise VEND_FAILURE, VMC cancel, ESP reset, UART disconnect, Pi process
   restart during payment, and a payment that finishes after VMC cancellation.

An ambiguous or late charged payment intentionally stops on the red recovery
screen. Check the Moderninha/Pix record and the VMC physically before pressing
`Já verifiquei — encerrar sessão`.

## Timeout behavior in version zero

- Pix retains the existing 300-second status polling window. Expiry queues a
  correlated MDB denial and then session cancellation.
- Moderninha retains the existing blocking PlugPag behavior; the base project
  has no application-level Moderninha timer. A VMC cancel/reset makes any later
  terminal success ambiguous and forces operator recovery.
- The firmware continues to advertise the proven 30-second MDB application
  response time. During Snakky testing, record the actual VMC cancellation time
  before considering a separate firmware change.

## Currency and amounts

For this test build, the proven MDB setup bytes remain unchanged:
currency `0x0840`, scale factor `1`, decimal places `2`. The Pi interprets the
VMC vend price as centavos and charges `price / 100` BRL. `0x0840` is not the
packed ISO-4217 numeric value for BRL, so that semantic mismatch is documented
but deliberately not changed before a separate machine compatibility test.
