@echo off
echo Cleaning Python cache...
del /s /q backend\__pycache__ 2>nul
del /s /q backend\api\__pycache__ 2>nul
del /s /q backend\services\__pycache__ 2>nul
echo.
echo Starting backend...
cd backend
python -B app.py
pause
