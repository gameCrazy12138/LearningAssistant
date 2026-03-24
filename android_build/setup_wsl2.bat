@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   WSL2 + Buildozer 一键配置助手
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请以管理员身份运行此脚本！
    echo 右键点击脚本 - "以管理员身份运行"
    pause
    exit /b 1
)

echo [1/4] 启用 WSL 功能...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
set WSL_RESULT=%errorlevel%
echo.
if %WSL_RESULT% equ 0 (
    echo [成功] WSL 功能已启用
) else (
    echo [失败] 无法启用 WSL 功能 - 错误代码：%WSL_RESULT%
    pause
    exit /b 1
)

echo.
echo [2/4] 启用虚拟机平台...
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
set VM_RESULT=%errorlevel%
echo.
if %VM_RESULT% equ 0 (
    echo [成功] 虚拟机平台已启用
) else (
    echo [失败] 无法启用虚拟机平台 - 错误代码：%VM_RESULT%
    pause
    exit /b 1
)

echo.
echo [3/4] 设置 WSL2 为默认版本...
wsl --set-default-version 2
set WSL2_RESULT=%errorlevel%
if %WSL2_RESULT% equ 0 (
    echo [成功] WSL2 已设置为默认版本
) else (
    echo [警告] 设置失败，可能需要手动配置 - 错误代码：%WSL2_RESULT%
)

echo.
echo [4/4] 检查 WSL 状态...
wsl --list --verbose

echo.
echo ========================================
echo   ✅ WSL2 基础配置完成！
echo ========================================
echo.
echo ⚠️ 重要提示：
echo 1. 请重启电脑使配置生效
echo 2. 重启后从 Microsoft Store 安装 Ubuntu 22.04
echo 3. 参考 docs\WSL2 打包方案.md 继续配置
echo.
pause
