@echo off
cd /d "%~dp0"

:: Activar entorno virtual y ejecutar
call .venv\Scripts\activate.bat

:: Compilar si no existe el módulo
if not exist "neuronet_core*.pyd" (
    echo Compilando modulo C++...
    python setup.py build_ext --inplace
    if exist "C:\nb\neuronet_core*.pyd" (
        copy "C:\nb\neuronet_core*.pyd" .
    )
)

:: Ejecutar la GUI
echo Iniciando NeuroNet...
python src\python\neuronet_gui.py

pause
