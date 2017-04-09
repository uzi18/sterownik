local zadana = 21                       --zadana temperatura
local histereza = 1                     --histereza
local termostat = 'termostat'           --wirtualny przełącznik z Domoticza

commandArray = {}
--print('wartosc temperatury:' .. tonumber(otherdevices['salon']))

if (otherdevices[termostat]=='On') then

	if (devicechanged['salon']) then
	--print(tonumber(otherdevices['salon_Temperature']))
		if (tonumber(otherdevices['salon']) > (zadana + histereza)) then
			commandArray[termostat]='Off'
		end	
	end	
	
elseif (otherdevices[termostat]=='Off') then
    
	if (devicechanged['salon']) then
		if  (tonumber(otherdevices['salon']) < (zadana - histereza)) then
			commandArray[termostat]='Off'
		end
	end
end
return commandArray