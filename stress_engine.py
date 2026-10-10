"""
stress_engine.py - Automated Physics Falsification Engine for AxiomStress
Powered by Gemma 4 / Google GenAI SDK.
"""

import os
import re
import json
import io
from typing import Dict, Any, Tuple, Optional
from PIL import Image

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from dotenv import load_dotenv

load_dotenv()

# System and user prompt template
FALSIFICATION_PROMPT = """You are AxiomStress, an adversarial physics verification and automated falsification engine.
Analyze the handwritten or sketched physics equation presented in the image.

Perform a deep, rigorous 5-step Falsification Protocol:

### 1. Spatial & Syntactic Ambiguity Check
- Transcribe the mathematical equation accurately from the image.
- Explicitly identify potential symbol ambiguities or notation confusions (e.g., sin²x vs sin 2x, ν vs v, ρ vs p, partial vs total derivatives, missing tensor indices).
- If multiple interpretations exist, branch the hypothesis and proceed with the standard primary equation.

### 2. Dimensional Analysis & Asymptotic Limit Stress Tests
- Perform dimensional analysis using SI base dimensions ([M], [L], [T], [Q], [Θ]) to check homogeneity.
- Stress-test the equation across relevant physical regimes and asymptotic limits:
  * Relativistic limits ($v \\to c$, $v \\ll c$)
  * Quantum / Classical correspondence limits ($\\hbar \\to 0$, $n \\to \\infty$)
  * Thermal limits ($T \\to 0$ K, $T \\to \\infty$)
  * Geometric / Boundary limits (e.g., large angles, extreme curvatures, $r \\to 0$, $r \\to \\infty$)

### 3. Failure Point Diagnosis & Patched Formulation
- Diagnose the exact physical mechanism and threshold where the formula breaks down (e.g. non-linearities, non-conservation, infinite energies, unphysical speeds).
- Present the Patched / Corrected LaTeX formula that restores physical validity across the extended regime.
- Display both Original and Patched equations in clear display LaTeX blocks:
  $$ \\text{Original: } ... $$
  $$ \\text{Patched: } ... $$

### 4. Cross-Domain Analogies
- Provide 2 distinct, high-fidelity cross-domain analogies illustrating the breakdown and patch (e.g., from acoustics, semiconductor physics, fluid mechanics, structural engineering, or signal processing).

### 5. Executable Numerical Simulation Specification
Emit a final standalone JSON block enclosed strictly in ```json ... ``` with the following exact keys to allow interactive mathematical verification:
```json
{
  "variable_name": "x",
  "x_min": 0.0,
  "x_max": 2.0,
  "original_label": "Original Linear Form",
  "original_expr": "x",
  "patched_label": "Patched Non-linear Form",
  "patched_expr": "sin(x)",
  "breakdown_threshold": 0.35,
  "x_axis_title": "Independent Variable x",
  "y_axis_title": "System Response y"
}
```

CRITICAL RULES FOR JSON:
- `original_expr` and `patched_expr` MUST be valid 1-variable math expressions of `x` (using standard Python/numpy math functions like `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`, `sinh`, `cosh`, `tanh`, `**`, `*`, `/`, `+`, `-`).
- For relativity ($p=mv$), use normalized $x = v/c$ from $0.0$ to $0.99$, `original_expr = "x"`, `patched_expr = "x / sqrt(1 - x**2)"`, `breakdown_threshold = 0.2`.
- For pendulum ($\theta'' + (g/L)\theta = 0$), use angle $x = \theta$ from $0.0$ to $3.14$, `original_expr = "x"`, `patched_expr = "sin(x)"`, `breakdown_threshold = 0.35`.
- For harmonic oscillator, use dimensionless position or energy $x$ where original quadratic potential vs Morse/anharmonic potential diverges.
"""

def preprocess_image(image_input) -> Image.Image:
    """
    Preprocess input image:
    - Convert to RGB
    - Resize longest dimension to max 1024px to save tokens and latency while preserving aspect ratio.
    """
    if isinstance(image_input, (str, os.PathLike)):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        # Streamlit UploadedFile or similar file-like object
        img = Image.open(image_input)

    # Convert to RGB mode
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize if max dimension > 1024px
    max_dim = 1024
    w, h = img.size
    if max(w, h) > max_dim:
        if w > h:
            new_w = max_dim
            new_h = int(h * (max_dim / w))
        else:
            new_h = max_dim
            new_w = int(w * (max_dim / h))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    return img

def extract_json_spec(text: str) -> Optional[Dict[str, Any]]:
    """
    Safely extracts and parses the JSON specification block from the model output.
    """
    if not text:
        return None

    # First attempt: Match ```json ... ``` blocks
    json_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except Exception:
            pass

    # Second attempt: Look for outermost curly braces containing required keys
    json_candidates = re.findall(r"\{[^{}]*\"original_expr\"[^{}]*\}", text, re.DOTALL)
    for cand in json_candidates:
        try:
            return json.loads(cand)
        except Exception:
            pass

    # Third attempt: Broadest curly brace match
    brace_match = re.search(r"(\{[\s\S]*\})", text)
    if brace_match:
        try:
            parsed = json.loads(brace_match.group(1))
            if "original_expr" in parsed and "patched_expr" in parsed:
                return parsed
        except Exception:
            pass

    return None

def get_preset_fallback(preset_name: str) -> Tuple[str, Dict[str, Any], str]:
    """
    Provides rich precomputed theoretical analysis and simulation spec
    for instant exploration and testing.
    """
    if "pendulum" in preset_name.lower():
        raw_text = r"""### 1. Spatial & Syntactic Ambiguity Check
- **Transcription**: $\theta'' + \left(\frac{g}{L}\right)\theta = 0$
- **Ambiguity Analysis**: The second-derivative notation $\theta''$ denotes $\frac{d^2\theta}{dt^2}$. The equation represents the linearized torque balance of a planar simple pendulum of length $L$ under gravitational acceleration $g$.
- **Hypothesis**: The small-angle approximation $\sin\theta \approx \theta$ has been substituted for the exact gravitational restoring torque $\tau_g = -mgL\sin\theta$.

### 2. Dimensional Analysis & Asymptotic Limit Stress Tests
- **Dimensional Homogeneity**:
  * $[\theta] = 1$ (dimensionless angle in radians)
  * $[g] = [L][T]^{-2}$
  * $[L] = [L]$
  * $[g/L] = [T]^{-2}$
  * $[\theta''] = [T]^{-2}$
  * Dimensional balance: $[T]^{-2} + [T]^{-2}\cdot 1 = 0$ (Homogeneous $\checkmark$)
- **Asymptotic Limit Stress**:
  * As $\theta \to 0$: $\sin\theta = \theta - \frac{\theta^3}{6} + \mathcal{O}(\theta^5) \to \theta$ (Valid $\checkmark$)
  * As $\theta \to \pi/2$ ($90^\circ$): True restoring torque $\sin(\pi/2)=1.0$, Linear approximation predicts $\pi/2 \approx 1.5708$ ($+57\%$ error $\times$).
  * As $\theta \to \pi$ (Inverted pendulum): True torque is $0$, Linear model predicts unphysical restoring acceleration $\pi \cdot (g/L)$.

### 3. Failure Point Diagnosis & Patched Formulation
- **Breakdown Regime**: Small-angle Taylor series truncation fails significantly for $\theta > 0.35\text{ rad} \approx 20^\circ$. Period becomes strongly amplitude-dependent (anharmonicity via complete elliptic integrals of the first kind $K(k)$).
- **Patched Exact Formulation**:
  $$ \text{Original (Linear): } \frac{d^2\theta}{dt^2} + \frac{g}{L}\theta = 0 $$
  $$ \text{Patched (Exact Non-Linear): } \frac{d^2\theta}{dt^2} + \frac{g}{L}\sin(\theta) = 0 $$
  $$ \text{Exact Period: } T(\theta_0) = 4\sqrt{\frac{L}{g}}\, K\left(\sin^2\frac{\theta_0}{2}\right) \approx 2\pi\sqrt{\frac{L}{g}}\left[1 + \frac{1}{16}\theta_0^2 + \frac{11}{3072}\theta_0^4 + \dots\right] $$

### 4. Cross-Domain Analogies
1. **Electronics / Signal Processing**: Class-A Transistor Linear Amplification vs. Harmonic Clipping. A small input voltage operates in the linear transconductance region; overdriving the gate causes strong non-linear harmonic distortion and saturation.
2. **Structural Engineering**: Euler Column Buckling. Small lateral deflections follow Hookean linear elasticity, but exceeding the critical buckling load induces non-linear geometric deformation and bifurcation.

### 5. Executable Numerical Simulation Specification
```json
{
  "variable_name": "theta",
  "x_min": 0.0,
  "x_max": 3.14159,
  "original_label": "Linear Restoring Force F_lin = - (g/L) θ",
  "original_expr": "x",
  "patched_label": "Exact Restoring Force F_exact = - (g/L) sin(θ)",
  "patched_expr": "sin(x)",
  "breakdown_threshold": 0.35,
  "x_axis_title": "Deflection Angle θ (radians)",
  "y_axis_title": "Normalized Restoring Force Torque (g/L)"
}
```
"""
        thoughts = "Examined simple pendulum equation. Traced Taylor series expansion of sin(theta) = theta - theta^3/6 + ... Diagnosed non-linear breakdown at theta > 0.35 rad (20 deg). Calculated elliptic integral correction."
        spec = extract_json_spec(raw_text)
        return raw_text, spec, thoughts

    elif "relativity" in preset_name.lower():
        raw_text = r"""### 1. Spatial & Syntactic Ambiguity Check
- **Transcription**: $p = m \cdot v$
- **Ambiguity Analysis**: $p$ represents linear momentum, $m$ represents invariant rest mass $m_0$, and $v$ is 1-dimensional velocity.
- **Hypothesis**: The formulation assumes Galilean invariance with constant inertia independent of reference frame velocity.

### 2. Dimensional Analysis & Asymptotic Limit Stress Tests
- **Dimensional Homogeneity**:
  * $[p] = [M][L][T]^{-1}$
  * $[m] = [M]$, $[v] = [L][T]^{-1} \implies [m\cdot v] = [M][L][T]^{-1}$ (Homogeneous $\checkmark$)
- **Asymptotic Limit Stress**:
  * Non-relativistic limit ($v \ll c$): $\gamma = (1 - v^2/c^2)^{-1/2} \to 1 \implies p \to mv$ (Valid $\checkmark$)
  * Relativistic limit ($v \to c$): Newtonian $p = mc$ (finite); Special Relativity requires $p \to \infty$ as $v \to c$ to prohibit superluminal acceleration under finite force ($F = dp/dt$).
  * Infinite speed test ($v > c$): Newtonian mechanics permits unbounded velocity, violating Lorentz covariance and causality.

### 3. Failure Point Diagnosis & Patched Formulation
- **Breakdown Regime**: Significant divergence ($>2\%$ deviation) occurs at $v \ge 0.20\,c$. At $v = 0.866\,c$, relativistic momentum is exactly $2\times$ classical expectation. At $v = 0.99\,c$, $\gamma \approx 7.09$.
- **Patched Relativistic Formulation**:
  $$ \text{Original (Newtonian): } p = m v $$
  $$ \text{Patched (Relativistic): } p = \gamma m v = \frac{m v}{\sqrt{1 - \frac{v^2}{c^2}}} $$
  $$ \text{Invariant 4-Momentum: } P^\mu = m \frac{dx^\mu}{d\tau} = (\gamma m c, \gamma m \mathbf{v}) $$

### 4. Cross-Domain Analogies
1. **Compressible Aerodynamics**: Subsonic Incompressible Flow vs. Transonic Compressibility Drag Divergence. As airflow velocity approaches Mach 1 ($v \to c_s$), the Prandtl-Glauert factor $\beta = \sqrt{1 - M^2}$ creates an asymptotic pressure spike analogous to the Lorentz factor $\gamma$.
2. **Network Queueing Theory**: M/M/1 Queue Latency. As server utilization $\rho = \lambda/\mu$ approaches $1.0$, queue delay diverges asymptotically as $1/(1 - \rho)$, preventing infinite packet throughput.

### 5. Executable Numerical Simulation Specification
```json
{
  "variable_name": "beta",
  "x_min": 0.0,
  "x_max": 0.98,
  "original_label": "Classical Momentum p_class = m * (v/c)",
  "original_expr": "x",
  "patched_label": "Relativistic Momentum p_rel = (v/c) / sqrt(1 - (v/c)^2)",
  "patched_expr": "x / sqrt(maximum(1e-5, 1 - x**2))",
  "breakdown_threshold": 0.20,
  "x_axis_title": "Normalized Velocity β = v / c",
  "y_axis_title": "Normalized Momentum p / (m·c)"
}
```
"""
        thoughts = "Checked Newtonian linear momentum p = mv. Tested Galilean transformation vs Lorentz boost. Diagnosed asymptote at v -> c. Configured relativistic gamma factor patch."
        spec = extract_json_spec(raw_text)
        return raw_text, spec, thoughts

    else: # Quantum Oscillator
        raw_text = r"""### 1. Spatial & Syntactic Ambiguity Check
- **Transcription**: $\frac{d^2\psi}{dx^2} + \frac{2m}{\hbar^2}\left(E - \frac{1}{2}kx^2\right)\psi = 0$
- **Ambiguity Analysis**: Time-independent 1D Schrödinger equation for a parabolic harmonic oscillator potential $V(x) = \frac{1}{2}kx^2 = \frac{1}{2}m\omega^2 x^2$.
- **Hypothesis**: The system models ideal parabolic confinement with infinite bound states and equally spaced energy rungs $\Delta E = \hbar\omega$.

### 2. Dimensional Analysis & Asymptotic Limit Stress Tests
- **Dimensional Homogeneity**:
  * $[\psi] = [L]^{-1/2}$
  * $[d^2\psi/dx^2] = [L]^{-5/2}$
  * $[2m/\hbar^2] = [M] / ([M]^2[L]^4[T]^{-2}) = [M]^{-1}[L]^{-4}[T]^2$
  * $[E - \frac{1}{2}kx^2] = [M][L]^2[T]^{-2}$
  * Product: $[2m/\hbar^2][E - V]\psi = [L]^{-2} \cdot [L]^{-1/2} = [L]^{-5/2}$ (Homogeneous $\checkmark$)
- **Asymptotic Limit Stress**:
  * Low energy ground state ($n=0, x \to 0$): Parabolic approximation matches physical diatomic potential (Valid $\checkmark$).
  * Large displacement limit ($x \to \infty$ or dissociation): Harmonic potential $V(x) \to \infty$ predicts infinite binding energy, whereas real chemical/atomic bonds dissociate at finite $D_e$.

### 3. Failure Point Diagnosis & Patched Formulation
- **Breakdown Regime**: Breaks down for high vibrational quantum numbers $n \gg 1$ and large displacements ($x > x_{\text{dissoc}}$). Real molecular potentials exhibit anharmonic softening and finite dissociation energy.
- **Patched Anharmonic / Morse Formulation**:
  $$ \text{Original (Harmonic): } V_{\text{harm}}(x) = \frac{1}{2} k x^2 $$
  $$ \text{Patched (Morse Potential): } V_{\text{Morse}}(x) = D_e \left(1 - e^{-a x}\right)^2 \approx \frac{1}{2}kx^2 - D_e a^3 x^3 + \frac{7}{12}D_e a^4 x^4 $$
  $$ \text{Corrected Eigenenergies: } E_n = \hbar\omega\left(n + \frac{1}{2}\right) - \frac{(\hbar\omega)^2}{4D_e}\left(n + \frac{1}{2}\right)^2 $$

### 4. Cross-Domain Analogies
1. **Mechanical Stress & Strain**: Linear Hookean Elasticity vs. Plastic Yielding & Necking. Springs deform linearly $\sigma = E\epsilon$ up to the proportional limit; beyond that, dislocation slip causes non-linear softening and ultimate fracture.
2. **Optical Fiber Non-linearities**: Linear Kerr Refraction vs. Self-Phase Modulation and Soliton Collapse in non-linear dielectric media under high optical field intensities.

### 5. Executable Numerical Simulation Specification
```json
{
  "variable_name": "x",
  "x_min": -1.5,
  "x_max": 2.5,
  "original_label": "Harmonic Potential V_harm = 0.5 * x^2",
  "original_expr": "0.5 * x**2",
  "patched_label": "Morse Anharmonic Potential V_morse = (1 - exp(-x))^2",
  "patched_expr": "(1 - exp(-x))**2",
  "breakdown_threshold": 0.70,
  "x_axis_title": "Normalized Displacement x / x_0",
  "y_axis_title": "Normalized Potential Energy V / D_e"
}
```
"""
        thoughts = "Evaluated 1D quantum harmonic oscillator potential V(x) = 1/2 k x^2. Analyzed asymptotic dissociation limit. Formulated Morse potential and cubic/quartic anharmonic corrections."
        spec = extract_json_spec(raw_text)
        return raw_text, spec, thoughts

def run_falsification_protocol(
    image_input,
    api_key: Optional[str] = None,
    preset_name: Optional[str] = None
) -> Tuple[str, Optional[Dict[str, Any]], str]:
    """
    Executes the full automated falsification protocol:
    1. Preprocesses image
    2. Calls Gemma 4 (gemma-4-26b-a4b-it) via google.genai Client with thinking_level='high'
    3. Extracts reasoning traces and parsed JSON simulation spec.
    """
    effective_api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    # If no API key is provided and preset_name is available, return curated benchmark analysis
    if not effective_api_key:
        if preset_name:
            return get_preset_fallback(preset_name)
        raise ValueError(
            "GEMINI_API_KEY is not configured. Please enter your Gemini API key in the sidebar "
            "or configure it in your environment / .env file."
        )

    if genai is None or types is None:
        raise ImportError(
            "google-genai package is not available. Please install `google-genai`."
        )

    # Preprocess image
    pil_image = preprocess_image(image_input)

    # Initialize client
    client = genai.Client(api_key=effective_api_key)

    # Build GenerateContentConfig
    # thinking_level="high", temperature=0.1, max_output_tokens=4096
    config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high"),
        temperature=0.1,
        max_output_tokens=4096,
    )

    model_name = "gemma-4-26b-a4b-it"

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                pil_image,
                FALSIFICATION_PROMPT
            ],
            config=config
        )
    except Exception as e:
        # If model is unavailable or rate limited, attempt fallback if preset is provided or raise clear error
        err_str = str(e)
        if preset_name and ("404" in err_str or "not found" in err_str.lower() or "permission" in err_str.lower()):
            # Graceful fallback for preset
            return get_preset_fallback(preset_name)
        raise RuntimeError(f"Gemma 4 API Execution Error: {err_str}")

    # Extract response text and thoughts
    raw_text = response.text or ""
    thoughts_list = []

    # Attempt to extract thinking traces from response candidates
    if hasattr(response, "candidates") and response.candidates:
        for candidate in response.candidates:
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                for part in candidate.content.parts:
                    if getattr(part, "thought", False) and hasattr(part, "text"):
                        thoughts_list.append(part.text)

    thoughts = "\n\n".join(thoughts_list) if thoughts_list else "High-level reasoning traces processed internally by Gemma 4."

    # Parse JSON specification
    spec = extract_json_spec(raw_text)

    # If spec extraction failed, create a fallback baseline from parsed equations
    if not spec:
        spec = {
            "variable_name": "x",
            "x_min": 0.0,
            "x_max": 2.0,
            "original_label": "Original Linearized Formulation",
            "original_expr": "x",
            "patched_label": "Patched Formulation",
            "patched_expr": "sin(x)",
            "breakdown_threshold": 0.5,
            "x_axis_title": "Normalized Parameter x",
            "y_axis_title": "Response Amplitude"
        }

    return raw_text, spec, thoughts
