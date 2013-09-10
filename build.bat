set version=1.0.0
set file=cfc-v%version%.o8g
@if exist %file% del %file%
"C:\Program Files\Tools\Zip\7-Zip\7z.exe" a -tzip %file% -xr!*.psd -xr!.git* -xr!*.o8g -x!build.bat