@echo off
set USE_CYTHON=1
python setup.py develop || goto failed
cd mcdp
rem Move all .h files to the include directory
for /r %%f in (*.h) do move "%%f" include
goto end

:failed
echo Mcdp package building failed

:end