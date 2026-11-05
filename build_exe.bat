@echo off
rem Build the Windows executable: dist\MotorbikeExpert.exe  (owner: Lam)
rem Run from the repository root:  build_exe.bat
rem Needs Python 3.10+ on PATH. PyInstaller is installed into .venv-build, not into your main Python.

rem Set BUILD_VENV to use another folder, e.g. when the repo path is very long.
if "%BUILD_VENV%"=="" set BUILD_VENV=.venv-build
if not exist "%BUILD_VENV%" (
    python -m venv "%BUILD_VENV%" || goto :error
)
call "%BUILD_VENV%\Scripts\activate.bat" || goto :error
python -m pip install --quiet --upgrade pip pyinstaller || goto :error

python -m unittest discover tests || goto :error

pyinstaller --noconfirm --clean --onefile --windowed ^
    --name MotorbikeExpert ^
    --paths src ^
    --add-data "knowledge_base;knowledge_base" ^
    --add-data "scenarios;scenarios" ^
    src\gui.py || goto :error

echo.
echo Done: dist\MotorbikeExpert.exe
echo Test it on another Windows machine before 12/11.
goto :eof

:error
echo.
echo Build failed.
exit /b 1
