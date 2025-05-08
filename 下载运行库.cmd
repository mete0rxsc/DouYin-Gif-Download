@echo off
echo 开始安装依赖...
pip install -r requirements.txt
if %errorlevel% == 0 (
    echo 安装完成
    type nul > installed_deps.flag
) else (
    echo 安装失败
)
pause