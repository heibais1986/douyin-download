# GitHub Actions 自动编译

这个workflow使用Nuitka将Python代码编译成机器码，获得终极的反编译保护。

## 🚀 触发编译

### 方法1：创建标签触发
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 方法2：手动触发
1. 进入GitHub仓库的Actions标签页
2. 点击"Build Release" workflow
3. 点击"Run workflow"按钮
4. 输入版本号（如：v1.0.0）

## 📦 编译产物

编译完成后，会在以下位置生成：

### Windows版本
- `抖音监控器.exe` - 生产版本（无控制台）
- `抖音监控器_调试版.exe` - 调试版本（带控制台）
- `checksums.txt` - SHA256校验和

### Linux版本
- `douyin-monitor-linux` - Linux可执行文件

## 🛡️ 保护特性

- ✅ **完全无法反编译** - 编译成原生机器码
- ✅ **商业级保护** - 适合商业发布
- ✅ **性能提升** - 运行速度比Python快2-5倍
- ✅ **跨平台支持** - 支持Windows和Linux

## 📋 使用步骤

1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "Release version 1.0.0"
   git push
   ```

2. **创建Release标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **等待编译完成**
   - Actions会自动运行编译
   - 编译需要15-30分钟

4. **下载编译产物**
   - 进入Actions页面
   - 下载artifacts中的文件

## 🔧 故障排除

### 编译失败
- 检查requirements.txt中的依赖
- 确保所有必要的文件都已提交
- 查看Actions日志了解具体错误

### 文件缺失
- 确保aria2c.exe存在于项目根目录
- 检查lib/js目录中的JavaScript文件

### 性能问题
- Nuitka编译需要大量内存和时间
- 考虑使用GitHub的付费运行器获得更好性能