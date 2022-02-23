import os
import subprocess
from subprocess import Popen, PIPE

default_print_encoding = 'cp866'
default_unicode        = 'utf-8'
default_encoding       = 'cp1251'
default_iso            = 'ISO-8859-1'

cwd = "G:/apps/perso"
config = "perso.config.default"
command = "CSD::PostBank_ID::21-0-0::[everything,ext.order_generate.postbank.change_delivery_date,\'21.10.2019\',311001]"
"""
# 1. Popen call
args = [
    #"C:/apps/perso/run.exe",
    #"C:/apps/perso/run.bat",
    os.path.join(cwd, "run.exe"),
    cwd,
    config,
    command
]

proc = Popen(args, cwd=cwd, shell=False, stdout=PIPE, stderr=PIPE)
proc.wait()

res = proc.communicate()  # tuple('stdout', 'stderr')

print(proc.returncode)
if proc.returncode:
    print(res[1].decode(default_print_encoding))
print('result:', res[0].decode(default_print_encoding))
"""

args = [
    os.path.join(cwd, "run.exe"),
    cwd,
    config,
    command
]

code = subprocess.call(args)

print('code:', code)

"""
# 2. Unix only
import os
a = os.fork() # копирует текущий процесс и возвращает 0, если теперь находимся внутри дочернего процесса, и PID внутри родительского

args = [
    cwd,
    config,
    command
]

if a == 0:
    mpathTotest = os.path.join(cwd, "run.exe") # имя исполняемого файла
    os.execlp(mpathTotest, *args)
else:
    print(1)
"""
