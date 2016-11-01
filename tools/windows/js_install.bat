@echo off

call "%~dp0_settings.bat"
prompt $LQ$G$S$P$G
rem echo %1%
cd %~dp0

rem to get jumpscale code
git clone https://github.com/Jumpscale/jumpscale_core8.git
cd jumpscale_core8
git pull origin @ys:@ys
git checkout @ys
cd ..

mkdir Lib\site-packages\JumpScale
junction  Lib\site-packages\JumpScale\baselib jumpscale_core8\lib\JumpScale\baselib 
junction  Lib\site-packages\JumpScale\core jumpscale_core8\lib\JumpScale\core
junction  Lib\site-packages\JumpScale\grid jumpscale_core8\lib\JumpScale\grid
copy jumpscale_core8\install\InstallTools.py Lib\site-packages\JumpScale\InstallTools.py
copy jumpscale_core8\lib\JumpScale\__init__.py Lib\site-packages\JumpScale\__init__.py

mkdir hrd\system