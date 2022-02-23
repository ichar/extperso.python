ren ext ext_
ren config.py config_.py
del /F /Q build
del /F /Q dist
pyinstaller -F --hidden-import=pymssql --hidden-import=_mssql --hidden-import=win32timezone service.py -n persoService
ren ext_ ext
ren config_.py config.py
