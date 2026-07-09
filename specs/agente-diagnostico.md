# Agente de Diagnóstico de Confía Process

**Como:** cliente potencial que tiene un problema en sus procesos pero no sabe exactamente qué es

**Quiero:** describir mi problema a un agente que me haga preguntas guiadas

**Para:** obtener un diagnóstico inicial claro de qué está fallando en mis procesos y un primer acercamiento de solución

## Criterios de aceptación

- El agente saluda al usuario y le pregunta cuál es su problema
- Hace máximo 3 preguntas antes de diagnosticar — preguntas simples, una por vez
- Si el usuario no sabe explicar bien su problema, ofrece un caso puntual resonante como ejemplo
- El diagnóstico final incluye una sugerencia concreta de por dónde arrancar
- La conversación cierra invitando al usuario a conectar con Confía Process para una entrevista de profundidad

## Casos límite

- Si el usuario escribe algo fuera de procesos — agotar instancias de acompañamiento
- Si el usuario es agresivo o sin sentido — ignorar la agresividad y guiarlo pacientemente
