// @ts-ignore
import { app, BrowserWindow, ipcMain } from 'electron';
import { spawn } from 'child_process';
import path from 'path';
import { isDev } from './util.js';
import { dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

let mainWindow: BrowserWindow | null = null;
let backendProcess: any = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'), // Adjust if needed
    },
  });

  if (isDev()) {
    mainWindow.loadURL('http://localhost:5123'); // Vite dev server
  } else {
    mainWindow.loadFile(path.join(app.getAppPath(), 'dist-react/index.html')); // Production build
  }
}

function startBackend() {
  // Adjust path based on environment
  const scriptPath = isDev()
    ? path.join(__dirname, '..', 'src', 'electron', 'backend', 'app.py')
    : path.join(process.resourcesPath, 'backend', 'app.py'); // You'll need to copy backend to `resources` in build

  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';

  console.log(`Starting backend from: ${scriptPath}`);
  backendProcess = spawn(pythonExecutable, [scriptPath]);

  backendProcess.stdout.on('data', (data: Buffer) => {
    console.log(`[Backend]: ${data}`);
  });

  backendProcess.stderr.on('data', (data: Buffer) => {
    console.error(`[Backend ERROR]: ${data}`);
  });

  backendProcess.on('exit', (code: Buffer) => {
    console.log(`Backend process exited with code ${code}`);
  });
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    console.log('Backend process terminated');
  }
}

// App lifecycle
app.whenReady().then(() => {
  console.log('App is ready');
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('before-quit', () => {
  stopBackend();
});
