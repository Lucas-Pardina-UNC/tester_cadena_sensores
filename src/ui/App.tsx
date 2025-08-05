//import { useState } from "react";
import { BackendUrlProvider } from "./components/BackendUrlProvider";
import { AlertProvider } from "./components/CustomAlertContext";
import { ProjectProvider } from "./components/ProjectContext";
import { ChainsProvider } from "./components/ChainsContext";
import MainPanel from "./components/MainPanel";
import "./app.scss";

function App() {
  return (
    <>
      <div className="app">
        <BackendUrlProvider>
          <AlertProvider>
            <ProjectProvider>
              <ChainsProvider>
                <header className="app__header">
                  <h1>Tester - Sensores EML</h1>
                </header>
                <main className="app__main">
                  <MainPanel />
                </main>
              </ChainsProvider>
            </ProjectProvider>
          </AlertProvider>
        </BackendUrlProvider>
      </div>
    </>
  );
}

export default App;
