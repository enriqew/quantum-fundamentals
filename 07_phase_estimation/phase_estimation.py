#!/usr/bin/env python3
"""
Project 7: Quantum Phase Estimation (QPE)

QPE is a fundamental subroutine that extracts eigenvalues from unitary operators.
It's the core of Shor's algorithm and many quantum simulation algorithms.

Key Concepts:
- Eigenvalue extraction via controlled operations
- Inverse QFT to read out phase
- Precision scales with number of qubits

Problem Statement:
    Given a unitary U and an eigenstate |ψ⟩ with U|ψ⟩ = e^(2πiφ)|ψ⟩
    Estimate the phase φ ∈ [0, 1)

Mathematical Foundation:
    The algorithm uses controlled-U^(2^k) operations to encode φ in phases,
    then inverse QFT to convert these phases to a binary representation.
"""

import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import plot_measurement_results
from shared.braket_utils import run_circuit, get_state_vector
from shared.math_utils import continued_fraction, convergents


def inverse_qft(circuit: Circuit, n: int, qubit_offset: int = 0) -> Circuit:
    """
    Apply inverse QFT to n qubits.
    """
    # Swap qubits
    for i in range(n // 2):
        circuit.swap(qubit_offset + i, qubit_offset + n - 1 - i)

    # Inverse rotations
    for i in range(n - 1, -1, -1):
        qubit = qubit_offset + i

        for j in range(n - 1, i, -1):
            control_qubit = qubit_offset + j
            k = j - i + 1
            angle = -2 * np.pi / (2 ** k)
            circuit.cphaseshift(control_qubit, qubit, angle)

        circuit.h(qubit)

    return circuit


def controlled_u_power(
    circuit: Circuit,
    control: int,
    target: int,
    theta: float,
    power: int
) -> Circuit:
    """
    Apply controlled-U^power where U is a Z-rotation by theta.

    This is a simple example; real applications use more complex unitaries.

    Args:
        circuit: Braket Circuit
        control: Control qubit
        target: Target qubit
        theta: Rotation angle (eigenvalue is e^(i*theta))
        power: Power to raise U to
    """
    circuit.cphaseshift(control, target, theta * power)
    return circuit


def phase_estimation(
    theta: float,
    n_precision: int = 4
) -> Tuple[Circuit, Dict[str, int], float]:
    """
    Quantum Phase Estimation for a simple phase rotation.

    For U = diag(1, e^(iθ)) with eigenvalue e^(iθ) on |1⟩:
    - Prepare eigenstate |1⟩ on target qubit
    - Use n_precision qubits to estimate φ = θ/(2π)

    Args:
        theta: The phase angle (0 to 2π)
        n_precision: Number of precision qubits

    Returns:
        Tuple of (circuit, counts, estimated_phase)
    """
    circuit = Circuit()
    n_total = n_precision + 1  # precision qubits + target qubit
    target = n_precision  # Target qubit is last

    # Step 1: Prepare eigenstate |1⟩ on target
    circuit.x(target)

    # Step 2: Apply Hadamard to all precision qubits
    for i in range(n_precision):
        circuit.h(i)

    # Step 3: Apply controlled-U^(2^k) operations
    for k in range(n_precision):
        power = 2 ** (n_precision - 1 - k)
        controlled_u_power(circuit, k, target, theta, power)

    # Step 4: Apply inverse QFT to precision register
    inverse_qft(circuit, n_precision, qubit_offset=0)

    # Step 5: Measure
    counts = run_circuit(circuit, shots=1000)

    # Extract most likely measurement (precision qubits only)
    def extract_precision_bits(outcome: str) -> str:
        return outcome[:n_precision]

    precision_counts = {}
    for outcome, count in counts.items():
        bits = extract_precision_bits(outcome)
        precision_counts[bits] = precision_counts.get(bits, 0) + count

    most_likely = max(precision_counts.keys(), key=lambda k: precision_counts[k])
    measured_int = int(most_likely, 2)
    estimated_phase = measured_int / (2 ** n_precision)

    return circuit, counts, estimated_phase


def analyze_qpe_math() -> None:
    """
    Mathematical analysis of QPE.
    """
    print("\n" + "=" * 60)
    print("Mathematical Analysis of QPE")
    print("=" * 60)

    print("""
Quantum Phase Estimation Algorithm:

Given: Unitary U with eigenstate |ψ⟩ and eigenvalue e^(2πiφ)
Goal: Estimate φ to n bits of precision

Initial state:
    |0⟩^⊗n |ψ⟩

After Hadamards on precision register:
    (1/√2ⁿ) Σⱼ |j⟩ |ψ⟩

After controlled-U^(2^k) operations:
    For each precision qubit k, apply U^(2^k) controlled on qubit k.

    |j⟩|ψ⟩ → |j⟩ U^j |ψ⟩ = e^(2πijφ)|j⟩|ψ⟩

    Full state: (1/√2ⁿ) Σⱼ e^(2πijφ) |j⟩ |ψ⟩

This is the QFT of |φ⟩ (in the Fourier basis)!

After inverse QFT:
    |φ̃⟩|ψ⟩ where φ̃ is the n-bit binary approximation of φ

Measurement gives the binary representation of φ.

Key Insight:
    - Controlled-U^(2^k) encodes φ·2^k in the phase of qubit k
    - These phases form a Fourier pattern
    - Inverse QFT "decodes" this pattern to give φ in binary
    """)


def precision_analysis() -> None:
    """
    Analyze how precision affects accuracy.
    """
    print("\n" + "=" * 60)
    print("Precision Analysis")
    print("=" * 60)

    true_phase = 0.3  # φ = 0.3
    theta = 2 * np.pi * true_phase

    print(f"\nTrue phase: φ = {true_phase}")
    print("\n| Precision bits | Best estimate | Error |")
    print("|----------------|---------------|-------|")

    for n in range(2, 8):
        _, counts, estimated = phase_estimation(theta, n_precision=n)
        error = abs(estimated - true_phase)

        print(f"| {n:14} | {estimated:.6f}      | {error:.6f} |")

    print("""
For n precision bits:
    - Maximum error: 1/(2^n)
    - Success probability: 4/π² ≈ 0.405 (for exact representation)
    - Higher with inexact phases due to interference
    """)


def demonstrate_exact_phase() -> None:
    """
    Demonstrate QPE with an exactly representable phase.
    """
    print("\n" + "=" * 60)
    print("Exact Phase Representation")
    print("=" * 60)

    # Phase that's exactly representable with 3 bits: φ = 3/8
    true_phase = 3/8
    theta = 2 * np.pi * true_phase

    print(f"\nPhase φ = 3/8 = 0.375 (exactly 0.011 in binary)")

    _, counts, estimated = phase_estimation(theta, n_precision=3)

    print(f"\nMeasurement results:")
    for outcome, count in sorted(counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  {outcome}: {count}")

    print(f"\nEstimated phase: {estimated}")
    print(f"True phase: {true_phase}")
    print(f"Error: {abs(estimated - true_phase)}")


def visualize_qpe() -> None:
    """
    Visualize QPE results.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    test_phases = [0.25, 0.375, 0.333, 0.7]

    for ax, true_phase in zip(axes.flat, test_phases):
        theta = 2 * np.pi * true_phase
        _, counts, estimated = phase_estimation(theta, n_precision=4)

        # Extract precision bits only
        precision_counts = {}
        for outcome, count in counts.items():
            bits = outcome[:4]
            precision_counts[bits] = precision_counts.get(bits, 0) + count

        sorted_counts = sorted(precision_counts.items(), key=lambda x: -x[1])[:8]
        labels = [x[0] for x in sorted_counts]
        values = [x[1] for x in sorted_counts]

        ax.bar(labels, values, color='steelblue', edgecolor='black')
        ax.set_xlabel("Measurement")
        ax.set_ylabel("Counts")
        ax.set_title(f"φ = {true_phase:.3f}, Est = {estimated:.3f}")
        ax.tick_params(axis='x', rotation=45)

    plt.suptitle("QPE Results for Various Phases (4-bit precision)",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "qpe_results.png", dpi=150)
    print("Saved: qpe_results.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point.
    """
    print("=" * 60)
    print("  QUANTUM PHASE ESTIMATION")
    print("  Project 7: Extracting Eigenvalues")
    print("=" * 60)

    # Part 1: Mathematical analysis
    analyze_qpe_math()

    # Part 2: Exact phase
    demonstrate_exact_phase()

    # Part 3: Precision analysis
    precision_analysis()

    # Part 4: Visualizations
    visualize_qpe()

    print("\n" + "=" * 60)
    print("🎉 Phase Estimation Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. QPE extracts eigenvalues from unitary operators
2. Uses controlled-U^(2^k) to encode phase in qubit phases
3. Inverse QFT converts phases to binary representation
4. Precision: n bits gives error ≤ 1/2^n
5. Foundation for Shor's algorithm!

Next: Project 8 - Grover's Search Algorithm
    """)


if __name__ == "__main__":
    main()
