import { app, BrowserWindow } from 'electron'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { spawn, ChildProcess } from 'node:child_process'
import fs from 'node:fs'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 后端进程管理
let backendProcess: ChildProcess | null = null

// The built directory structure
//
// ├─┬─┬ dist
// │ │ └── index.html
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js
// │ │ └── preload.mjs
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 Use ['ENV_NAME'] avoid vite:define plugin - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null

// 启动后端服务
function startBackend() {
  const isDev = VITE_DEV_SERVER_URL !== undefined
  
  if (isDev) {
    // 开发环境：假设后端已手动启动
    console.log('Development mode: Backend should be started manually')
    return
  }

  // 生产环境：启动打包的后端
  try {
    const backendPath = path.join(process.resourcesPath, 'backend', 'study-helper-backend.exe')
    console.log('Starting backend from:', backendPath)
    
    if (!fs.existsSync(backendPath)) {
      console.error('Backend executable not found at:', backendPath)
      return
    }
    
    // 设置数据根目录
    // process.resourcesPath: 安装目录/resources
    // 安装根目录: 安装目录/resources/.. = 安装目录
    const appRoot = path.dirname(process.resourcesPath)  // 更可靠的方法获取安装根目录
    const dataRoot = path.join(appRoot, 'study-helper')
    
    console.log('Resources path:', process.resourcesPath)
    console.log('App root:', appRoot)
    console.log('Data root:', dataRoot)
    
    // 确保数据目录存在
    if (!fs.existsSync(dataRoot)) {
      fs.mkdirSync(dataRoot, { recursive: true })
      console.log('Created data root directory')
    }
    
    backendProcess = spawn(backendPath, [], {
      detached: false,
      stdio: ['ignore', 'pipe', 'pipe'], // 捕获输出和错误
      cwd: path.join(process.resourcesPath, 'backend'),
      env: {
        ...process.env,
        STUDY_HELPER_DATA_ROOT: dataRoot  // 通过环境变量传递数据根目录
      }
    })

    // 监听后端输出
    backendProcess.stdout?.on('data', (data) => {
      console.log('[Backend]', data.toString())
    })

    backendProcess.stderr?.on('data', (data) => {
      console.error('[Backend Error]', data.toString())
    })

    backendProcess.on('error', (err) => {
      console.error('Failed to start backend:', err)
    })

    backendProcess.on('exit', (code) => {
      console.log('Backend process exited with code:', code)
    })

    console.log('Backend started successfully, PID:', backendProcess.pid)
  } catch (err) {
    console.error('Error starting backend:', err)
  }
}

// 关闭后端服务
function stopBackend() {
  if (backendProcess) {
    console.log('Stopping backend...')
    try {
      backendProcess.kill()
      backendProcess = null
      console.log('Backend stopped')
    } catch (err) {
      console.error('Error stopping backend:', err)
    }
  }
}

function createWindow() {
  win = new BrowserWindow({
    title: 'Study Helper',
    width: 1200,
    height: 800,
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),
    },
  })

  // 打开开发者工具（调试用，生产环境可以注释掉）
  // if (!VITE_DEV_SERVER_URL) {
  //   win.webContents.openDevTools()
  // }

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL)
  } else {
    win.loadFile(path.join(RENDERER_DIST, 'index.html'))
  }
}

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

app.whenReady().then(() => {
  startBackend()
  // 等待后端启动（增加到 3 秒）
  setTimeout(() => {
    createWindow()
  }, 3000)
})

// 程序退出前清理
app.on('before-quit', () => {
  stopBackend()
})
