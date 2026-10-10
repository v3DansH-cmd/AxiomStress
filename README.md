# Link : https://v3dansh-cmd-axiomstress-app-zan0ai.streamlit.app/
# ⚡ AxiomStress - Automated Adversarial Physics Falsification Platform

**AxiomStress** is an autonomous theoretical physics verification and stress-testing system powered by **Gemma 4** (`gemma-4-26b-a4b-it`) with deep reasoning traces (`thinking_level="high"`).

It scans handwritten or sketched theoretical physics equations, subjects them to dimensional analysis, relativistic & quantum asymptotic limits, detects boundary breakdown points, derives mathematically patched generalizations, and generates interactive Plotly simulation proofs.

---

## 🚀 Key Features

1. **🔬 Multi-Modal Equation Ingestion**:
   - 3 preloaded chalkboard research presets:
     - `preset_pendulum.png`: Simple Harmonic Pendulum ($\theta'' + (g/L)\theta = 0$)
     - `preset_relativity.png`: Classical Momentum ($p = m \cdot v$)
     - `preset_quantum_osc.png`: 1D Quantum Harmonic Oscillator ($\frac{d^2\psi}{dx^2} + \frac{2m}{\hbar^2}(E - \frac{1}{2}kx^2)\psi = 0$)
   - Custom handwritten sketch / image uploader (PNG, JPG, WEBP).
   - Automatic Pillow image preprocessing (RGB normalization & 1024px maximum dimension scaling).

2. **🧠 Gemma 4 Reasoning & Falsification Protocol**:
   - Model: `gemma-4-26b-a4b-it` via official `google.genai` SDK.
   - Temperature `0.1` and `thinking_level="high"` with 4096 output tokens.
   - Spatial ambiguity detection & hypothesis branching.
   - Base SI dimensional verification ($[M], [L], [T], [Q], [\Theta]$).
   - Asymptotic limits ($v \to c$, $\hbar \to 0$, $T \to 0$, extreme curvatures).
   - Failure point diagnosis & patched LaTeX formulas.
   - 2 cross-domain intuitive analogies.

3. **📊 Interactive Plotly Simulation Proof**:
   - Plots Original Linearized/Approximation (dashed red) vs. Patched Physical Formulation (solid emerald green).
   - Divergence error area highlighting.
   - Dynamic parameter scaling and breakdown threshold marker.
   - Quantitative divergence percentage error metrics.
   - One-click Markdown report export (`.md`).

---

## 📁 Project Structure

```
hacktober/
├── assets/                       # Dark chalkboard equation presets
│   ├── preset_pendulum.png
│   ├── preset_relativity.png
│   └── preset_quantum_osc.png
├── app.py                        # Streamlit Wide Dual-Column Web Application
├── stress_engine.py              # Gemma 4 Falsification Engine & JSON Spec Extractor
├── sim_engine.py                 # Plotly Dark Simulation Proof & Divergence Evaluator
├── create_presets.py             # Script to generate dark equation sketches
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # Documentation
```
