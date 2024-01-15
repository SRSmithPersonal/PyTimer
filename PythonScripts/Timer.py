import subprocess
import time


def sleep_killer(t, proc):
    time.sleep(t)
    subprocess.call(f'TASKKILL /F /IM {proc}', shell=True)
    time.sleep(10)


def get_procs():
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select ProcessName'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    li = []
    for line in proc.stdout:
        if line.rstrip():
            ll = line.decode().rstrip()
            if ll not in ["ProcessName", "-----------", "ApplicationFrameHost", "SystemSettings", "TextInputHost"]:
                li.append(ll)
    return li
