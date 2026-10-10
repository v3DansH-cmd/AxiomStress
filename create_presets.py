"""
create_presets.py - Generates clean dark-themed placeholder PNGs in assets/
representing handwritten/sketched physics equations for AxiomStress.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

def setup_assets_dir():
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    return assets_dir

def generate_preset_pendulum(assets_dir):
    """
    Generates preset_pendulum.png: theta'' + (g/L)theta = 0
    Chalkboard dark aesthetic with subtle pendulum diagram.
    """
    fig = plt.figure(figsize=(7, 3.5), dpi=200, facecolor="#0b0f19")
    ax = fig.add_subplot(111, facecolor="#0b0f19")
    
    # Draw background grid lines (subtle blueprint/graph paper feel)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-3, 3)
    for x in np.linspace(-5, 5, 21):
        ax.axvline(x, color="#1a2236", linewidth=0.5, alpha=0.6)
    for y in np.linspace(-3, 3, 13):
        ax.axhline(y, color="#1a2236", linewidth=0.5, alpha=0.6)
        
    # Draw subtle pendulum sketch
    pivot_x, pivot_y = -3.2, 1.8
    rod_length = 2.2
    angle = -np.pi / 5
    bob_x = pivot_x + rod_length * np.sin(angle)
    bob_y = pivot_y - rod_length * np.cos(angle)
    
    # Ceiling & pivot
    ax.plot([pivot_x - 0.6, pivot_x + 0.6], [pivot_y, pivot_y], color="#4b5563", lw=2)
    ax.plot([pivot_x], [pivot_y], 'o', color="#9ca3af", markersize=5)
    # Dashed vertical reference
    ax.plot([pivot_x, pivot_x], [pivot_y, pivot_y - 2.4], ':', color="#4b5563", lw=1)
    # Rod & Bob
    ax.plot([pivot_x, bob_x], [pivot_y, bob_y], '-', color="#60a5fa", lw=2)
    ax.plot([bob_x], [bob_y], 'o', color="#38bdf8", markersize=14, alpha=0.85)
    # Arc for theta
    arc_angles = np.linspace(-np.pi/2, angle - np.pi/2, 20)
    ax.plot(pivot_x + 0.8 * np.cos(arc_angles), pivot_y + 0.8 * np.sin(arc_angles), color="#f59e0b", lw=1.2)
    ax.text(pivot_x + 0.25, pivot_y - 0.7, r'$\theta$', color="#f59e0b", fontsize=13, fontweight='bold')
    
    # Main Equation
    ax.text(
        0.5, 0.4,
        r"$\theta'' + \left(\frac{g}{L}\right)\theta = 0$",
        color="#38bdf8",
        fontsize=22,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#1e3a8a", alpha=0.9, lw=1.5)
    )
    
    # Label & Assumption Tag
    ax.text(0.5, -1.1, "Simple Pendulum Linear Approx (sin θ ≈ θ)", color="#94a3b8", fontsize=10, ha="center", style="italic")
    ax.text(0.5, -1.8, "Breakdown: Large amplitude swings (θ > 0.35 rad / ~20°)", color="#f87171", fontsize=9, ha="center")
    
    ax.axis('off')
    plt.tight_layout()
    output_path = os.path.join(assets_dir, "preset_pendulum.png")
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Created: {output_path}")

def generate_preset_relativity(assets_dir):
    """
    Generates preset_relativity.png: p = m * v
    Chalkboard dark aesthetic with classical momentum vs c limit.
    """
    fig = plt.figure(figsize=(7, 3.5), dpi=200, facecolor="#0b0f19")
    ax = fig.add_subplot(111, facecolor="#0b0f19")
    
    ax.set_xlim(-5, 5)
    ax.set_ylim(-3, 3)
    for x in np.linspace(-5, 5, 21):
        ax.axvline(x, color="#1a2236", linewidth=0.5, alpha=0.6)
    for y in np.linspace(-3, 3, 13):
        ax.axhline(y, color="#1a2236", linewidth=0.5, alpha=0.6)
        
    # Diagram: particle velocity arrow approaching c barrier
    ax.arrow(-4.0, 0.5, 2.2, 0, head_width=0.3, head_length=0.3, fc='#ec4899', ec='#ec4899', lw=2)
    ax.text(-3.0, 1.1, r"$\vec{v} \to c$", color="#f472b6", fontsize=12, ha="center")
    ax.plot([-1.2, -1.2], [-2.2, 2.2], '--', color="#ef4444", lw=1.8, alpha=0.8)
    ax.text(-1.1, 2.3, "Speed limit $c$", color="#ef4444", fontsize=9, ha="left")
    
    # Main Equation
    ax.text(
        1.8, 0.4,
        r"$p = m \cdot v$",
        color="#fb7185",
        fontsize=24,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#831843", alpha=0.9, lw=1.5)
    )
    
    # Labels
    ax.text(1.8, -1.1, "Newtonian Momentum Definition", color="#94a3b8", fontsize=10, ha="center", style="italic")
    ax.text(1.8, -1.8, "Breakdown: Relativistic speeds ($v / c > 0.2$)", color="#f87171", fontsize=9, ha="center")
    
    ax.axis('off')
    plt.tight_layout()
    output_path = os.path.join(assets_dir, "preset_relativity.png")
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Created: {output_path}")

def generate_preset_quantum_osc(assets_dir):
    r"""
    Generates preset_quantum_osc.png: d^2\psi/dx^2 + (2m/\hbar^2)(E - 1/2 k x^2)\psi = 0
    Chalkboard dark aesthetic with harmonic potential well and wavefunction.
    """
    fig = plt.figure(figsize=(7, 3.5), dpi=200, facecolor="#0b0f19")
    ax = fig.add_subplot(111, facecolor="#0b0f19")
    
    ax.set_xlim(-5, 5)
    ax.set_ylim(-3, 3)
    for x in np.linspace(-5, 5, 21):
        ax.axvline(x, color="#1a2236", linewidth=0.5, alpha=0.6)
    for y in np.linspace(-3, 3, 13):
        ax.axhline(y, color="#1a2236", linewidth=0.5, alpha=0.6)
        
    # Draw parabolic well V(x) = 1/2 k x^2
    px = np.linspace(-4.4, -1.2, 50)
    py = 0.8 * (px + 2.8)**2 - 1.8
    ax.plot(px, py, color="#818cf8", lw=1.8, alpha=0.85)
    # Ground state wave Gaussian
    gx = np.linspace(-4.0, -1.6, 40)
    gy = -1.2 + 0.9 * np.exp(-((gx + 2.8)/0.5)**2)
    ax.plot(gx, gy, color="#34d399", lw=2)
    ax.text(-2.8, -2.4, r"$V(x) = \frac{1}{2}kx^2$", color="#818cf8", fontsize=9, ha="center")
    
    # Main Equation
    ax.text(
        1.7, 0.4,
        r"$\frac{d^2\psi}{dx^2} + \frac{2m}{\hbar^2}\left(E - \frac{1}{2}kx^2\right)\psi = 0$",
        color="#a7f3d0",
        fontsize=16,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#111827", edgecolor="#065f46", alpha=0.9, lw=1.5)
    )
    
    # Labels
    ax.text(1.7, -1.1, "1D Quantum Harmonic Oscillator (Schrödinger Eq)", color="#94a3b8", fontsize=10, ha="center", style="italic")
    ax.text(1.7, -1.8, "Breakdown: Anharmonicity & high vibrational states", color="#f87171", fontsize=9, ha="center")
    
    ax.axis('off')
    plt.tight_layout()
    output_path = os.path.join(assets_dir, "preset_quantum_osc.png")
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print(f"Created: {output_path}")

def main():
    assets_dir = setup_assets_dir()
    print(f"Generating presets in {assets_dir}...")
    generate_preset_pendulum(assets_dir)
    generate_preset_relativity(assets_dir)
    generate_preset_quantum_osc(assets_dir)
    print("All presets generated successfully.")

if __name__ == "__main__":
    main()
