# 🤖 Android APK 打包说明

## ⚠️ 打包前准备

### 当前状态：Docker 未安装

你有 **三个选择**（都无需 Docker）：

---

## 🌐 方案一：GitHub Actions 在线打包（推荐⭐⭐⭐⭐⭐）

**优点**：
- ✅ **无需安装任何软件**（只需 Git）
- ✅ 不占用本地磁盘空间
- ✅ 不消耗本地性能
- ✅ GitHub 服务器帮你打包

**步骤**：
1. 创建 GitHub 仓库
2. 运行 `build_online.bat` 推送代码
3. 在 GitHub Actions 页面下载 APK

**一键脚本**：
```batch
# Windows 端运行
build_online.bat
```

📖 **详细教程**：[`docs\GitHub Actions 打包指南.md`](../docs/GitHub Actions 打包指南.md)

---

##  方案二：WSL2 + Buildozer

**优点**：
- ✅ 无需安装 Docker
- ✅ Kivy 官方推荐方式
- ✅ 稳定可靠，性能更好
- ✅ 一次配置永久使用

**步骤**：
1. 运行 `setup_wsl2.bat` 启用 WSL2（需管理员权限）
2. 重启电脑
3. 从 Microsoft Store 安装 Ubuntu 22.04
4. 参考 `docs\WSL2 打包方案.md` 完成后续配置
5. 在 Ubuntu 终端中运行打包命令

**一键脚本**：
```batch
# Windows 端运行（管理员权限）
setup_wsl2.bat
```

**Ubuntu 中打包命令**：
```bash
cd /mnt/i/code/ai_code_text/android_build
buildozer android debug
```

📖 **详细教程**：[`docs\WSL2 打包方案.md`](../docs/WSL2 打包方案.md)

---

## 💡 方案二：旧版 Docker Desktop（临时方案）

如果不想用 WSL2，可以安装旧版 Docker Desktop 4.25.2。

📖 **详细教程**：[`docs\Docker 安装问题解决方案.md`](../docs/Docker 安装问题解决方案.md)

---

## 📋 安装 Docker Desktop

### 快速步骤

1. **下载 Docker Desktop**
   ```
   https://www.docker.com/products/docker-desktop/
   ```

2. **安装并启动**
   - 运行安装程序
   - 使用 WSL 2 模式（推荐）
   - 等待 Docker 完全启动（状态栏变绿）

3. **验证安装**
   ```powershell
   docker --version
   ```

**详细安装指南请查看：** `docs/Docker 安装指南.md`

---

## 🚀 开始打包

### 方式一：一键脚本（推荐）⭐⭐⭐⭐⭐

安装好 Docker 后，双击运行：
```
pack_android.bat
```

**自动完成：**
- ✅ 检查 Docker 环境
- ✅ 检查 Docker 运行状态
- ✅ 执行打包命令
- ✅ 复制 APK 到发布目录

---

### 方式二：手动命令

在 PowerShell 中运行：

```powershell
cd i:\code\ai_code_text\android_build
docker run --rm -v ${PWD}:/home/user/hostcwd kivy/buildozer android debug
```

---

## 📊 打包信息

| 项目 | 说明 |
|------|------|
| **首次时间** | 20-40 分钟 |
| **后续时间** | 5-10 分钟 |
| **磁盘空间** | 至少 10GB |
| **APK 位置** | `bin/*.apk` |
| **发布目录** | `../dist/LearningAssistant_android/` |

---

## 📦 生成的 APK

**文件名：** `LearningAssistant-v3.0.4-debug.apk`  
**大小：** 约 30-50MB  
**版本：** Debug（可直接安装测试）  
**支持系统：** Android 5.0+ (API 21)

---

## ⚠️ 常见问题速查

### Q: Docker 无法运行？

**解决：**
- 确保 Docker Desktop 已启动
- 检查 BIOS 虚拟化是否开启
- 重启 Docker Desktop

### Q: 构建时间过长？

**正常现象：**
- 首次需要下载 Android SDK、NDK 等（约 2-5GB）
- 后续构建会使用缓存，速度很快

### Q: 空间不足？

**需要空间：** 约 10GB

**清理命令：**
```bash
docker system prune -a
```

### Q: 网络问题导致下载失败？

**建议：**
- 使用稳定网络
- 可尝试更换 DNS（8.8.8.8）
- 耐心等待，Docker 会自动重试

---

## 📞 获取帮助

### 文档资源

- **安装指南：** `docs/Docker 安装指南.md`
- **打包脚本：** `pack_android.bat`
- **官方文档：** https://buildozer.readthedocs.io/

### 遇到问题？

1. 查看详细错误日志
2. 检查 Docker 是否正常运行
3. 确认网络和磁盘空间
4. 参考官方文档或社区论坛

---

## ✅ 打包流程

```
1. 安装 Docker Desktop
   ↓
2. 启动 Docker Desktop（状态栏变绿）
   ↓
3. 运行 pack_android.bat
   ↓
4. 等待 20-40 分钟（首次）
   ↓
5. APK 生成在 bin/ 目录
   ↓
6. 自动复制到 dist/LearningAssistant_android/
   ↓
7. 完成！可以安装测试
```

---

## 🎯 下一步行动

1. **立即下载 Docker Desktop**
   - 下载地址：https://www.docker.com/products/docker-desktop/
   
2. **安装并启动 Docker**
   - 按照安装向导操作
   - 等待 Docker 完全启动

3. **运行打包脚本**
   - 双击 `pack_android.bat`
   - 或手动运行 Docker 命令

4. **等待打包完成**
   - 首次需要耐心（20-40 分钟）
   - 可以查看实时日志

---

**状态：** ⏳ 等待 Docker 安装  
**难度：** ⭐⭐☆☆☆（中等）  
**推荐方案：** Docker（最简单可靠）  

🎉 **安装好 Docker 后即可开始打包！**
