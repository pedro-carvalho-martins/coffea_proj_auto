import subprocess
import os
import signal


def _processes():
    result = subprocess.run(
        ["ps", "-eo", "pid=,args="],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    for line in result.stdout.splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) != 2:
            continue
        try:
            yield int(fields[0]), fields[1]
        except ValueError:
            continue


def _terminate_matching(process_name):
    current_pid = os.getpid()
    for pid, command in _processes():
        if pid == current_pid or process_name not in command:
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Terminated process {pid} for {process_name}")
        except ProcessLookupError:
            continue
        except Exception as error:
            print(f"Failed to terminate process {pid}: {error}")


def kill_pid_executar():
    _terminate_matching("run_coffeapag_loop.sh")


def kill_python():
    _terminate_matching("launch_background.py")
    os.kill(os.getpid(), signal.SIGTERM)


def close_application():
    """Stop only the CoffeaPag loop, helper, and current app process."""
    kill_pid_executar()
    kill_python()
