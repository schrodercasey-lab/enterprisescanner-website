@echo off
echo.
echo ==========================================
echo    ENTERPRISE SCANNER - QUICK START
echo ==========================================
echo.
echo 🚀 Starting Enterprise Scanner Platform...
echo.

cd /d "C:\Users\schro\OneDrive\Desktop\BugBountyScanner\workspace"

echo ✅ Activating Python environment...
call .venv\Scripts\activate.bat

echo ✅ Starting stable production server...
echo.
echo 🌐 Platform will be available at:
echo    Main Site: http://localhost:5000
echo    Live Chat: http://localhost:5000/chat-demo
echo    Analytics: http://localhost:5000/analytics
echo.
echo 💼 Ready for Fortune 500 demonstrations!
echo.
echo ----------------------------------------
echo Press Ctrl+C to stop the server
echo ----------------------------------------
echo.

python stable_server.py

pause