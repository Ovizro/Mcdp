@echo off
set USE_CYTHON=1
python setup.py develop || goto failed
cd mcdp
move *.h include
cd variable
move *.h ../include
goto end

:failed
echo failed

:end