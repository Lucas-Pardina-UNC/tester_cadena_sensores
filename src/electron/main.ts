// @ts-ignore
import { app, BrowserWindow, ipcMain } from 'electron';
import { spawn } from 'child_process';
import path from 'path';
import { isDev } from './util.js';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import net from 'net';

const __dirname = dirname(fileURLToPath(import.meta.url));

let mainWindow: BrowserWindow | null = null;
let backendProcess: any = null;

function getAvailablePort(startingPort: number): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(startingPort, () => {
      const port = (server.address() as net.AddressInfo).port;
      server.close(() => resolve(port));
    });
  });
}

function createWindow() {
  const preloadPath = path.resolve(__dirname, 'preload.js');

  console.log('Using preload script at:', preloadPath);
  
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      contextIsolation: true,
      preload: preloadPath, // Use the correct path to preload.js
      //preload: path.join('preload.js'), // Adjust if needed
      //preload: path.join(__dirname, '..', 'dist-electron', 'preload.js')
      //preload: path.join(__dirname, 'preload.js'), // Adjust if needed
      // Use the built preload.js from dist-electron
      //preload: path.join(__dirname, '..', '..', 'dist-electron', 'preload.js'),
    },
  });

  if (isDev()) {
    mainWindow.loadURL('http://localhost:5123'); // Vite dev server
  } else {
    mainWindow.loadFile(path.join(app.getAppPath(), 'dist-react/index.html')); // Production build
  }
}

function startBackend(port: number) {
  const scriptPath = isDev()
    ? path.join(__dirname, '..', 'src', 'electron', 'backend', 'app.py')
    : path.join(process.resourcesPath, 'backend', 'app.py');

  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';

  console.log(`Starting backend from: ${scriptPath} on port ${port}`);
  backendProcess = spawn(pythonExecutable, [scriptPath, port.toString()]);

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

let backendPort: number;

// App lifecycle
app.whenReady().then(async () => {
  console.log('App is ready');
  backendPort = await getAvailablePort(5000);
  console.log(`Using backend port: ${backendPort}`);
  
  // Register IPC handler
  ipcMain.handle('get-backend-port', async () => {
    return backendPort;
  });
  
  startBackend(backendPort);
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('before-quit', () => {
  stopBackend();
});
