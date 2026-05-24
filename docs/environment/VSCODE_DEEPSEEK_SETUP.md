# Integración VS Code + DeepSeek para Proyecto Antigravity

## Estado: ✅ Funcionando

**Fecha:** [Añade la fecha actual]

### Herramientas configuradas
- **Editor principal:** VS Code
- **IA asistente:** DeepSeek (vía API)
- **Extensión:** Continue
- **IDE secundario:** Antigravity (modelos gratuitos Gemini/Claude)

### Flujo de trabajo recomendado

| Tarea | Herramienta |
|-------|-------------|
| Escribir/refactorizar código | VS Code + DeepSeek |
| Depuración rápida | VS Code + DeepSeek |
| Conversaciones largas con historial | Antigravity |
| Comparar con otro modelo (Gemini/Claude) | Antigravity |
| Analizar múltiples archivos | VS Code + DeepSeek |

### Carpetas del proyecto
- Principal: `C:\Users\34628\Downloads\Proyecto_antigravity`
- Curso: `C:\Users\34628\Downloads\Curso_Antigravity`
- Material: `C:\Users\34628\Downloads\Material_clases`

### Configuración de Continue en VS Code
```yaml
models:
  - name: DeepSeek
    provider: openai
    model: deepseek-chat
    apiKey: [TU_API_KEY]
    apiBase: https://api.deepseek.com/v1