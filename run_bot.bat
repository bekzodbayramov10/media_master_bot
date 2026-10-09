@echo off
cd /d "C:\Users\Bekzod\OneDrive\Desktop\boost_bot"
:loop
py -3.12 bot.py
echo Bot toxtadi, 5 soniyadan keyin qayta ishga tushadi...
timeout /t 5 /nobreak >nul
goto loop
