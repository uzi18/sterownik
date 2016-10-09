set IPADDRESS=http://192.168.2.4

@echo off
set SubDir=www/
for %%f in (%SubDir%*.*) do (
echo uploading %SubDir%%%f to %IPADDRESS%/upload/
curl.exe -0 -T %SubDir%%%f %IPADDRESS%/upload/

)
echo Done!
pause
