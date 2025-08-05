import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";
import { execSync } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Root and Paths
const root = path.resolve(__dirname, "..");
const scriptsDir = path.join(root, "scripts");
const distDir = path.join(root, "dist");

const requirementsPath = path.join(scriptsDir, "requirements.txt");
const ps1TemplatePath = path.join(scriptsDir, "python_dep_installer_template.ps1");
const outputPs1Path = path.join(scriptsDir, "python_dep_installer_generated.ps1");
const outputExePath = path.join(distDir, "PythonDepInstaller.exe");

const checkScriptPath = path.join(scriptsDir, "python_check_installer.ps1");
const checkExePath = path.join(distDir, "PythonCheckInstaller.exe");

// Make sure dist folder exists
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// --- 1. Read requirements.txt ---
let requirementsContent = "";
try {
  requirementsContent = fs.readFileSync(requirementsPath, "utf-8");
} catch (e) {
  console.error("❌ Could not read requirements.txt:", e);
  process.exit(1);
}

// --- 2. Format dependencies array for PowerShell ---
const deps = requirementsContent
  .split(/\r?\n/)
  .filter((line) => line.trim() !== "" && !line.trim().startsWith("#"))
  .map((line) => `    "${line.trim()}"`);

const packagesBlock = `# List of dependencies to be installed
$packages = @(
${deps.join(",\n")}
)`;

// --- 3. Inject into template ---
let ps1Template = "";
try {
  ps1Template = fs.readFileSync(ps1TemplatePath, "utf-8");
} catch (e) {
  console.error("❌ Could not read PS1 template:", e);
  process.exit(1);
}

const ps1Final = ps1Template.replace("__PACKAGES__", packagesBlock);

// --- 4. Write generated PowerShell script ---
fs.writeFileSync(outputPs1Path, ps1Final);
console.log("✅ PowerShell installer script generated at:", outputPs1Path);

// --- 5. Function to convert a .ps1 to .exe ---
function convertPs1ToExe(inputPs1, outputExe) {
  if (!fs.existsSync(inputPs1)) {
    console.error("❌ PS1 script not found:", inputPs1);
    process.exit(1);
  }

  try {
    execSync(
      `powershell -ExecutionPolicy Bypass -Command "Invoke-ps2exe '${inputPs1}' '${outputExe}'"`,
      { stdio: "inherit" }
    );
    console.log(`✅ .exe built at: ${outputExe}`);
  } catch (err) {
    console.error("❌ Error building .exe for", inputPs1, ":", err);
  }
}

// --- 6. Convert both scripts to .exe ---
convertPs1ToExe(outputPs1Path, outputExePath);
convertPs1ToExe(checkScriptPath, checkExePath);
