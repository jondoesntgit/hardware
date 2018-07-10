@ECHO OFF

REM Command file for running tests
pushd %~dp0

if "%1" == "" goto help
if "%1" == "test" goto test
if "%1" == "tests" goto test
if "%1" == "upload" goto upload_tests
if "%1" == "upload_tests" goto upload_tests

echo."%1" is not a valid recipe. Type "make" for help
goto end

:help

echo.
echo.Usage:
echo.
echo.make test
echo.    Runs pytest to evaluate all tests in the test/ directory
echo.
echo.make upload_tests
echo.    Runs tests, then uploads results to codecov

goto end

:test
py.test
goto end

:upload_tests
coverage run --source hardware setup.py test
codecov --token=d7078188-16c9-4e86-8d10-2b3c9f1aa992
goto end

:end
popd
