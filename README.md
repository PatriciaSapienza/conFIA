# DiagnosIA

Agente de diagnóstico de procesos para Confía Process. Aplicación web en
Python/Flask con una interfaz de chat que usa la API de Anthropic (Claude)
para guiar al usuario hacia un primer diagnóstico de sus procesos.

Ver especificación en [specs/agente-diagnostico.md](specs/agente-diagnostico.md).

## Requisitos

- Python 3.9+
- Una API key de Anthropic

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Definí tu API key como variable de entorno antes de correr la app:

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "tu-api-key"

# macOS / Linux
export ANTHROPIC_API_KEY="tu-api-key"
```

## Ejecutar

```bash
python app.py
```

Luego abrí [http://localhost:5000](http://localhost:5000) en el navegador.

## Estructura

```
DiagnosIA/
  app.py               # Backend Flask + integración con la API de Anthropic
  templates/index.html  # Interfaz de chat
  static/style.css      # Estilos (azul marino #003A70 / celeste #5BB8F5)
  static/chat.js         # Lógica del chat (fetch al backend)
  requirements.txt
  specs/agente-diagnostico.md
```
