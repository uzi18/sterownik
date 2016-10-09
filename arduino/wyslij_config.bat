set IPADDRESS=http://192.168.2.4

@echo off
echo uploading config.txt to %IPADDRESS%/upload/
curl.exe -0 -T config.txt %IPADDRESS%/upload/

echo Done!
pause
