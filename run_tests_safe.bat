@echo off
REM Safe Integration Test Runner (No Admin Required)
REM Uses Python directly - no PowerShell elevation needed

echo ======================================================================
echo JUPITER VR PLATFORM - SAFE INTEGRATION TESTING
echo ======================================================================
echo Running tests without admin privileges...
echo.

cd /d "%~dp0"
python test_integration_safe.py

echo.
echo ======================================================================
echo Test complete! Check integration_test_results.json for details.
echo ======================================================================
pause
