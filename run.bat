@echo off
chcp 65001 > nul
echo ========================================
echo    启动AI简历筛选系统
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate" (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建完成
    echo.
)

REM 激活虚拟环境
call venv\Scripts\activate

REM 检查依赖是否安装
python -c "import langchain" 2>nul
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
)

echo 启动Streamlit应用...
streamlit run src/main.py

pause