//import { useState } from "react";
import Projects from "./components/Projects";
import { ProjectProvider } from "./components/ProjectContext";
import { ChainsProvider } from "./components/ChainsContext";
import ChainsList from "./components/ChainsList";
import MainPanel from "./components/MainPanel";
import "./app.scss";

function App() {
  return (
    <>
      <ProjectProvider>
        <ChainsProvider>
          <h1>Tester - Sensores EML </h1>
          <MainPanel />
          {/* <Projects />
          <ChainsList /> */}
        </ChainsProvider>
      </ProjectProvider>
    </>
  );
}

export default App;
