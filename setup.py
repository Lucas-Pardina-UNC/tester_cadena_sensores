import sys
import subprocess
from typing import Tuple

# Required Python version
REQUIRED_PYTHON_VERSION: Tuple[int, int, int] = (3, 12, 2)

def check_python_version() -> None:
    """Verifica si la versión actual de Python cumple con el requisito mínimo."""
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        print(f"Se requiere Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}.{REQUIRED_PYTHON_VERSION[2]} o una versión más reciente.")
        print("Por favor, instale la versión requerida de Python e intente de nuevo.")
        sys.exit(1)

def install_dependencies() -> None:
    """Instala los paquetes requeridos que están listados en requirements.txt."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Error al instalar las dependencias. Asegúrese de que pip esté instalado e intente nuevamente.")
        sys.exit(1)

def main() -> None:
    # Paso 1: Verificar la versión de Python
    check_python_version()

    # Paso 2: Instalar dependencias
    print("Instalando dependencias...")
    install_dependencies()
    print("Todas las dependencias se instalaron correctamente.")

    print("¡Configuración completa! Ahora puede ejecutar su aplicación.")

if __name__ == "__main__":
    main()