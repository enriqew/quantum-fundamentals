#!/usr/bin/env python3
"""
Project 1: Hello World - Superposition and Measurement

This is your first quantum program! We demonstrate the most fundamental
quantum phenomena: superposition and measurement.

Key Concepts:
- Qubits start in the |0⟩ state
- The Hadamard gate creates superposition
- Measurement collapses superposition probabilistically

Mathematical Foundation:
    The Hadamard gate H transforms basis states as:
    H|0⟩ = (|0⟩ + |1⟩)/√2 = |+⟩
    H|1⟩ = (|0⟩ - |1⟩)/√2 = |-⟩

    In matrix form:
    H = (1/√2) * [[1,  1],
                  [1, -1]]

    The superposition state |+⟩ has equal probability of measuring 0 or 1:
    P(0) = |⟨0|+⟩|² = |1/√2|² = 0.5
    P(1) = |⟨1|+⟩|² = |1/√2|² = 0.5
"""

import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import (
    plot_measurement_results,
    plot_bloch_sphere,
    visualize_circuit_results,
)
from shared.braket_utils import run_circuit, get_state_vector


def create_superposition_circuit() -> Circuit:
    """
    Create a single-qubit superposition circuit.

    Circuit diagram:
        q0: ──H──

    The Hadamard gate creates an equal superposition:
    |0⟩ → (|0⟩ + |1⟩)/√2

    Returns:
        Braket Circuit object
    """
    circuit = Circuit()

    # Apply Hadamard gate to qubit 0
    circuit.h(0)

    return circuit


def create_multi_qubit_superposition(n_qubits: int = 3) -> Circuit:
    """
    Create n-qubit uniform superposition.

    Applying H⊗ⁿ to |0⟩⊗ⁿ creates:
    |ψ⟩ = (1/√2ⁿ) Σₓ |x⟩

    This is a uniform superposition over all 2ⁿ computational basis states.

    Args:
        n_qubits: Number of qubits

    Returns:
        Braket Circuit object
    """
    circuit = Circuit()

    # Apply Hadamard to all qubits
    for i in range(n_qubits):
        circuit.h(i)

    return circuit


def demonstrate_interference() -> Tuple[Circuit, Dict[str, int]]:
    """
    Demonstrate quantum interference with H-H sequence.

    Two Hadamards cancel out:
    H·H = I (identity)

    So: H(H|0⟩) = H|+⟩ = |0⟩

    This shows that quantum superposition involves coherent
    amplitudes that can interfere constructively or destructively.

    Returns:
        Tuple of (circuit, measurement_counts)
    """
    circuit = Circuit()

    # First Hadamard: |0⟩ → |+⟩
    circuit.h(0)

    # Second Hadamard: |+⟩ → |0⟩
    circuit.h(0)

    # Measure
    circuit_with_measurement = circuit.copy()
    counts = run_circuit(circuit_with_measurement, shots=1000)

    return circuit, counts


def demonstrate_phase_kickback() -> None:
    """
    Demonstrate how relative phase affects interference.

    Compare two circuits:
    1. H → H  (gives |0⟩)
    2. H → Z → H  (gives |1⟩)

    The Z gate adds a relative phase:
    Z|+⟩ = Z(|0⟩ + |1⟩)/√2 = (|0⟩ - |1⟩)/√2 = |-⟩

    Then: H|-⟩ = |1⟩

    This demonstrates that quantum phases are physically meaningful!
    """
    print("\n" + "=" * 60)
    print("Phase Kickback Demonstration")
    print("=" * 60)

    # Circuit 1: H-H
    circuit1 = Circuit().h(0).h(0)
    counts1 = run_circuit(circuit1, shots=1000)

    # Circuit 2: H-Z-H
    circuit2 = Circuit().h(0).z(0).h(0)
    counts2 = run_circuit(circuit2, shots=1000)

    print("\nCircuit 1: H → H")
    print(f"  |0⟩ → H → |+⟩ → H → |0⟩")
    print(f"  Results: {counts1}")

    print("\nCircuit 2: H → Z → H")
    print(f"  |0⟩ → H → |+⟩ → Z → |−⟩ → H → |1⟩")
    print(f"  Results: {counts2}")

    print("\n💡 Insight: The Z gate's phase flip completely changes the outcome!")
    print("   This is because quantum interference depends on phases.")


def analyze_superposition_statistics(n_shots: int = 10000) -> None:
    """
    Statistical analysis of superposition measurements.

    For a fair coin (which is what a measured qubit in |+⟩ is),
    the expected count for each outcome is n/2, with standard
    deviation σ = √(np(1-p)) = √(n/4).

    Args:
        n_shots: Number of measurement shots
    """
    print("\n" + "=" * 60)
    print(f"Statistical Analysis ({n_shots} shots)")
    print("=" * 60)

    circuit = create_superposition_circuit()
    counts = run_circuit(circuit, shots=n_shots)

    count_0 = counts.get('0', 0)
    count_1 = counts.get('1', 0)

    # Theoretical expectations
    expected = n_shots / 2
    std_dev = np.sqrt(n_shots * 0.5 * 0.5)

    print(f"\nMeasurement results:")
    print(f"  |0⟩: {count_0} ({100*count_0/n_shots:.2f}%)")
    print(f"  |1⟩: {count_1} ({100*count_1/n_shots:.2f}%)")

    print(f"\nTheoretical prediction:")
    print(f"  Expected: {expected:.0f} ± {std_dev:.1f} for each outcome")

    z_score_0 = (count_0 - expected) / std_dev
    z_score_1 = (count_1 - expected) / std_dev

    print(f"\nStatistical analysis:")
    print(f"  z-score for |0⟩: {z_score_0:.2f}")
    print(f"  z-score for |1⟩: {z_score_1:.2f}")

    if abs(z_score_0) < 2 and abs(z_score_1) < 2:
        print("  ✓ Results are within 2σ of expected (statistically consistent)")
    else:
        print("  ⚠ Results outside 2σ (unusual but possible)")


def visualize_superposition() -> None:
    """
    Create visualizations of the superposition state.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    # Single qubit superposition
    circuit = create_superposition_circuit()
    state_vector = get_state_vector(circuit)
    counts = run_circuit(circuit, shots=1000)

    print(f"\nState vector after H gate: {state_vector}")
    print(f"Expected: [1/√2, 1/√2] ≈ [0.707, 0.707]")

    # Plot results
    fig = visualize_circuit_results(
        counts,
        state_vector,
        title="Single Qubit Superposition"
    )
    plt.savefig(Path(__file__).parent / "superposition_results.png", dpi=150)
    print("Saved: superposition_results.png")

    # Bloch sphere visualization
    # |+⟩ state is on the equator at x=1
    fig = plot_bloch_sphere(
        theta=np.pi/2,  # On equator
        phi=0,          # Along +x axis
        title="Superposition State |+⟩ on Bloch Sphere"
    )
    plt.savefig(Path(__file__).parent / "bloch_sphere.png", dpi=150)
    print("Saved: bloch_sphere.png")

    # Multi-qubit superposition
    circuit_3q = create_multi_qubit_superposition(3)
    counts_3q = run_circuit(circuit_3q, shots=1000)

    fig = plot_measurement_results(
        counts_3q,
        title="3-Qubit Uniform Superposition",
    )
    plt.savefig(Path(__file__).parent / "multi_qubit_superposition.png", dpi=150)
    print("Saved: multi_qubit_superposition.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for the Hello World quantum program.
    """
    print("=" * 60)
    print("  QUANTUM HELLO WORLD")
    print("  Project 1: Superposition and Measurement")
    print("=" * 60)

    # Part 1: Basic superposition
    print("\n📌 Part 1: Creating Superposition")
    print("-" * 40)

    circuit = create_superposition_circuit()
    print(f"\nCircuit:\n{circuit}")

    # Get state vector (before measurement)
    state_vector = get_state_vector(circuit)
    print(f"\nState vector: {state_vector}")
    print("This represents: (1/√2)|0⟩ + (1/√2)|1⟩")

    # Run measurements
    counts = run_circuit(circuit, shots=1000)
    print(f"\nMeasurement results (1000 shots): {counts}")

    # Part 2: Multi-qubit superposition
    print("\n📌 Part 2: Multi-Qubit Superposition")
    print("-" * 40)

    n_qubits = 3
    circuit_multi = create_multi_qubit_superposition(n_qubits)
    print(f"\n{n_qubits}-qubit circuit:\n{circuit_multi}")

    counts_multi = run_circuit(circuit_multi, shots=1000)
    print(f"\nExpected: Uniform distribution over {2**n_qubits} states")
    print(f"Results: {counts_multi}")

    # Part 3: Interference
    print("\n📌 Part 3: Quantum Interference")
    print("-" * 40)

    circuit_hh, counts_hh = demonstrate_interference()
    print(f"\nH-H circuit:\n{circuit_hh}")
    print(f"Results: {counts_hh}")
    print("\n💡 Two Hadamards cancel out! H·H = I")
    print("   This is constructive interference at |0⟩")

    # Part 4: Phase demonstration
    demonstrate_phase_kickback()

    # Part 5: Statistical analysis
    analyze_superposition_statistics(10000)

    # Part 6: Generate visualizations
    visualize_superposition()

    print("\n" + "=" * 60)
    print("🎉 Hello World Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. The Hadamard gate creates superposition from |0⟩
2. Measurement collapses superposition to definite outcomes
3. Probabilities emerge from |amplitude|²
4. Phases matter! They determine interference patterns
5. Multiple Hadamards on n qubits → 2ⁿ superposed states

Next: Project 2 - Bell State (Entanglement)
    """)


if __name__ == "__main__":
    main()
