@echo off
chcp 65001 > nul
echo ========================================
echo    启动AI简历筛选系统
echo ========================================
echo.

REM 获取脚本所在目录的上一级（项目根目录）
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

cd /d %PROJECT_DIR%

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\activate" (
    echo 错误: 虚拟环境不存在，请先运行 python -m venv venv
    pause
    exit /b
)

call venv\Scripts\activate

streamlit run src/main.py

pause