# Study Helper (Electron + FastAPI)

English | [中文文档](README.zh-CN.md)

Study Helper is a desktop app for exam preparation. It bundles:
- Backend: FastAPI (Python) with AI features (ModelScope, DashScope)
- Frontend: React + Vite + Electron (Windows installer included)

## Features
- Daily tasks and study records with charts
- Score management and statistics
- Essay OCR and AI optimization (Qwen models via ModelScope)
- General AI chat (text + image via DashScope)

## Repository Structure
- `backend/` FastAPI backend
- `frontend/` Electron + React frontend
- `study-helper/` Runtime data (created at first run)
  - `data/` persisted user data (versioned per your requirement)
  - `output/` generated reports (ignored by git)
  - `temp/` temp files (ignored by git)

## Prerequisites
- Node.js 18+
- Python 3.10+
- Windows for packaged app (other OS may build from sources)

## Backend Setup (Dev)
1. Create and activate venv, install deps:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create `.env` (optional for dev):
   ```ini
   MODELSCOPE_API_KEY=your_modelscope_key
   DASHSCOPE_API_KEY=your_dashscope_key
   ```
3. Run backend:
   ```bash
   python main.py
   ```
   Backend starts at `http://127.0.0.1:8000`.

## Frontend Setup (Dev)
1. Install deps:
   ```bash
   cd frontend
   npm install
   ```
2. Run dev server:
   ```bash
   npm run dev
   ```
3. In dev, open the web app at `http://localhost:5173`. The packaged app will launch Electron and start the backend automatically.

## Production Build
- Backend is frozen (PyInstaller) and copied into Electron via electron-builder (`extraResources`).
- To build a Windows installer:
  ```bash
  cd frontend
  npm run build:win
  ```
  Output under `frontend/release/`.

## Runtime Configuration
- In the app (System Settings), save API keys. They are stored in `study-helper/api_config.json`. No restart is required.
- Data root example (installed app): `D:/.../kaoyan-helper/study-helper/` containing `data/`, `output/`, `temp/`.

## Usage Guide
- Scores: manage score entries and visualize trends.
- Daily tasks: manage tasks and study records; view weekly/monthly charts.
- Essay module:
  1) Add topic (year/type/image/reference)
  2) OCR essay image
  3) Optimize essay with AI; save Markdown report under `study-helper/output/essays`.
- AI Chat: free-form Q&A; supports images via DashScope.

## Environment and Secrets
- Do NOT commit `.env` or runtime files. Git ignores secrets by default per `.gitignore`.
- API endpoints are centralized in `backend/config.py`.

## License
This project is licensed under the MIT License - see [LICENSE](LICENSE).

## Troubleshooting
- Packaged app doesn't start backend: ensure `resources/backend/study-helper-backend.exe` exists; check Electron logs in console.
- AI returns placeholder: verify API keys in System Settings; check `study-helper/backend.log`.
