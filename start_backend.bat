@echo off
cls
echo.
echo ====================================
echo   ENTERPRISE SCANNER BACKEND
echo ====================================
echo.
echo Starting Flask backend server...
echo Database: SQLite (enterprise_scanner.db)
echo.
echo Server will be available at:
echo   http://localhost:5000
echo.
echo API Endpoints:
echo   http://localhost:5000/api/leads
echo   http://localhost:5000/api/chat
echo   http://localhost:5000/api/security-assessment
echo.
echo Press Ctrl+C to stop the server
echo.
echo ====================================
echo.
cd backend
python app.py
pause
