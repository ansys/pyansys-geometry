@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
if "%SPHINXOPTS%" == "" (
	set SPHINXOPTS=-j auto -W --color
)
set SOURCEDIR=source
set APIDIR=source\api
set BUILDDIR=_build

if "%1" == "" goto help
if "%1" == "help" goto help
if "%1" == "clean" goto clean
if "%1" == "pdf" goto pdf
if "%1" == "html" goto html
if "%1" == "linkcheck" goto linkcheck
if "%1" == "single-example" goto single-example

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:linkcheck
%SPHINXBUILD% -M linkcheck %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:html
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:pdf
%SPHINXBUILD% -M latex %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
cd "%BUILDDIR%\latex"
for %%f in (*.tex) do (
pdflatex "%%f" --interaction=nonstopmode)
if NOT EXIST ansys-geometry-core.pdf (
	Echo "no pdf generated!"
	exit /b 1)
Echo "pdf generated!"
goto end

:clean
rmdir /s /q %BUILDDIR% > /NUL 2>&1
rmdir /s /q %APIDIR% > /NUL 2>&1
goto end

:single-example
if "%2" == "" (
	echo. No example specified.
	echo. Example: ./make.bat single-example examples/01_getting_started/01_math.mystnb
	exit /b 1
)
echo Building single example: %2
set BUILD_API=false
set SKIP_BUILD_CHEAT_SHEET=true
set SPHINXOPTS=-j auto
%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O% -D "include_patterns=index.rst,examples.rst,%2"
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:end
popd
