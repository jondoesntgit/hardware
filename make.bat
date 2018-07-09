@ECHO OFF

REM Command file for running tests
pushd %~dp0

if "%1" == "test" goto test
if "%1" == "upload_tests" goto tests

:test
py.test
goto end

:upload_tests
coverage run --source hardware setup.py test
codecov --token=d7078188-16c9-4e86-8d10-2b3c9f1aa992
goto end

:end
popd
