// global.d.ts
export {};

declare global {
  interface Window {
    ipcRenderer: {
      focusWindow: () => void;
      // Add other methods from your `contextBridge.exposeInMainWorld`
    };
    electronAPI: {
      getBackendPort: () => Promise<number>;
    };
  }
}
