import { fileURLToPath } from "url";
import path from "path";
import { execSync } from "child_process";
import fs from "fs";

// ✅ Define __dirname manually
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const root = path.resolve(__dirname, "..");
const nsiTemplatePath = path.join(root, "scripts", "python_check.nsi");
const requirementsPath = path.join(root, "scripts", "requirements.txt");
const tempNsiPath = path.join(root, "scripts", "script.generated.nsi");
const outputInstallerPath = path.join(root, "dist", "PythonDepInstaller.exe");

// Read requirements.txt
let requirementsContent = "";
try {
  requirementsContent = fs.readFileSync(requirementsPath, "utf-8");
} catch (e) {
  console.error("❌ Could not read requirements.txt:", e);
  process.exit(1);
}

// Convert requirements.txt lines into pip install commands
const pipCommands = requirementsContent
  .split(/\r?\n/)
  .filter((line) => line.trim() !== "" && !line.trim().startsWith("#"))
  .map((dep) => `nsExec::ExecToStack 'pip install ${dep}'`)
  .join("\n        ");

// Read NSI template and inject pip commands
let nsiContent = fs.readFileSync(nsiTemplatePath, "utf-8");
nsiContent = nsiContent.replace("__REQUIREMENTS__", pipCommands);

// Write the modified NSI to a temp file
fs.writeFileSync(tempNsiPath, nsiContent);

console.log("🛠️ Building NSIS installer...");
execSync(`makensis /DOUTPUT_PATH="${outputInstallerPath}" "${tempNsiPath}"`, {
  stdio: "inherit",
});

console.log("✅ Installer created at:", outputInstallerPath);
