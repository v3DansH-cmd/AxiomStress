"""
app.py - AxiomStress: Automated Adversarial Physics Falsification Platform
Powered by Gemma 4 & Google GenAI SDK.
"""

import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

import stress_engine
import sim_engine

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AxiomStress | Physics Falsification Protocol",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Dark Glassmorphism Aesthetic)
st.markdown(
    """
    <style>
    /* Dark Theme & High Contrast Styling */
    .stApp {
        background-color: #080c14;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header Gradient & Badges */
    .axiom-hero {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.3) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .axiom-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
        letter-spacing: -0.5px;
    }
    .axiom-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-right: 6px;
    }
    .badge-cyan {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .badge-purple {
        background-color: rgba(168, 85, 247, 0.15);
        color: #c084fc;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .badge-emerald {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Card Panels */
    .glass-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(51, 65, 85, 0.6);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }

    /* Metric Callout Card */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 1.4rem;
        font-weight: 700;
        font-family: monospace;
        margin-top: 4px;
    }

    /* Primary Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: #ffffff;
        font-weight: 700;
        font-size: 1.05rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #1d4ed8, #6d28d9);
        border-color: #38bdf8;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #0f172a !rs;
        border-radius: 8px;
        color: #cbd5e1 !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Banner
st.markdown(
    """
    <div class="axiom-hero">
        <div style="margin-bottom: 8px;">
            <span class="badge badge-cyan">⚡ GEMMA 4 REASONING ENGINE</span>
            <span class="badge badge-purple">🔬 AUTOMATED FALSIFICATION</span>
            <span class="badge badge-emerald">📊 THEORETICAL STRESS PROOF</span>
        </div>
        <h1 class="axiom-title">AxiomStress</h1>
        <p class="axiom-subtitle">
            Autonomous adversarial physics falsification engine. Stress-tests sketched & handwritten theoretical equations against dimensional bounds, asymptotic limits, and relativistic/quantum regimes.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Ensure presets exist
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if not os.path.exists(assets_dir) or not os.path.exists(os.path.join(assets_dir, "preset_pendulum.png")):
    import create_presets
    create_presets.main()

# Initialize session state for analysis results
if "analysis_raw" not in st.session_state:
    st.session_state["analysis_raw"] = None
if "analysis_spec" not in st.session_state:
    st.session_state["analysis_spec"] = None
if "analysis_thoughts" not in st.session_state:
    st.session_state["analysis_thoughts"] = None
if "current_image_name" not in st.session_state:
    st.session_state["current_image_name"] = None

# Sidebar: Configuration & API Key
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    env_api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_api_key,
        type="password",
        help="Provide your Gemini API key to run live multimodal inference with Gemma 4."
    )
    
    if api_key_input:
        st.markdown("<span class='badge badge-emerald'>🔑 API Key Loaded</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge badge-purple'>🧪 Preset Benchmark Mode Active</span>", unsafe_allow_html=True)
        st.caption("Live inference requires an API key. Built-in presets run instantly with full benchmark proofs.")
        
    st.markdown("---")
    st.markdown("### 🧠 Model Architecture")
    st.markdown("- **Model**: `gemma-4-26b-a4b-it`")
    st.markdown("- **Thinking Level**: `High` (Deep reasoning traces)")
    st.markdown("- **Temperature**: `0.1` (Deterministic rigor)")
    st.markdown("- **Token Window**: `4096 tokens`")
    st.markdown("---")
    st.caption("AxiomStress v1.0 • DeepMind Hacktober Protocol")

# Main Dual Column Layout
col_left, col_right = st.columns([0.42, 0.58], gap="large")

# ==========================================
# LEFT COLUMN: Inputs, Presets & Controls
# ==========================================
with col_left:
    st.markdown("### 📥 Hypothesis Input")
    
    input_mode = st.radio(
        "Select Input Source",
        options=["🔬 Preloaded Research Presets", "📤 Upload Custom Sketch"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    selected_image = None
    preset_key = None
    image_display_title = ""

    if input_mode == "🔬 Preloaded Research Presets":
        preset_option = st.selectbox(
            "Select Benchmark Theory",
            options=[
                "1. Simple Harmonic Pendulum: θ'' + (g/L)θ = 0",
                "2. Classical Linear Momentum: p = m · v",
                "3. 1D Quantum Harmonic Oscillator: d²ψ/dx² + (2m/ħ²)(E - ½kx²)ψ = 0"
            ],
            index=0
        )
        
        if "Pendulum" in preset_option:
            preset_key = "preset_pendulum"
            image_path = os.path.join(assets_dir, "preset_pendulum.png")
            image_display_title = "Simple Harmonic Pendulum Equation"
        elif "Momentum" in preset_option:
            preset_key = "preset_relativity"
            image_path = os.path.join(assets_dir, "preset_relativity.png")
            image_display_title = "Classical Newtonian Momentum"
        else:
            preset_key = "preset_quantum_osc"
            image_path = os.path.join(assets_dir, "preset_quantum_osc.png")
            image_display_title = "Quantum Harmonic Oscillator Potential"

        if os.path.exists(image_path):
            selected_image = Image.open(image_path)
    else:
        uploaded_file = st.file_uploader(
            "Upload handwritten equation or sketch",
            type=["png", "jpg", "jpeg", "webp"],
            help="Upload a clear image of a handwritten physics equation or theory sketch."
        )
        if uploaded_file is not None:
            selected_image = Image.open(uploaded_file)
            image_display_title = f"Uploaded: {uploaded_file.name}"
            preset_key = None

    # Image Preview Card
    if selected_image is not None:
        st.markdown(f"**Sketch Preview**: *{image_display_title}*")
        st.image(selected_image, use_container_width=True)
    else:
        st.info("Please select a preset or upload an equation sketch to begin.")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    # Primary Action Button
    run_btn = st.button("🚀 Run Falsification Protocol", use_container_width=True)
    
    if run_btn and selected_image is not None:
        with st.spinner("⚡ Gemma 4 Falsification Engine running dimensional stress & asymptotic tests..."):
            try:
                raw_report, parsed_spec, thought_traces = stress_engine.run_falsification_protocol(
                    image_input=selected_image,
                    api_key=api_key_input if api_key_input else None,
                    preset_name=preset_key
                )
                
                st.session_state["analysis_raw"] = raw_report
                st.session_state["analysis_spec"] = parsed_spec
                st.session_state["analysis_thoughts"] = thought_traces
                st.session_state["current_image_name"] = image_display_title
                st.toast("✅ Falsification Protocol completed successfully!", icon="⚡")
            except Exception as ex:
                st.error(f"Falsification Protocol failed: {str(ex)}")

# Automatically run the first preset on first load if state is empty
if st.session_state["analysis_spec"] is None and selected_image is not None:
    raw_report, parsed_spec, thought_traces = stress_engine.run_falsification_protocol(
        image_input=selected_image,
        api_key=api_key_input if api_key_input else None,
        preset_name=preset_key or "preset_pendulum"
    )
    st.session_state["analysis_raw"] = raw_report
    st.session_state["analysis_spec"] = parsed_spec
    st.session_state["analysis_thoughts"] = thought_traces
    st.session_state["current_image_name"] = image_display_title

# ==========================================
# RIGHT COLUMN: Reasoning, Report & Proof
# ==========================================
with col_right:
    st.markdown("### 📋 Falsification Proof & Verification")
    
    if st.session_state["analysis_raw"] is not None and st.session_state["analysis_spec"] is not None:
        spec = st.session_state["analysis_spec"]
        raw_report = st.session_state["analysis_raw"]
        thought_traces = st.session_state.get("analysis_thoughts", "")
        
        # 1. Expandable Reasoning Chain
        with st.expander("🧠 Gemma 4 Reasoning Traces", expanded=False):
            st.markdown(
                f"""
                <div style="background-color: #0b1120; border: 1px solid #1e293b; border-radius: 6px; padding: 14px; font-family: monospace; font-size: 0.88rem; color: #93c5fd; white-space: pre-wrap;">
{thought_traces}
                </div>
                """,
                unsafe_allow_html=True
            )

        # 2. Tabbed Interface: Report & LaTeX vs. Interactive Simulation Proof
        tab_report, tab_sim = st.tabs([
            "📄 Falsification Report & LaTeX",
            "📊 Interactive Simulation Proof"
        ])

        # TAB 1: Report & LaTeX
        with tab_report:
            # Clean display of markdown report without raw json block if present
            clean_display_report = raw_report
            if "```json" in clean_display_report:
                clean_display_report = clean_display_report.split("```json")[0].strip()
            
            st.markdown(clean_display_report)
            
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            
            # Markdown Report Download Button
            report_download_content = f"""# AxiomStress Falsification Report
**Target Hypothesis**: {st.session_state.get('current_image_name', 'Custom Sketch')}
**Engine**: Gemma 4 (gemma-4-26b-a4b-it) Thinking Level: High

---

## Reasoning Trace Summary
{thought_traces}

---

## Full Falsification Analysis
{raw_report}
"""
            st.download_button(
                label="📥 Download Falsification Report (.md)",
                data=report_download_content,
                file_name="axiom_stress_falsification_report.md",
                mime="text/markdown",
                use_container_width=True
            )

        # TAB 2: Interactive Simulation Proof
        with tab_sim:
            st.markdown("#### Dynamic Limit Stress Test")
            
            # Interactive Controls Row
            ctl_col1, ctl_col2 = st.columns([0.5, 0.5])
            
            with ctl_col1:
                scale_slider = st.slider(
                    "🔍 Parameter Domain Scale",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.0,
                    step=0.1,
                    help="Extends the parameter envelope beyond nominal bounds to reveal asymptotic divergence."
                )
            
            default_thresh = float(spec.get("breakdown_threshold", 0.5))
            with ctl_col2:
                thresh_slider = st.slider(
                    "⚠️ Breakdown Threshold (x)",
                    min_value=float(spec.get("x_min", 0.0)),
                    max_value=float(spec.get("x_max", 2.0)) * scale_slider,
                    value=default_thresh,
                    step=0.01,
                    help="Adjust the breakdown threshold marker on the proof chart."
                )

            # Generate Plotly Chart
            fig = sim_engine.create_falsification_plot(
                spec=spec,
                param_scale=scale_slider,
                threshold_override=thresh_slider
            )
            st.plotly_chart(fig, use_container_width=True)

            # Divergence Metrics Strip
            metrics = sim_engine.calculate_divergence_metrics(spec, thresh_slider)
            
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">Probe Point (x)</div>
                        <div class="metric-value">{metrics['x']:.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m_col2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">Original (y)</div>
                        <div class="metric-value" style="color: #ef4444;">{metrics['y_original']:.3f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m_col3:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">Patched (y)</div>
                        <div class="metric-value" style="color: #10b981;">{metrics['y_patched']:.3f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with m_col4:
                pct_color = "#f59e0b" if metrics['percentage_error'] > 5.0 else "#38bdf8"
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-title">Divergence Error</div>
                        <div class="metric-value" style="color: {pct_color};">{metrics['percentage_error']:.1f}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Mathematical Spec Inspector
            with st.expander("🔍 Simulation Mathematical Spec", expanded=False):
                st.json(spec)

    else:
        st.info("👈 Select a preset or upload an equation sketch on the left and click **Run Falsification Protocol** to generate the proof.")
