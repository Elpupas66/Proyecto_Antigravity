Entorno de IA Local con Antigravity + VS Code + Ollama + Claude Code
Objetivo

Configurar un entorno de desarrollo con IA 100 % local usando:

Antigravity
Visual Studio Code
Ollama
Claude Code
modelos locales de lenguaje.
1. Software instalado
VS Code

Comprobación:

code --version
Ollama

Comprobación:

ollama -v

Ver modelos instalados:

ollama list
Git (Git Bash)

Comprobación:

where.exe git

Ruta detectada:

C:\Users\34628\scoop\apps\git\current\cmd\git.exe

Ruta de bash:

C:\Users\34628\scoop\apps\git\current\bin\bash.exe

Comprobación:

Test-Path "C:\Users\34628\scoop\apps\git\current\bin\bash.exe"

Resultado esperado:

True
2. Modelos instalados en Ollama

Listado:

ollama list

Modelos actuales:

Qwen 3.5 4B

Qwen 3.5 4B

Gemma 4 e2b

Gemma 4

Instalación de Gemma:

ollama run gemma4:e2b
3. Conectar Claude Code con Ollama

Claude Code usa la API compatible con Anthropic de Ollama.

Variables necesarias:

$env:ANTHROPIC_AUTH_TOKEN="ollama"
$env:ANTHROPIC_BASE_URL="http://localhost:11434"
4. Problema encontrado

Claude Code no encontraba Git Bash.

Error:

Claude Code was unable to find CLAUDE_CODE_GIT_BASH_PATH

Solución:

$env:CLAUDE_CODE_GIT_BASH_PATH="C:\Users\34628\scoop\apps\git\current\bin\bash.exe"
5. Lanzar Claude Code con modelo local

Desde la terminal del proyecto:

ollama launch claude --model qwen3.5:4b

Esto conecta Claude Code con Ollama.

6. Estructura del proyecto
Proyecto-claude
│
├─ .claude
│  └─ agents
│     └─ trading-analyst.md
│
├─ dashboard_mt5.html
├─ historialTradingMT4.html
└─ Para recordar.txt
7. Flujo de trabajo

1️⃣ Abrir Antigravity
2️⃣ Abrir proyecto
3️⃣ Abrir terminal
4️⃣ Ejecutar:

ollama launch claude --model qwen3.5:4b

Claude Code puede:

leer archivos del proyecto
modificar código
crear scripts
automatizar tareas.
8. Cómo usar modelos directamente

Ejecutar modelo:

ollama run gemma4:e2b

Salir del modelo:

/bye
9. Cómo interrumpir respuestas
Ctrl + C
10. Ver modelo activo
ollama ps
11. Uso recomendado de modelos
Modelo	Uso
qwen3.5:4b	coding general
gemma4:e2b	razonamiento
qwen3.5:0.8b	tareas rápidas
❓ Pregunta 1
¿Si apago el ordenador se pierde la configuración?

No.

Todo queda guardado en:

instalación de programas
modelos descargados
archivos del proyecto.

Lo único que se pierde son variables temporales de PowerShell.

Por eso cada sesión se debe ejecutar:

$env:CLAUDE_CODE_GIT_BASH_PATH="C:\Users\34628\scoop\apps\git\current\bin\bash.exe"
ollama launch claude --model qwen3.5:4b

Luego podemos hacer esto permanente.

❓ Pregunta 2
¿Cómo pasar esta configuración a otro ordenador?
1. Instalar software

Instalar:

Antigravity
VS Code
Ollama
Git
2. Copiar proyecto

Copiar carpeta:

Proyecto-Claude
3. Instalar modelos

En el nuevo equipo ejecutar:

ollama run qwen3.5:4b
ollama run gemma4:e2b
4. Configurar Claude Code
$env:CLAUDE_CODE_GIT_BASH_PATH="ruta_a_git_bash"
ollama launch claude --model qwen3.5:4b
Próximos pasos

Crear laboratorio IA:

AI-LAB
├─ trading
├─ automatizaciones
├─ scraping
├─ proyectos-clientes
└─ experimentos
Conclusión

El portátil ahora funciona como:

Antigravity
   ↓
VS Code
   ↓
Claude Code
   ↓
Ollama
   ↓
modelos locales

Sistema 100 % local y privado.

Sugerencia

Te recomiendo guardar este archivo en:

Proyecto-claude/docs/SETUP_IA_LOCAL.md