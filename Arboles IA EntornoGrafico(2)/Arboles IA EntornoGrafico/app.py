import os
import json
import streamlit as st

# Configuración de página con estética moderna para Música
st.set_page_config(
    page_title="Sistema de Recomendación Musical - Árboles",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para una presentación premium
st.markdown("""
<style>
    .main-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #EC4899, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .breadcrumb-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.75rem 1.2rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
    }
    @media (prefers-color-scheme: dark) {
        .breadcrumb-box {
            background-color: #1E293B;
            border-color: #334155;
            color: #F1F5F9;
        }
    }
    .breadcrumb-item {
        color: #EC4899;
        font-weight: 600;
    }
    .breadcrumb-sep {
        color: #94A3B8;
        font-weight: 400;
    }
    .question-card {
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    @media (prefers-color-scheme: dark) {
        .question-card {
            background: #0F172A;
            border-color: #1E293B;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
    }
    .level-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #FCE7F3;
        color: #DB2777;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    @media (prefers-color-scheme: dark) {
        .level-badge {
            background-color: #831843;
            color: #FBCFE8;
        }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Funciones para manejo de datos del árbol de música
# -------------------------------------------------------------
JSON_FILE = "EstructurasDeDatos.json"  # Asegúrate de guardar tu JSON musical con este nombre o cambia el nombre aquí

def cargar_arbol(ruta_archivo=JSON_FILE):
    """Carga el árbol de decisiones musicales desde el archivo JSON de forma segura."""
    if not os.path.exists(ruta_archivo):
        return None, f"No se encontró el archivo '{ruta_archivo}'."
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if not isinstance(datos, dict) or "valor" not in datos:
                return None, "El formato del JSON debe contener al menos un nodo raíz con la clave 'valor'."
            return datos, None
    except json.JSONDecodeError as e:
        return None, f"Error al decodificar JSON: {e}"
    except Exception as e:
        return None, f"Error al leer archivo: {e}"

# -------------------------------------------------------------
# Inicialización del estado de la sesión
# -------------------------------------------------------------
if "arbol" not in st.session_state or st.session_state.arbol is None:
    arbol, error = cargar_arbol()
    st.session_state.arbol = arbol
    st.session_state.error_arbol = error
    st.session_state.historial = [arbol] if arbol else []
    st.session_state.explicacion_ia = None

def reiniciar_navegacion():
    """Reinicia la navegación al nodo raíz."""
    if st.session_state.arbol:
        st.session_state.historial = [st.session_state.arbol]
    else:
        st.session_state.historial = []
    st.session_state.explicacion_ia = None

def recargar_archivo():
    """Recarga el archivo JSON desde el disco."""
    arbol, error = cargar_arbol()
    st.session_state.arbol = arbol
    st.session_state.error_arbol = error
    reiniciar_navegacion()

# -------------------------------------------------------------
# Barra lateral (Configuración y utilidades)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Configuración de IA")
    
    modelo_ollama = st.text_input(
        "Modelo de Ollama:",
        value="llama3.2:1b",
        help="Nombre del modelo descargado localmente"
    )
    
    temperatura = st.slider(
        "Creatividad (Temperatura):",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1
    )
    
    st.markdown("---")
    st.markdown("### 📂 Gestión del Árbol")
    if st.button("🔄 Recargar JSON", use_container_width=True):
        recargar_archivo()
        st.toast("Árbol recargado correctamente", icon="✅")
        st.rerun()

    if st.button("⏪ Reiniciar Recorrido", use_container_width=True):
        reiniciar_navegacion()
        st.rerun()

    with st.expander("👀 Ver estructura del JSON activo"):
        if st.session_state.arbol:
            st.json(st.session_state.arbol)
        else:
            st.warning("No hay árbol cargado.")

# -------------------------------------------------------------
# Cabecera principal
# -------------------------------------------------------------
st.markdown('<div class="main-title">🎵 Sistema de Recomendación Musical con IA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Exploración jerárquica de géneros, estilos y análisis de perfiles sonoros mediante Ollama</div>', unsafe_allow_html=True)

if st.session_state.error_arbol:
    st.error(st.session_state.error_arbol)
    st.stop()

historial = st.session_state.historial
if not historial:
    st.session_state.historial = [st.session_state.arbol]
    historial = st.session_state.historial

nodo_actual = historial[-1]
camino_titulos = [nodo["valor"] for nodo in historial]
nivel_actual = len(historial)
hijos = nodo_actual.get("hijos", [])

# Miga de pan / Breadcrumb Dinámica
breadcrumb_html = '<div class="breadcrumb-box"><span>📍 <b>Ruta Musical:</b></span> '
for idx, tit in enumerate(camino_titulos):
    if idx > 0:
        breadcrumb_html += '<span class="breadcrumb-sep">➔</span> '
    breadcrumb_html += f'<span class="breadcrumb-item">{tit}</span> '
breadcrumb_html += '</div>'
st.markdown(breadcrumb_html, unsafe_allow_html=True)

# Lógica de navegación del Árbol de Decisiones
if hijos:
    st.session_state.explicacion_ia = None
    
   # Lógica limpia para mostrar el texto del nodo actual sin duplicar
    if "pregunta" in nodo_actual:
        pregunta_texto = nodo_actual["pregunta"]
    elif nivel_actual == 1:
        pregunta_texto = nodo_actual["valor"]  # Muestra exactamente lo que dice el JSON raíz
    else:
        pregunta_texto = f"Dentro de **{nodo_actual['valor']}**, selecciona un subgénero:"

    st.markdown(f"""
    <div class="question-card">
        <span class="level-badge">Nivel {nivel_actual}</span>
        <h3 style="margin-top:0.3rem; margin-bottom:0.5rem; font-weight:600;">{pregunta_texto}</h3>
        <p style="color:#64748B; font-size:0.9rem; margin-bottom:0;">Selecciona una opción para continuar con la recomendación:</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(min(len(hijos), 3))
    for i, hijo in enumerate(hijos):
        col_act = cols[i % len(cols)]
        etiqueta = hijo.get("valor", f"Opción {i+1}")
        icono = "🎸" if nivel_actual == 1 else ("🎧" if hijo.get("hijos") else "🎶")
        
        if col_act.button(f"{icono} {etiqueta}", key=f"btn_hijo_{nivel_actual}_{i}", use_container_width=True):
            st.session_state.historial.append(hijo)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col_nav1, col_nav2, _ = st.columns([1, 1, 2])
    with col_nav1:
        if nivel_actual > 1:
            if st.button("⬅️ Paso anterior", use_container_width=True):
                st.session_state.historial.pop()
                st.rerun()
    with col_nav2:
        if nivel_actual > 1:
            if st.button("🔄 Reiniciar selección", use_container_width=True):
                reiniciar_navegacion()
                st.rerun()

else:
    # Nivel final (Nodo Hoja) -> Mostrar artistas directamente
    artistas = nodo_actual.get("artistas", [])
    
    st.markdown(f"""
    <div class="question-card" style="border-left: 5px solid #EC4899;">
        <span class="level-badge" style="background-color: #FCE7F3; color: #DB2777;">Resultado Final</span>
        <h3 style="margin-top: 0.3rem; margin-bottom: 0.5rem;">Estilo: <b>{nodo_actual['valor']}</b></h3>
        <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 0;">
            Artistas clave recomendados para este género:
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back1, col_back2, _ = st.columns([1, 1, 2])
    with col_back1:
        if st.button("⬅️ Volver atrás", use_container_width=True):
            st.session_state.historial.pop()
            st.rerun()
    with col_back2:
        if st.button("🔄 Nueva búsqueda", use_container_width=True):
            reiniciar_navegacion()
            st.rerun()

    st.markdown("---")
    st.subheader("🎧 Recomendación y Análisis del Perfil Sonoro (Ollama)")

    prompt = (
        f"Analiza el perfil musical resultante: '{nodo_actual['valor']}'. "
        f"La ruta de selecciones en el árbol de decisiones es: {' > '.join(camino_titulos)}. "
        "Proporciona: 1) Una descripción detallada del género o estilo sonoro, "
        "2) Artistas clave o referentes históricos recomendados para escuchar, "
        "y 3) Sugerencias de configuración de audio (ecualización) o el contexto ideal de escucha."
    )

    try:
        import ollama

        if st.session_state.explicacion_ia is None:
            with st.spinner(f"Generando recomendación musical con {modelo_ollama}..."):
                stream = ollama.chat(
                    model=modelo_ollama,
                    messages=[
                        {"role": "system", "content": "Eres un crítico y experto musical profesional especializado en géneros, producción de sonido y recomendación de perfiles musicales. Responde de forma amena, estructurada y pedagógica."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": temperatura},
                    stream=True
                )
                
                def generar_stream():
                    for chunk in stream:
                        yield chunk['message']['content']

                respuesta_completa = st.write_stream(generar_stream)
                st.session_state.explicacion_ia = respuesta_completa
        else:
            st.markdown(st.session_state.explicacion_ia)
            
            if st.button("🔄 Regenerar recomendación"):
                st.session_state.explicacion_ia = None
                st.rerun()

    except Exception as e:
        error_msg = str(e)
        st.error("⚠️ No se pudo comunicar con el servidor local de Ollama para la recomendación.")
        
        col_err1, col_err2 = st.columns([1, 1])
        with col_err1:
            if st.button("🔄 Reintentar conexión", use_container_width=True):
                st.session_state.explicacion_ia = None
                st.rerun()
        with col_err2:
            if st.button("💡 Ver recomendación de prueba (Offline)", use_container_width=True):
                st.session_state.explicacion_ia = (
                    f"### 🎶 Recomendación Musical para: {nodo_actual['valor']}\n\n"
                    f"* **Ruta seleccionada**: `{' > '.join(camino_titulos)}`\n"
                    f"* **Descripción**: Este perfil refleja una selección detallada de preferencias acústicas o electrónicas orientadas a una experiencia inmersiva.\n"
                    f"* **Artistas sugeridos**: Referentes destacados del género a nivel internacional.\n"
                    f"* **Nota**: Asegúrate de tener activo el servicio de Ollama (`ollama serve`) para obtener respuestas dinámicas en tiempo real."
                )
                st.rerun()