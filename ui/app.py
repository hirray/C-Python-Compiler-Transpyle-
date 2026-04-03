import sys
import os
import time
import pandas as pd
import streamlit as st

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
import phases.lexer
import phases.parser
import phases.semantic
import phases.intermediate
import phases.optimizer
import phases.generator

# Force hot-reload modules in development so Streamlit catches live changes!
importlib.reload(phases.lexer)
importlib.reload(phases.parser)
importlib.reload(phases.semantic)
importlib.reload(phases.intermediate)
importlib.reload(phases.optimizer)
importlib.reload(phases.generator)

from phases.lexer import lexical_analysis
from phases.parser import syntax_analysis
from phases.semantic import semantic_analysis
from phases.intermediate import generate_intermediate
from phases.optimizer import optimize_code
from phases.generator import generate_python_code

# =========================================
# 🔹 PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="C to Python | Premium Compiler",
    layout="wide",
    page_icon="💻",
    initial_sidebar_state="collapsed"
)

# =========================================
# 🔹 PREMIUM CSS
# =========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&display=swap');
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1c24, #0e1117);
        font-family: 'Inter', sans-serif;
    }

    .header-container {
        text-align: center;
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .main-title {
        background: linear-gradient(90deg, #00c3ff, #ffff1c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    .sub-title {
        color: #888;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .stTextArea textarea {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: #e0e0e0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #00c3ff 0%, #0072ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 195, 255, 0.3) !important;
    }

    /* Phase Table Styling */
    .phase-label {
        font-size: 0.85rem;
        font-weight: bold;
        color: #00c3ff;
        margin-bottom: 5px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =========================================
# 🔹 HELPER: GENERATE FULL REPORT
# =========================================
def generate_full_report():
    report = []
    report.append("=========================================")
    report.append("⌬ COMPILER ENGINE - FULL ACADEMIC REPORT")
    report.append("=========================================\n")
    
    if "phases" in st.session_state:
        p = st.session_state.phases
        
        report.append("◈ PHASE 1: TOKENS")
        for t in p.get("tokens", []):
            report.append(str(t))
        
        report.append("\n◈ PHASE 2: INITIAL SYMBOL TABLE")
        for k, v in p.get("symbol_table_init", {}).items():
            report.append(f"{k}: {v}")
            
        report.append("\n◈ PHASE 3: SYNTAX (PARSED OUTPUT)")
        for item in p.get("parsed", []):
            report.append(str(item))
            
        report.append("\n◈ PHASE 4: SEMANTIC ANALYSIS")
        errors = p.get("errors", [])
        report.append(f"Errors Found: {len(errors)}")
        for e in errors:
            report.append(e)
            
        report.append("\n◈ PHASE 5: INTERMEDIATE CODE (IR)")
        for line in p.get("ir", []):
            report.append(line)
            
        report.append("\n◈ PHASE 6: OPTIMIZED IR")
        for line in p.get("optimized", []):
            report.append(line)
            
        report.append("\n◈ FINAL RESULT: PYTHON")
        report.append(st.session_state.get("py_output", ""))
        
    return "\n".join(report)

# =========================================
# 🔹 HEADER
# =========================================
st.markdown("""
    <div class="header-container">
        <div class="sub-title">⌬ Modular Integrated Engine</div>
        <div class="main-title">C ❯ Python Compiler</div>
    </div>
""", unsafe_allow_html=True)

# Initialize Session State safely
if "c_source" not in st.session_state:
    st.session_state.c_source = """#include <stdio.h>

int main() {
    int n = 5;
    for(int i = 0; i < n; i++) {
        printf("Hello World %d\\n", i);
    }
    return 0;
}"""

if "py_output" not in st.session_state:
    st.session_state.py_output = ""

if "phases" not in st.session_state:
    st.session_state.phases = {}

# =========================================
# 🔹 LAYOUT
# =========================================
col1, col2 = st.columns([1.2, 0.8], gap="large")

with col1:
    st.markdown("#### ◈ Source (C)")
    u_file = st.file_uploader("Upload Source", type=["c"], label_visibility="collapsed")
    if u_file:
        st.session_state.c_source = u_file.read().decode("utf-8")
        st.toast("File Loaded!", icon="📁")

    c_code_input = st.text_area("source code",value=st.session_state.c_source,height=350, label_visibility="collapsed")
    

with col2:
    st.markdown("#### ⚡ Pipeline & Result")
    compile_clicked = st.button("❯ GENERATE PYTHON")
    
    status_placeholder = st.empty()
    output_placeholder = st.empty()

    if compile_clicked:
        if not c_code_input.strip():
            st.warning("Input C code cannot be empty.")
        else:
            with status_placeholder.container():
                with st.status("≣ Processing Engine...", expanded=True) as status:
                    # Clear previous phase data
                    st.session_state.phases = {}
                    
                    st.write("◈ **Phase 1:** Lexical Analysis...")
                    lines = c_code_input.split("\n")
                    tokens, symbol_table = lexical_analysis(lines)
                    st.session_state.phases["tokens"] = tokens
                    st.session_state.phases["symbol_table_init"] = symbol_table.copy()
                    time.sleep(0.3)
                    
                    st.write("◈ **Phase 2:** Syntax Analysis...")
                    parsed, syntax_errors = syntax_analysis(lines)
                    st.session_state.phases["parsed"] = parsed
                    st.session_state.phases["syntax_errors"] = syntax_errors
                    time.sleep(0.3)
                    
                    if syntax_errors:
                        status.update(label="❌ Syntax Errors", state="error")
                        for e in syntax_errors:
                            st.error(e)
                        st.session_state.py_output = ""
                        st.stop()
                    
                    st.write("◈ **Phase 3:** Semantic Checking...")
                    symbol_table_updated, errors = semantic_analysis(parsed, symbol_table)
                    st.session_state.phases["symbol_table_updated"] = symbol_table_updated
                    st.session_state.phases["errors"] = errors
                    time.sleep(0.3)
                    
                    if errors:
                        status.update(label="❌ Semantic Errors", state="error")
                        for e in errors:
                            st.error(e)
                        st.session_state.py_output = ""
                    else:
                        st.write("◈ **Phase 4:** Intermediate Code...")
                        ir_code = generate_intermediate(parsed)
                        st.session_state.phases["ir"] = ir_code
                        time.sleep(0.2)
                        
                        st.write("◈ **Phase 5:** Code Optimization...")
                        optimized_code = optimize_code(ir_code)
                        st.session_state.phases["optimized"] = optimized_code
                        time.sleep(0.2)
                        
                        st.write("◈ **Phase 6:** Python Generation...")
                        final_code = generate_python_code(optimized_code)
                        time.sleep(0.2)
                        
                        st.session_state.py_output = "\n".join(final_code)
                        status.update(label="✅ Compilation Successful", state="complete", expanded=False)
                        st.toast("Translation Complete!", icon="✨")

    # Display Output
    if st.session_state.py_output:
        with output_placeholder.container():
            st.code(st.session_state.py_output, language="python", line_numbers=True)
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button("📁 Download Python", data=st.session_state.py_output, file_name="translated.py", use_container_width=True)
            with d_col2:
                # Toggle for the bottom section
                view_phases = st.toggle("≣ View Intermediate Phases", value=False)
    elif not compile_clicked:
        output_placeholder.markdown(f"""<div style="height: 350px; display: flex; align-items: center; justify-content: center; border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px; color: #555;"><p style="font-size: 14px;">Review C code and click GENERATE</p></div>""", unsafe_allow_html=True)

# =========================================
# 🔹 INTERMEDIATE STEPS SECTION (BOTTOM)
# =========================================
if st.session_state.py_output and "view_phases" in locals() and view_phases:
    st.markdown("---")
    st.markdown("### 🔍 Internal Engine States (Phase Decomposition)")
    
    p = st.session_state.phases
    
    # 1. Tokens and Symbol Table
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="phase-label">Phase 1: Token Stream</div>', unsafe_allow_html=True)
        token_df = pd.DataFrame(p.get("tokens", []), columns=["Type", "Value"])
        st.dataframe(token_df, use_container_width=True, hide_index=True, height=200)
        
    with c2:
        st.markdown('<div class="phase-label">Phase 2-3: Symbol Table (Final)</div>', unsafe_allow_html=True)
        # Convert symbol table dict to table
        sb = p.get("symbol_table_updated", {})
        sb_data = [{"Variable": k, "Type": v["type"], "Value": v["value"]} for k, v in sb.items()]
        st.dataframe(pd.DataFrame(sb_data), use_container_width=True, hide_index=True, height=200)

    # 2. Syntax Analysis (JSON)
    st.markdown('<div class="phase-label">Phase 2: Syntax Analysis (Abstracted List)</div>', unsafe_allow_html=True)
    with st.container(height=180, border=True):
        st.json(p.get("parsed", []), expanded=True)

    # 3. IR and Optimization Note
    st.markdown("""
        <div style="background: rgba(0, 195, 255, 0.05); padding: 8px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #00c3ff;">
            <p style="margin: 0; font-size: 0.75rem; color: #888;">
                <b>Note:</b> Braces <code>{ }</code> are preserved in the Optimized IR so that <b>Phase 6 (Generator)</b> can correctly map them to Python indentation levels.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 3. IR and Optimization
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="phase-label">Phase 4-5: Intermediate Representation (IR)</div>', unsafe_allow_html=True)
        st.code("\n".join(p.get("ir", [])), language="python")
    with c4:
        st.markdown('<div class="phase-label">Phase 5-6: Optimized Code (Internal IR)</div>', unsafe_allow_html=True)
        st.code("\n".join(p.get("optimized", [])), language="python")

    # 4. Global Download
    report_text = generate_full_report()
    st.download_button(
        label="📄 Download Full Compiler Report (.txt)",
        data=report_text,
        file_name="compiler_engine_report.txt",
        mime="text/plain",
        use_container_width=True
    )

# Footer
st.markdown("""<div style="text-align: center; color: #444; font-size: 0.7rem; margin-top: 1rem;">⌬ Modular Integrated Compiler Engine • Phase 6 Complete</div>""", unsafe_allow_html=True)