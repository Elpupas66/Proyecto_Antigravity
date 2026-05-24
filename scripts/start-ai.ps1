Write-Host ""
Write-Host "🚀 Iniciando laboratorio IA..." -ForegroundColor Green
Write-Host ""

Write-Host "Comprobando Ollama..."
ollama -v

Write-Host ""
Write-Host "Modelos instalados:"
ollama list

Write-Host ""
Write-Host "Lanzando Claude Code con Qwen..."
ollama launch claude --model qwen3.5:4b