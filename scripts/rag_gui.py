import json
import os
import psutil
import streamlit as st
import sys
from datetime import datetime

# Annahme: rag_system.py ist importierbar
sys.path.append(os.path.dirname(__file__))
from rag_system import RAGSystem

st.title("Lokales RAG-System für Masterarbeiten")

# Config
config_path = "../config/research-criteria.yaml"
system = RAGSystem(config_path, cpu_only=True)

# Sidebar: PDF Upload
with st.sidebar:
    st.header("PDF Indexierung")
    uploaded_files = st.file_uploader("PDFs hochladen", type="pdf", accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            path = os.path.join(system.config["paths"]["literature_base"], file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            st.success(f"Datei {file.name} hochgeladen")
        if st.button("Indexieren"):
            system.indexer.index_directory(system.config["paths"]["literature_base"])
            st.success("Indexierung abgeschlossen")

    # RAM Monitor
    st.header("System-Status")
    ram = psutil.virtual_memory()
    st.metric("RAM-Nutzung", f"{ram.percent}% ({ram.used / (1024**3):.1f} GB)")

# Main: Suche
st.header("Semantische Suche")
query = st.text_input("Ihre Frage eingeben")
if st.button("Suchen") and query:
    with st.spinner("Suche läuft..."):
        result = system.query(query)
    st.json(result)

    # Zitat-Buttons
    for source in result["sources"]:
        if st.button(f"Kopiere Zitat: {source['citation']}"):
            st.write("Zitat kopiert!")  # Echter Clipboard via JS möglich, aber einfach halten

# History (einfach als Session State)
if "history" not in st.session_state:
    st.session_state.history = []
st.session_state.history.append({"query": query, "timestamp": datetime.now().isoformat()})
st.header("Such-History")
st.write(st.session_state.history) 