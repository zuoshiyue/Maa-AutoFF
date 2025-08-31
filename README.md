<!-- markdownlint-disable MD033 MD041 -->
<div align="center">

# AutoFF

《最终幻想14：水晶世界》小助手
由 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 强力驱动！  

</div>

## 功能列表
- 自动采集
- 自动钓鱼
- 金蝶小游戏

## 使用说明
- [新手上路](https://kdocs.cn/l/cr7ysRpwQO6s)(**使用前必看**)

## 开发相关
### 技术栈
- 前端技术
  - javaScript
  - Vue 3 (v3.3.7)
  - Pinia (v2.1.7)
  - Vite (v4.5.0)
  - SASS (v1.69.5)
  - Vue Router (v4.2.5)
  - Element Plus (v2.4.1)
- 后端技术
  - Python (3.10.x)
  - pywebview (v5.4)
  - opencv-python (v4.5.5.64)
  - numpy (v1.24.2)
  - rapidocr (v3.2.0)
- 打包
  - npm
  - Nuitka (v2.4.7)
  - npm
  - Nuitka

### 运行方法
- `git clone https://github.com/Jai-wei/Maa-AutoFF.git`
- `pip install requirements.txt`
- `cd frontend && npm install`
- `npm run build`
- `python AutoFF.py`

### 自动打包生成exe应用程序
本项目使用GitHub Actions自动打包生成exe应用程序。每次推送到`main`分支或创建拉取请求时，都会自动触发打包流程。

您也可以手动触发打包流程：
1. 访问项目的Actions页面
2. 选择"Build AutoFF Executable"工作流
3. 点击"Run workflow"按钮

打包生成的exe文件可以通过以下方式获取：
1. 在Actions页面找到对应的workflow run
2. 在Artifacts部分下载"AutoFF-executable"

## 鸣谢
- [MaaFramework](https://github.com/MaaXYZ/MaaFramework)
- [rapidocr](https://github.com/RapidAI/RapidOCR)
- [msc](https://github.com/NakanoSanku/msc)
- [mtc](https://github.com/NakanoSanku/mtc)

## 更新日志
- 2025-09-03: 在Nuitka打包脚本中添加exe文件存在性检查，以帮助诊断打包问题
- 2025-09-02: 修复Nuitka打包脚本中输出文件路径显示不准确的问题
- 2025-09-01: 修复Nuitka打包脚本中的Unicode编码错误，确保在Windows环境下能正确打印中文字符
- 2025-08-31: 优化采集自动切换职业；修复GitHub Actions工作流，更新到v4版本以解决弃用问题
- 2025-04-26: 删除print语句，优化代码
- 2025-04-25: 支持mumu5模拟器
- 2025-04-24: 初始版本上传

## Join us
- AutoFF 交流群 QQ 群：728747469 - **禁止RMT、工作室相关**
- AutoFF 开发群 QQ 群：222082281 - **非开发者勿加**
- MaaFramework 开发交流 QQ 群: 595990173 - **非开发者勿加**
