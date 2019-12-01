ren ext ext_
ren config.py config_.py
del /F /Q build
del /F /Q dist
pyinstaller -F --hidden-import=pymssql --hidden-import=_mssql --hidden-import=win32timezone service.py -n persoService
pyinstaller -F --hidden-import=pymssql --hidden-import=_mssql --hidden-import=win32timezone run.py -n run
ren ext_ ext
ren config_.py config.py
 