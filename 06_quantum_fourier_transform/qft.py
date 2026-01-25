#!/usr/bin/env python3
"""
Project 6: Quantum Fourier Transform (QFT)

The QFT is the quantum analog of the discrete Fourier transform and is
the key component of many quantum algorithms including Shor's algorithm
and quantum phase estimation.

Key Concepts:
- Fourier basis vs computational basis
- Exponential speedup: O(n²) vs O(n·2ⁿ) classical FFT
- Phase rotations and controlled operations

Mathematical Foundation:
    The QFT transforms computational basis states to Fourier basis:

    |j⟩ → (1/√N) Σₖ e^(2πijk/N) |k⟩

    where N = 2ⁿ for n qubits.

    This can be written in product form:
    |j₁j₂...jₙ⟩ → (|0⟩ + e^(2πi·0.jₙ)|1⟩)/√2 ⊗
                  (|0⟩ + e^(2πi·0.jₙ₋₁jₙ)|1⟩)/√2 ⊗
                  ...
                  (|0⟩ + e^(2πi·0.j₁j₂...jₙ)|1⟩)/√2
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import plot_state_vector, visualize_circuit_results
from shared.braket_utils import run_circuit, get_state_vector


def qft_rotations(circuit: Circuit, n: int, qubit_offset: int = 0) -> Circuit:
    """
    Apply QFT rotations (without final swap) to n qubits.

    The QFT uses:
    1. Hadamard gates
    2. Controlled phase rotations R_k = diag(1, e^(2πi/2^k))

    Args:
        circuit: Braket Circuit object
        n: Number of qubits
        qubit_offset: Starting qubit index

    Returns:
        Modified circuit
    """
    if n == 0:
        return circuit

    n_total = n + qubit_offset

    for i in range(n):
        qubit = qubit_offset + i

        # Apply Hadamard to current qubit
        circuit.h(qubit)

        # Apply controlled rotations
        for j in range(i + 1, n):
            control_qubit = qubit_offset + j
            # R_k rotation where k = j - i + 1
            k = j - i + 1
            angle = 2 * np.pi / (2 ** k)
            circuit.cphaseshift(control_qubit, qubit, angle)

    return circuit


def swap_registers(circuit: Circuit, n: int, qubit_offset: int = 0) -> Circuit:
    """
    Swap qubits to reverse their order (required after QFT rotations).

    Args:
        circuit: Braket Circuit object
        n: Number of qubits
        qubit_offset: Starting qubit index

    Returns:
        Modified circuit
    """
    for i in range(n // 2):
        circuit.swap(qubit_offset + i, qubit_offset + n - 1 - i)
    return circuit


def qft(circuit: Circuit, n: int, qubit_offset: int = 0, do_swaps: bool = True) -> Circuit:
    """
    Apply the full Quantum Fourier Transform to n qubits.

    QFT|j⟩ = (1/√N) Σₖ ωⁿᵏ|k⟩ where ω = e^(2πi/N)

    Args:
        circuit: Braket Circuit object
        n: Number of qubits
        qubit_offset: Starting qubit index
        do_swaps: Whether to include final swaps

    Returns:
        Modified circuit
    """
    qft_rotations(circuit, n, qubit_offset)
    if do_swaps:
        swap_registers(circuit, n, qubit_offset)
    return circuit


def inverse_qft(circuit: Circuit, n: int, qubit_offset: int = 0, do_swaps: bool = True) -> Circuit:
    """
    Apply the inverse QFT.

    QFT†|k⟩ = (1/√N) Σⱼ ω⁻ʲᵏ|j⟩

    Args:
        circuit: Braket Circuit object
        n: Number of qubits
        qubit_offset: Starting qubit index
        do_swaps: Whether to include initial swaps

    Returns:
        Modified circuit
    """
    if do_swaps:
        swap_registers(circuit, n, qubit_offset)

    # Apply rotations in reverse order with negative angles
    for i in range(n - 1, -1, -1):
        qubit = qubit_offset + i

        # Apply controlled rotations (in reverse order)
        for j in range(n - 1, i, -1):
            control_qubit = qubit_offset + j
            k = j - i + 1
            angle = -2 * np.pi / (2 ** k)
            circuit.cphaseshift(control_qubit, qubit, angle)

        # Apply Hadamard
        circuit.h(qubit)

    return circuit


def classical_dft_matrix(n: int) -> np.ndarray:
    """
    Compute the classical DFT matrix for comparison.

    DFT_jk = (1/√N) ω^(jk) where ω = e^(2πi/N)

    Args:
        n: Number of qubits (DFT size is 2^n)

    Returns:
        The DFT matrix as a numpy array
    """
    N = 2 ** n
    omega = np.exp(2j * np.pi / N)
    indices = np.arange(N)
    return np.power(omega, np.outer(indices, indices)) / np.sqrt(N)


def verify_qft() -> None:
    """
    Verify QFT matches classical DFT matrix.
    """
    print("\n" + "=" * 60)
    print("Verifying QFT matches DFT matrix")
    print("=" * 60)

    for n in [2, 3, 4]:
        # Build QFT matrix by applying QFT to each basis state
        N = 2 ** n
        qft_matrix = np.zeros((N, N), dtype=complex)

        for j in range(N):
            # Prepare basis state |j⟩
            circuit = Circuit()
            binary = format(j, f'0{n}b')

            for i, bit in enumerate(binary):
                if bit == '1':
                    circuit.x(i)

            # Apply QFT
            qft(circuit, n)

            # Get state vector
            state = get_state_vector(circuit)
            qft_matrix[:, j] = state

        # Compare with classical DFT
        dft_matrix = classical_dft_matrix(n)

        # Check if matrices are close (up to global phase)
        diff = np.abs(np.abs(qft_matrix) - np.abs(dft_matrix))
        max_diff = np.max(diff)

        status = "✓" if max_diff < 1e-10 else "✗"
        print(f"\n  n = {n} qubits (N = {N}):")
        print(f"    Max difference: {max_diff:.2e} {status}")


def demonstrate_qft_on_states() -> None:
    """
    Show QFT action on various input states.
    """
    print("\n" + "=" * 60)
    print("QFT on Various States")
    print("=" * 60)

    n = 3
    N = 2 ** n

    test_states = [
        ("000", "Uniform superposition"),
        ("001", "Small frequency"),
        ("100", "Higher frequency"),
        ("+++", "All-plus state"),
    ]

    for state_str, description in test_states:
        circuit = Circuit()

        # Prepare initial state
        if "+" in state_str:
            for i in range(n):
                circuit.h(i)
        else:
            for i, bit in enumerate(state_str):
                if bit == '1':
                    circuit.x(i)

        initial_state = get_state_vector(circuit)

        # Apply QFT
        qft(circuit, n)
        final_state = get_state_vector(circuit)

        print(f"\n  Initial: |{state_str}⟩ ({description})")
        print(f"    Before QFT: {np.round(initial_state, 3)}")
        print(f"    After QFT:  {np.round(final_state, 3)}")


def analyze_qft_structure() -> None:
    """
    Analyze the mathematical structure of the QFT.
    """
    print("\n" + "=" * 60)
    print("Mathematical Structure of QFT")
    print("=" * 60)

    print("""
The Quantum Fourier Transform on n qubits:

Definition:
    QFT|j⟩ = (1/√2ⁿ) Σₖ₌₀^(2ⁿ-1) e^(2πijk/2ⁿ) |k⟩

Product Representation:
    Let j = j₁2^(n-1) + j₂2^(n-2) + ... + jₙ2⁰

    QFT|j₁j₂...jₙ⟩ = ⊗ᵐ₌₁ⁿ (|0⟩ + e^(2πi·0.jₘjₘ₊₁...jₙ)|1⟩)/√2

    where 0.jₘjₘ₊₁...jₙ = jₘ/2 + jₘ₊₁/4 + ... + jₙ/2^(n-m+1)

Circuit Construction:
    For each qubit k (from 0 to n-1):
    1. Apply Hadamard H
    2. Apply controlled rotations R_m for m = 2, 3, ..., n-k
       where R_m = diag(1, e^(2πi/2ᵐ))

    Finally, swap qubits to reverse order.

Gate Count:
    - Hadamard gates: n
    - Controlled rotations: n(n-1)/2
    - Swap gates: ⌊n/2⌋

    Total: O(n²) gates

Classical FFT:
    - O(n·2ⁿ) operations

Quantum Speedup:
    Exponential! O(n²) vs O(n·2ⁿ)
    """)


def complexity_comparison() -> None:
    """
    Compare QFT vs classical FFT complexity.
    """
    print("\n" + "=" * 60)
    print("Complexity Comparison: QFT vs FFT")
    print("=" * 60)

    print("\n| n qubits | N = 2^n | FFT ops (n·2^n) | QFT gates (n²) | Speedup |")
    print("|----------|---------|-----------------|----------------|---------|")

    for n in [5, 10, 20, 30, 50]:
        N = 2 ** n
        fft_ops = n * N
        qft_gates = n * n

        if fft_ops > 1e9:
            fft_str = f"{fft_ops:.2e}"
        else:
            fft_str = f"{fft_ops:,}"

        speedup = fft_ops / qft_gates if qft_gates > 0 else float('inf')

        print(f"| {n:8} | 2^{n:<5} | {fft_str:>15} | {qft_gates:>14} | {speedup:>7.0f}x |")


def qft_approximation(n: int, precision: int) -> Circuit:
    """
    Create an approximate QFT with limited precision.

    In practice, very small rotations can be ignored because:
    1. They have negligible effect on the final state
    2. They're often below the noise threshold

    Args:
        n: Number of qubits
        precision: Maximum distance for controlled rotations

    Returns:
        Approximate QFT circuit
    """
    circuit = Circuit()

    for i in range(n):
        circuit.h(i)

        for j in range(i + 1, min(i + precision + 1, n)):
            k = j - i + 1
            angle = 2 * np.pi / (2 ** k)
            circuit.cphaseshift(j, i, angle)

    swap_registers(circuit, n)
    return circuit


def demonstrate_qft_precision() -> None:
    """
    Show how QFT precision affects accuracy.
    """
    print("\n" + "=" * 60)
    print("Approximate QFT Analysis")
    print("=" * 60)

    n = 5
    N = 2 ** n

    # Full precision QFT
    circuit_full = Circuit()
    for i, bit in enumerate(format(13, f'0{n}b')):
        if bit == '1':
            circuit_full.x(i)
    qft(circuit_full, n)
    full_state = get_state_vector(circuit_full)

    print(f"\nComparing approximate QFT (n={n} qubits):")
    print("-" * 50)

    for precision in [1, 2, 3, n-1]:
        # Approximate QFT
        circuit_approx = Circuit()
        for i, bit in enumerate(format(13, f'0{n}b')):
            if bit == '1':
                circuit_approx.x(i)

        # Custom approximate QFT
        for i in range(n):
            circuit_approx.h(i)
            for j in range(i + 1, min(i + precision + 1, n)):
                k = j - i + 1
                angle = 2 * np.pi / (2 ** k)
                circuit_approx.cphaseshift(j, i, angle)
        swap_registers(circuit_approx, n)

        approx_state = get_state_vector(circuit_approx)

        # Calculate fidelity
        fidelity = np.abs(np.vdot(full_state, approx_state)) ** 2

        gates_saved = (n * (n - 1) // 2) - (sum(min(precision, n - i - 1) for i in range(n)))

        print(f"\n  Precision {precision}:")
        print(f"    Fidelity: {fidelity:.6f}")
        print(f"    Gates saved: {gates_saved}")


def visualize_qft() -> None:
    """
    Create visualizations of QFT.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    n = 3

    # Show QFT on different basis states
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for j, ax_row in zip([0, 1], axes):
        for k, ax in enumerate(ax_row):
            state_idx = j * 4 + k
            circuit = Circuit()

            # Prepare basis state
            binary = format(state_idx, f'0{n}b')
            for i, bit in enumerate(binary):
                if bit == '1':
                    circuit.x(i)

            # Apply QFT
            qft(circuit, n)
            state = get_state_vector(circuit)

            # Plot amplitudes
            x = np.arange(2 ** n)
            amplitudes = np.abs(state) ** 2

            ax.bar(x, amplitudes, color='steelblue', edgecolor='black')
            ax.set_xlabel('Output state')
            ax.set_ylabel('Probability')
            ax.set_title(f'QFT|{binary}⟩')
            ax.set_xticks(x)
            ax.set_xticklabels([format(i, f'0{n}b') for i in x], rotation=45)
            ax.set_ylim(0, 0.5)

    plt.suptitle("QFT on Computational Basis States (3 qubits)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "qft_basis_states.png", dpi=150)
    print("Saved: qft_basis_states.png")

    # Visualize phase structure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create QFT matrix visualization
    dft = classical_dft_matrix(n)
    phases = np.angle(dft) / np.pi

    im = ax.imshow(phases, cmap='twilight', aspect='auto', vmin=-1, vmax=1)
    ax.set_xlabel('Input state |j⟩')
    ax.set_ylabel('Output state |k⟩')
    ax.set_title('QFT Matrix Phases (units of π)')
    ax.set_xticks(range(2**n))
    ax.set_yticks(range(2**n))
    ax.set_xticklabels([format(i, f'0{n}b') for i in range(2**n)])
    ax.set_yticklabels([format(i, f'0{n}b') for i in range(2**n)])

    plt.colorbar(im, label='Phase (×π)')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "qft_phases.png", dpi=150)
    print("Saved: qft_phases.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for QFT demonstration.
    """
    print("=" * 60)
    print("  QUANTUM FOURIER TRANSFORM")
    print("  Project 6: The Heart of Quantum Algorithms")
    print("=" * 60)

    # Part 1: Show QFT circuit
    print("\n📌 Part 1: QFT Circuit")
    print("-" * 40)

    circuit = Circuit()
    qft(circuit, 3)
    print(f"\n3-qubit QFT circuit:\n{circuit}")

    # Part 2: Verify correctness
    verify_qft()

    # Part 3: Demonstrate on states
    demonstrate_qft_on_states()

    # Part 4: Mathematical structure
    analyze_qft_structure()

    # Part 5: Complexity comparison
    complexity_comparison()

    # Part 6: Approximate QFT
    demonstrate_qft_precision()

    # Part 7: Visualizations
    visualize_qft()

    print("\n" + "=" * 60)
    print("🎉 Quantum Fourier Transform Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. QFT transforms computational basis to Fourier basis
2. Uses O(n²) gates vs O(n·2ⁿ) classical FFT operations
3. Product structure enables efficient implementation
4. Controlled phase rotations encode frequency information
5. Approximate QFT reduces gates with minimal error

Applications:
- Phase estimation (Project 7)
- Shor's algorithm (Project 11)
- Quantum signal processing
- Hamiltonian simulation

Next: Project 7 - Quantum Phase Estimation
    """)


if __name__ == "__main__":
    main()
