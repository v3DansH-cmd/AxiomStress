"""
sim_engine.py - Interactive Mathematical Simulation & Falsification Proof Engine
Powered by Plotly and NumPy.
"""

import re
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, Optional, Tuple

# Safe mathematical environment for string evaluation
SAFE_MATH_ENV = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "maximum": np.maximum,
    "minimum": np.minimum,
    "pi": np.pi,
    "e": np.e,
    "np": np,
}

def clean_expression(expr_str: str) -> str:
    """
    Sanitizes and normalizes math expressions for Python/NumPy evaluation.
    """
    if not expr_str:
        return "x"

    s = str(expr_str).strip()
    
    # Strip any enclosing backticks or markdown
    s = re.sub(r"^`+|`+$", "", s)
    
    # Replace caret ^ with power **
    s = s.replace("^", "**")
    
    # Replace LaTeX commands if any
    s = s.replace(r"\sin", "sin").replace(r"\cos", "cos").replace(r"\tan", "tan")
    s = s.replace(r"\sqrt", "sqrt").replace(r"\exp", "exp").replace(r"\ln", "log")
    s = s.replace(r"\cdot", "*").replace(r"\times", "*")
    s = s.replace(r"\pi", "pi").replace(r"\theta", "x").replace(r"\beta", "x")

    # Replace variable names if specified as something other than x
    # (e.g. theta, v, beta, t) with x
    for var in ["theta", "beta", "v_rel", "psi", "xi"]:
        s = re.sub(rf"\b{var}\b", "x", s)

    return s

def evaluate_expression(expr_str: str, x_vals: np.ndarray) -> Tuple[np.ndarray, Optional[str]]:
    """
    Safely evaluates a 1D expression across an array of x values.
    Returns (y_vals, error_message).
    """
    cleaned = clean_expression(expr_str)
    env = dict(SAFE_MATH_ENV)
    env["x"] = x_vals
    
    try:
        # Evaluate safely in restricted scope
        y_vals = eval(cleaned, {"__builtins__": {}}, env)
        
        # Handle scalar output
        if np.isscalar(y_vals):
            y_vals = np.full_like(x_vals, float(y_vals))
        else:
            y_vals = np.asarray(y_vals, dtype=float)

        # Clean non-finite values for clean plotting
        y_vals = np.where(np.isnan(y_vals), np.nan, y_vals)
        # Cap extreme asymptotes if needed (e.g. > 1e6)
        y_vals = np.where(np.abs(y_vals) > 1e5, np.nan, y_vals)
        return y_vals, None

    except Exception as e:
        # Fallback linear or baseline if evaluation fails
        fallback_y = x_vals.copy()
        return fallback_y, f"Expression evaluation notice: '{cleaned}' ({str(e)})"

def create_falsification_plot(
    spec: Dict[str, Any],
    param_scale: float = 1.0,
    threshold_override: Optional[float] = None,
    num_points: int = 500
) -> go.Figure:
    """
    Generates a high-contrast dark-themed Plotly chart comparing
    the Original vs. Patched equations with divergence shading and
    breakdown threshold markers.
    """
    x_min = float(spec.get("x_min", 0.0))
    x_max = float(spec.get("x_max", 2.0))
    
    # Adjust max range with parameter scaling slider
    scaled_x_max = x_min + (x_max - x_min) * param_scale
    if scaled_x_max <= x_min:
        scaled_x_max = x_min + 1.0

    x_vals = np.linspace(x_min, scaled_x_max, num_points)

    orig_expr = spec.get("original_expr", "x")
    patch_expr = spec.get("patched_expr", "sin(x)")
    
    orig_label = spec.get("original_label", "Original Approximation")
    patch_label = spec.get("patched_label", "Patched Physical Law")
    
    x_title = spec.get("x_axis_title", "Independent Parameter (x)")
    y_title = spec.get("y_axis_title", "System Response (y)")
    
    breakdown_thresh = spec.get("breakdown_threshold", None)
    if threshold_override is not None:
        breakdown_thresh = threshold_override
    elif breakdown_thresh is not None:
        try:
            breakdown_thresh = float(breakdown_thresh)
        except (ValueError, TypeError):
            breakdown_thresh = None

    # Evaluate curves
    y_orig, err_orig = evaluate_expression(orig_expr, x_vals)
    y_patch, err_patch = evaluate_expression(patch_expr, x_vals)

    fig = go.Figure()

    # 1. Subtle Divergence Fill Area (Difference / Error Margin)
    # Filter valid finite points for difference fill
    valid_mask = np.isfinite(y_orig) & np.isfinite(y_patch)
    if np.any(valid_mask):
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_vals[valid_mask], x_vals[valid_mask][::-1]]),
            y=np.concatenate([y_orig[valid_mask], y_patch[valid_mask][::-1]]),
            fill='toself',
            fillcolor='rgba(239, 68, 68, 0.12)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Divergence / Failure Margin',
            hoverinfo='skip',
            showlegend=True
        ))

    # 2. Original Form Curve (Dashed Red Line)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_orig,
        mode='lines',
        name=f"❌ {orig_label}",
        line=dict(color='#ef4444', width=3.2, dash='dash'),
        hovertemplate="<b>Original</b><br>" + x_title + ": %{x:.3f}<br>" + y_title + ": %{y:.3f}<extra></extra>"
    ))

    # 3. Patched Exact Form Curve (Solid Emerald/Green Line)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_patch,
        mode='lines',
        name=f"✅ {patch_label}",
        line=dict(color='#10b981', width=3.5),
        hovertemplate="<b>Patched</b><br>" + x_title + ": %{x:.3f}<br>" + y_title + ": %{y:.3f}<extra></extra>"
    ))

    # 4. Vertical Marker for Breakdown Threshold
    if breakdown_thresh is not None and x_min <= breakdown_thresh <= scaled_x_max:
        # Find y value near threshold for marker anchor
        fig.add_vline(
            x=breakdown_thresh,
            line_width=2.2,
            line_dash="dot",
            line_color="#f59e0b",
            annotation_text=f"⚠️ Breakdown: {breakdown_thresh:.2f}",
            annotation_position="top right",
            annotation_font=dict(color="#f59e0b", size=12, family="monospace"),
            annotation_bgcolor="rgba(17, 24, 39, 0.85)",
            annotation_bordercolor="#f59e0b",
            annotation_borderwidth=1,
            annotation_borderpad=4
        )

    # 5. Plotly Dark Sleek Theme Layout
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#111827",
        title=dict(
            text="<b>Falsification Proof & Divergence Analysis</b>",
            font=dict(size=17, color="#f8fafc", family="sans-serif"),
            x=0.02,
            y=0.96
        ),
        margin=dict(l=60, r=40, t=65, b=55),
        xaxis=dict(
            title=dict(text=f"<b>{x_title}</b>", font=dict(color="#94a3b8", size=13)),
            gridcolor="#1f293d",
            zerolinecolor="#374151",
            tickfont=dict(color="#cbd5e1"),
            showgrid=True,
        ),
        yaxis=dict(
            title=dict(text=f"<b>{y_title}</b>", font=dict(color="#94a3b8", size=13)),
            gridcolor="#1f293d",
            zerolinecolor="#374151",
            tickfont=dict(color="#cbd5e1"),
            showgrid=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            font=dict(color="#e2e8f0", size=11),
            bgcolor="rgba(15, 23, 42, 0.75)",
            bordercolor="#334155",
            borderwidth=1
        ),
        hovermode="x unified",
        height=480
    )

    return fig

def calculate_divergence_metrics(spec: Dict[str, Any], x_val: float) -> Dict[str, float]:
    """
    Computes numerical metrics at a specified probe x value.
    """
    orig_expr = spec.get("original_expr", "x")
    patch_expr = spec.get("patched_expr", "sin(x)")
    
    probe_arr = np.array([float(x_val)])
    y_orig, _ = evaluate_expression(orig_expr, probe_arr)
    y_patch, _ = evaluate_expression(patch_expr, probe_arr)
    
    val_orig = float(y_orig[0]) if np.isfinite(y_orig[0]) else 0.0
    val_patch = float(y_patch[0]) if np.isfinite(y_patch[0]) else 0.0
    
    abs_err = abs(val_orig - val_patch)
    pct_err = (abs_err / (abs(val_patch) + 1e-9)) * 100.0
    
    return {
        "x": x_val,
        "y_original": val_orig,
        "y_patched": val_patch,
        "absolute_divergence": abs_err,
        "percentage_error": pct_err
    }
