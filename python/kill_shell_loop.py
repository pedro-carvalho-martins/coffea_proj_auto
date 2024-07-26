import subprocess
import os
import signal

def kill_pid_executar():

    # Find the PID(s) of the running script
    result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
    processes = result.stdout.splitlines()

    for process in processes:
        if 'executar.sh' in process:
            # Extract the PID (second column)
            pid = int(process.split()[1])
            try:
                # Kill the process
                os.kill(pid, signal.SIGTERM)
                print(f"Terminated process {pid} for executar2.sh")
            except ProcessLookupError:
                print(f"Process {pid} not found")
            except PermissionError:
                print(f"Permission denied to kill process {pid}")
            except Exception as e:
                print(f"Failed to terminate process {pid}: {e}")