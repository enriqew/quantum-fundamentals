"""
Visualization utilities for quantum computing projects.

Provides functions for visualizing:
- Measurement results as histograms
- Quantum states on the Bloch sphere
- State vector amplitudes and phases
- Probability distributions
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns


def plot_measurement_results(
    counts: Dict[str, int],
    title: str = "Measurement Results",
    figsize: Tuple[int, int] = (10, 6),
    color: str = "steelblue",
    show_probabilities: bool = True,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot measurement results as a bar chart.

    Args:
        counts: Dictionary mapping bitstrings to counts
        title: Plot title
        figsize: Figure size (width, height)
        color: Bar color
        show_probabilities: If True, show probabilities instead of raw counts
        save_path: If provided, save figure to this path

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Sort by bitstring for consistent ordering
    sorted_items = sorted(counts.items())
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    if show_probabilities:
        total = sum(values)
        values = [v / total for v in values]
        ylabel = "Probability"
    else:
        ylabel = "Counts"

    bars = ax.bar(labels, values, color=color, edgecolor='black', linewidth=1.2)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f'{val:.3f}' if show_probabilities else f'{val}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center', va='bottom',
            fontsize=10
        )

    ax.set_xlabel("Measurement Outcome", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45 if len(labels) > 8 else 0)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_bloch_sphere(
    theta: float,
    phi: float,
    title: str = "Bloch Sphere",
    figsize: Tuple[int, int] = (8, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot a quantum state on the Bloch sphere.

    The state |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩ is represented as
    a point (sin(θ)cos(φ), sin(θ)sin(φ), cos(θ)) on the unit sphere.

    Args:
        theta: Polar angle (0 to π)
        phi: Azimuthal angle (0 to 2π)
        title: Plot title
        figsize: Figure size
        save_path: If provided, save figure to this path

    Returns:
        matplotlib Figure object
    """
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')

    # Draw the Bloch sphere wireframe
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = np.outer(np.cos(u), np.sin(v))
    y_sphere = np.outer(np.sin(u), np.sin(v))
    z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_wireframe(x_sphere, y_sphere, z_sphere,
                      color='lightgray', alpha=0.3, linewidth=0.5)

    # Draw axes
    ax.quiver(0, 0, 0, 1.3, 0, 0, color='red', alpha=0.6, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 1.3, 0, color='green', alpha=0.6, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, 0, 0, 1.3, color='blue', alpha=0.6, arrow_length_ratio=0.1)

    # Label axes and key states
    ax.text(1.4, 0, 0, r'$|+\rangle$', fontsize=12)
    ax.text(-1.4, 0, 0, r'$|-\rangle$', fontsize=12)
    ax.text(0, 1.4, 0, r'$|+i\rangle$', fontsize=12)
    ax.text(0, -1.4, 0, r'$|-i\rangle$', fontsize=12)
    ax.text(0, 0, 1.4, r'$|0\rangle$', fontsize=12, fontweight='bold')
    ax.text(0, 0, -1.4, r'$|1\rangle$', fontsize=12, fontweight='bold')

    # Plot the state vector
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    ax.quiver(0, 0, 0, x, y, z, color='purple', linewidth=3,
              arrow_length_ratio=0.15)
    ax.scatter([x], [y], [z], color='purple', s=100, marker='o')

    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Equal aspect ratio
    ax.set_box_aspect([1, 1, 1])

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_state_vector(
    amplitudes: np.ndarray,
    n_qubits: Optional[int] = None,
    title: str = "State Vector",
    figsize: Tuple[int, int] = (12, 5),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot state vector amplitudes and phases.

    Args:
        amplitudes: Complex numpy array of state amplitudes
        n_qubits: Number of qubits (inferred if not provided)
        title: Plot title
        figsize: Figure size
        save_path: If provided, save figure to this path

    Returns:
        matplotlib Figure object
    """
    if n_qubits is None:
        n_qubits = int(np.log2(len(amplitudes)))

    n_states = len(amplitudes)
    labels = [format(i, f'0{n_qubits}b') for i in range(n_states)]

    magnitudes = np.abs(amplitudes)
    phases = np.angle(amplitudes)
    probabilities = magnitudes ** 2

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Plot probabilities
    colors = cm.viridis(phases / (2 * np.pi) + 0.5)
    bars = axes[0].bar(labels, probabilities, color=colors, edgecolor='black')
    axes[0].set_xlabel("Basis State", fontsize=11)
    axes[0].set_ylabel("Probability |α|²", fontsize=11)
    axes[0].set_title("Probability Distribution", fontsize=12, fontweight='bold')
    axes[0].tick_params(axis='x', rotation=45 if n_states > 8 else 0)

    # Plot phases (only for non-zero amplitudes)
    mask = magnitudes > 1e-10
    phases_filtered = phases[mask]
    labels_filtered = [labels[i] for i in range(n_states) if mask[i]]

    if len(phases_filtered) > 0:
        axes[1].bar(labels_filtered, phases_filtered / np.pi,
                   color='coral', edgecolor='black')
        axes[1].set_xlabel("Basis State", fontsize=11)
        axes[1].set_ylabel("Phase (×π radians)", fontsize=11)
        axes[1].set_title("Phases of Non-zero Amplitudes", fontsize=12, fontweight='bold')
        axes[1].tick_params(axis='x', rotation=45 if len(labels_filtered) > 8 else 0)
        axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def plot_probability_distribution(
    probabilities: Dict[str, float],
    theoretical: Optional[Dict[str, float]] = None,
    title: str = "Probability Distribution",
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot probability distribution with optional theoretical comparison.

    Args:
        probabilities: Measured/simulated probabilities
        theoretical: Theoretical probabilities for comparison
        title: Plot title
        figsize: Figure size
        save_path: If provided, save figure to this path

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    sorted_items = sorted(probabilities.items())
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    x = np.arange(len(labels))
    width = 0.35 if theoretical else 0.7

    bars1 = ax.bar(x - width/2 if theoretical else x, values, width,
                   label='Measured', color='steelblue', edgecolor='black')

    if theoretical:
        theo_values = [theoretical.get(label, 0) for label in labels]
        bars2 = ax.bar(x + width/2, theo_values, width,
                      label='Theoretical', color='coral', edgecolor='black')

    ax.set_xlabel("Measurement Outcome", fontsize=12)
    ax.set_ylabel("Probability", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45 if len(labels) > 8 else 0)

    if theoretical:
        ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig


def visualize_circuit_results(
    counts: Dict[str, int],
    state_vector: Optional[np.ndarray] = None,
    title: str = "Circuit Analysis",
    figsize: Tuple[int, int] = (14, 5),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Comprehensive visualization of circuit results.

    Args:
        counts: Measurement counts
        state_vector: Optional state vector for additional analysis
        title: Plot title
        figsize: Figure size
        save_path: If provided, save figure to this path

    Returns:
        matplotlib Figure object
    """
    has_sv = state_vector is not None
    n_plots = 3 if has_sv else 1

    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    if n_plots == 1:
        axes = [axes]

    # Plot 1: Measurement histogram
    sorted_items = sorted(counts.items())
    labels = [item[0] for item in sorted_items]
    total = sum(counts.values())
    probs = [item[1] / total for item in sorted_items]

    axes[0].bar(labels, probs, color='steelblue', edgecolor='black')
    axes[0].set_xlabel("Outcome")
    axes[0].set_ylabel("Probability")
    axes[0].set_title("Measurement Results")
    axes[0].tick_params(axis='x', rotation=45 if len(labels) > 8 else 0)

    if has_sv:
        n_qubits = int(np.log2(len(state_vector)))
        sv_labels = [format(i, f'0{n_qubits}b') for i in range(len(state_vector))]

        # Plot 2: State vector magnitudes
        mags = np.abs(state_vector) ** 2
        axes[1].bar(sv_labels, mags, color='coral', edgecolor='black')
        axes[1].set_xlabel("Basis State")
        axes[1].set_ylabel("Probability")
        axes[1].set_title("State Vector Probabilities")
        axes[1].tick_params(axis='x', rotation=45 if len(sv_labels) > 8 else 0)

        # Plot 3: Complex plane representation
        real_parts = state_vector.real
        imag_parts = state_vector.imag
        colors = cm.hsv(np.linspace(0, 1, len(state_vector)))

        for i, (r, im, c, lbl) in enumerate(zip(real_parts, imag_parts, colors, sv_labels)):
            if np.abs(r) > 1e-10 or np.abs(im) > 1e-10:
                axes[2].annotate('', xy=(r, im), xytext=(0, 0),
                               arrowprops=dict(arrowstyle='->', color=c, lw=2))
                axes[2].scatter([r], [im], c=[c], s=100, zorder=5)
                axes[2].annotate(lbl, (r, im), fontsize=8,
                               xytext=(5, 5), textcoords='offset points')

        axes[2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[2].axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        axes[2].set_xlabel("Real")
        axes[2].set_ylabel("Imaginary")
        axes[2].set_title("Amplitudes in Complex Plane")
        axes[2].set_aspect('equal')

        # Draw unit circle
        theta = np.linspace(0, 2*np.pi, 100)
        axes[2].plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    return fig
