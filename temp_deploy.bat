@echo off
echo Schroeder123! | scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=NUL "website\index.html" "root@134.199.147.45:/var/www/html/index.html"
