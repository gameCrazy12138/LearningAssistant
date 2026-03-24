@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo.
echo ========================================
echo   GitHub Actions 在线打包助手
echo ========================================
echo.

REM 检查 Git 是否安装
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git 未安装！
    echo 请先安装 Git: https://git-scm.com/
    pause
    exit /b 1
)

echo [1/4] 初始化 Git 仓库...
if not exist ".git" (
    git init
    git branch -M main
    echo Git 仓库已初始化
) else (
    echo Git 仓库已存在
)

echo.
echo [2/4] 提交当前代码...
git add .
git commit -m "准备打包 APK v3.0.4"

echo.
echo [3/4] 推送到 GitHub...
echo.
echo 请输入你的 GitHub 仓库地址:
echo 格式：https://github.com/YOUR_USERNAME/LearningAssistant.git
echo.
set /p REPO_URL=
if "%REPO_URL%"=="" (
    echo [错误] 未输入仓库地址
    pause
    exit /b 1
)

git remote set-url origin %REPO_URL% 2>nul || git remote add origin %REPO_URL%
git push -u origin main

echo.
echo [4/4] 打标签触发打包...
echo.
set /p VERSION=请输入版本号 (例如 v3.0.4，直接回车使用 v3.0.4): 
if "%VERSION%"=="" set VERSION=v3.0.4

echo 创建标签：%VERSION%
git tag %VERSION%
git push origin %VERSION%

echo.
echo ========================================
echo   ✅ 打包已触发！
echo ========================================
echo.
echo 下一步：
echo 1. 访问：https://github.com/YOUR_USERNAME/LearningAssistant/actions
echo 2. 等待 20-30 分钟（首次可能更长）
echo 3. 在 Actions 页面下载 APK 文件
echo.
echo 查看构建进度：
echo https://github.com/YOUR_USERNAME/LearningAssistant/actions
echo.
pause
