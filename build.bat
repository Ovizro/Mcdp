@echo off
set USE_CYTHON=1
python setup.py develop || goto failed
cd mcdp
move *.h include
exit

:failed
echo failed