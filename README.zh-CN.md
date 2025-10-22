# 考研助手（Electron + FastAPI）

[English](README.md) | 中文文档

考研助手是一款用于备考的桌面应用，集成：
- 后端：FastAPI（Python），提供 AI 能力（ModelScope、DashScope）
- 前端：React + Vite + Electron（支持 Windows 安装包）

## 功能特性
- 每日任务与学习记录，支持图表统计
- 成绩管理与趋势统计
- 作文 OCR 与 AI 优化（基于 Qwen 模型，经 ModelScope 调用）
- 通用 AI 对话（文本/图片，经 DashScope 调用）

## 代码结构
- `backend/` FastAPI 后端
- `frontend/` Electron + React 前端
- `study-helper/` 运行期数据（首次运行自动创建）
  - `data/` 持久化用户数据（按你的需求纳入版本控制）
  - `output/` 生成的报告（已被 git 忽略）
  - `temp/` 临时文件（已被 git 忽略）

## 运行前置
- Node.js 18+
- Python 3.10+
- Windows（用于打包生成安装包；其他系统可从源码运行）

## 后端开发环境配置
1. 创建并激活虚拟环境，安装依赖：
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. 创建 `.env`（可选，仅开发环境）：
   ```ini
   MODELSCOPE_API_KEY=你的_modelscope_key
   DASHSCOPE_API_KEY=你的_dashscope_key
   ```
3. 启动后端：
   ```bash
   python main.py
   ```
   服务默认运行在 `http://127.0.0.1:8000`。

## 前端开发环境配置
1. 安装依赖：
   ```bash
   cd frontend
   npm install
   ```
2. 启动开发服务器：
   ```bash
   npm run dev
   ```
3. 开发环境下通过浏览器访问 `http://localhost:5173`。打包后应用会自动启动 Electron 并拉起后端。

## 生产打包
- 后端通过 PyInstaller 冻结，打包产物经 electron-builder 的 `extraResources` 复制到应用中。
- 构建 Windows 安装包：
  ```bash
  cd frontend
  npm run build:win
  ```
  安装包输出在 `frontend/release/`。

## 运行期配置
- 在应用内的“系统设置”中保存 API 密钥，保存于应用根数据目录的 `study-helper/api_config.json`，无需重启生效。
- 典型数据根目录（已安装应用）：`D:/.../kaoyan-helper/study-helper/`，包含 `data/`、`output/`、`temp/`。

## 使用指南
- 成绩模块：增删改查成绩，查看趋势图。
- 每日任务：管理任务与学习记录，支持周/月视图图表。
- 作文模块：
  1) 添加题目（年份/类型/图片/参考范文）
  2) OCR 识别作文图片
  3) AI 优化作文；Markdown 报告保存到 `study-helper/output/essays`。
- AI 对话：自由问答；支持上传图片（DashScope）。

## 环境与敏感信息
- 不要提交 `.env` 与运行期文件；`.gitignore` 已默认忽略。
- 第三方 API 端点集中在 `backend/config.py`，如需可通过环境覆盖。

## 许可证
本项目采用 MIT License，详见 [LICENSE](LICENSE)。

## 常见问题
- 打包版未启动后端：确认 `resources/backend/study-helper-backend.exe` 存在，并查看 Electron 控制台日志。
- AI 返回占位符：在系统设置中检查 API 密钥；查看 `study-helper/backend.log`。
