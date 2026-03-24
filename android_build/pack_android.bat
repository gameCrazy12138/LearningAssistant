@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo LearningAssistant Android APK 打包工具
echo ========================================
echo.

REM 检查 Docker 是否安装
echo [1/4] 检查 Docker 环境...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 未安装！
    echo.
    echo 请先安装 Docker Desktop:
    echo 下载地址：https://www.docker.com/products/docker-desktop/
    echo.
    echo 安装指南请查看：docs\Docker 安装指南.md
    echo.
    pause
    exit /b 1
)

echo [完成] Docker 已安装
docker --version
echo.

REM 检查 Docker 是否运行
echo [2/4] 检查 Docker 运行状态...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker 未运行！
    echo.
    echo 请启动 Docker Desktop 应用
    echo 等待底部状态栏变绿后再试
    echo.
    pause
    exit /b 1
)

echo [完成] Docker 正在运行
echo.

REM 检查 buildozer.spec 是否存在
echo [3/4] 检查配置文件...
if not exist "buildozer.spec" (
    echo [错误] 找不到 buildozer.spec 文件！
    echo.
    pause
    exit /b 1
)

echo [完成] 配置文件就绪
echo.

REM 开始打包
echo [4/4] 开始构建 Android APK...
echo.
echo =====================================================
echo 重要提示：
echo - 首次构建需要下载大量依赖（约 2-5GB）
echo - 首次构建时间：20-40 分钟
echo - 后续构建时间：5-10 分钟
echo - 请确保网络连接稳定
echo - 请确保磁盘空间充足（至少 10GB）
echo =====================================================
echo.
set /p confirm="是否继续？(Y/N): "
if /i not "%confirm%"=="Y" (
    echo.
    echo 已取消打包
    pause
    exit /b 0
)

echo.
echo 开始打包，请稍候...
echo.

REM 运行 Docker 打包命令
docker run --rm -v %CD%:/home/user/hostcwd kivy/buildozer android debug

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [成功] APK 构建完成！
    echo ========================================
    echo.
    echo APK 文件位置：bin\*-debug.apk
    echo.
    
    REM 复制 APK 到发布目录
    set TARGET_DIR=..\dist\LearningAssistant_android
    if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
    
    echo 正在复制 APK 到发布目录...
    xcopy "bin\*-debug.apk" "%TARGET_DIR%\" /Y
    
    if %errorlevel% equ 0 (
        echo [完成] APK 已复制到：%TARGET_DIR%
    ) else (
        echo [警告] APK 复制失败，可手动复制
    )
    
    echo.
) else (
    echo.
    echo ========================================
    echo [错误] 构建失败，请检查上方错误信息
    echo ========================================
    echo.
    echo 常见问题：
    echo 1. 网络连接问题 - 检查网络或更换 DNS
    echo 2. 磁盘空间不足 - 清理磁盘释放 10GB+ 空间
    echo 3. Java 版本错误 - 需要使用 Java 8
    echo 4. 其他问题 - 查看详细日志
    echo.
)

pause
