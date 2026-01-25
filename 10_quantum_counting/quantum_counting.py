#!/usr/bin/env python3
"""
Project 10: Quantum Counting

Quantum Counting combines Grover's algorithm with Phase Estimation to count
the number of solutions to a search problem without finding them all.

Key Concepts:
- Amplitude estimation
- Grover iterator as a unitary
- Phase estimation to extract Grover angle
- Counting solutions from the angle

Problem Statement:
    Given an oracle f: {0,1}ⁿ → {0,1}, count M = |{x : f(x) = 1}|

    Classical: O(N) queries to count exactly
    Quantum: O(√N) queries for good approximation

Mathematical Foundation:
    The Grover iterator G = D·O has eigenvalues e^{±2iθ}
    where sin²(θ) = M/N (M solutions among N items).

    Phase estimation on G gives θ, from which we compute M.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Callable

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import plot_measurement_results
from shared.braket_utils import run_circuit, get_state_vector


def create_grover_oracle(marked_states: List[str]) -> Callable[[Circuit, int], Circuit]:
    """Create phase oracle for marked states."""
    def oracle(circuit: Circuit, n_qubits: int) -> Circuit:
        for marked in marked_states:
            for i, bit in enumerate(marked):
                if bit == '0':
                    circuit.x(i)

            if n_qubits == 2:
                circuit.cz(0, 1)
            elif n_qubits == 3:
                circuit.h(2)
                circuit.ccnot(0, 1, 2)
                circuit.h(2)

            for i, bit in enumerate(marked):
                if bit == '0':
                    circuit.x(i)
        return circuit
    return oracle


def grover_diffusion(circuit: Circuit, n_qubits: int) -> Circuit:
    """Apply Grover diffusion operator."""
    for i in range(n_qubits):
        circuit.h(i)
    for i in range(n_qubits):
        circuit.x(i)

    if n_qubits == 2:
        circuit.cz(0, 1)
    elif n_qubits == 3:
        circuit.h(2)
        circuit.ccnot(0, 1, 2)
        circuit.h(2)

    for i in range(n_qubits):
        circuit.x(i)
    for i in range(n_qubits):
        circuit.h(i)

    return circuit


def controlled_grover(circuit: Circuit, control: int, search_qubits: List[int],
                     oracle_fn: Callable, power: int = 1) -> Circuit:
    """
    Apply controlled Grover iteration G^power.

    For quantum counting, we need controlled-G^(2^k) operations.
    """
    n_search = len(search_qubits)

    for _ in range(power):
        # Controlled oracle (simplified - apply if control is |1⟩)
        # In real implementation, would need proper controlled gates

        # Apply oracle with control
        oracle_fn(circuit, n_search)

        # Apply diffusion
        grover_diffusion(circuit, n_search)

    return circuit


def inverse_qft(circuit: Circuit, n: int, qubit_offset: int = 0) -> Circuit:
    """Apply inverse QFT."""
    for i in range(n // 2):
        circuit.swap(qubit_offset + i, qubit_offset + n - 1 - i)

    for i in range(n - 1, -1, -1):
        qubit = qubit_offset + i
        for j in range(n - 1, i, -1):
            control_qubit = qubit_offset + j
            k = j - i + 1
            angle = -2 * np.pi / (2 ** k)
            circuit.cphaseshift(control_qubit, qubit, angle)
        circuit.h(qubit)

    return circuit


def quantum_counting_simplified(
    marked_states: List[str],
    n_search: int = 3,
    n_counting: int = 4
) -> Tuple[int, float]:
    """
    Simplified quantum counting demonstration.

    This demonstrates the principle; a full implementation would need
    proper controlled Grover operations.

    Args:
        marked_states: States to count
        n_search: Number of search qubits
        n_counting: Number of counting (precision) qubits

    Returns:
        Tuple of (estimated_count, theoretical_count)
    """
    N = 2 ** n_search
    M_true = len(marked_states)

    # Theoretical Grover angle
    theta = np.arcsin(np.sqrt(M_true / N))

    # Phase estimation would give us θ
    # From θ, we compute M = N·sin²(θ)
    estimated_M = N * np.sin(theta) ** 2

    return int(round(estimated_M)), M_true


def analyze_quantum_counting() -> None:
    """
    Analyze the mathematics of quantum counting.
    """
    print("\n" + "=" * 60)
    print("Mathematical Analysis of Quantum Counting")
    print("=" * 60)

    print("""
Quantum Counting Algorithm:

The key insight: Grover iterator G has eigenvalue structure!

Eigenvalue Analysis:
    G = D·O where D = 2|ψ⟩⟨ψ| - I, O = I - 2|w⟩⟨w|

    Let |w⟩ = superposition of marked states
        |s⟩ = superposition of unmarked states

    In the {|w⟩, |s⟩} basis, G acts as a rotation by 2θ where:
        sin(θ) = √(M/N)

    Eigenvalues of G: e^{±2iθ}
    Eigenstates: |ψ_±⟩ = (|w⟩ ± i|s⟩)/√2

Phase Estimation Connection:
    1. Prepare |ψ⟩ = H^⊗n|0⟩ (uniform superposition)
    2. |ψ⟩ is a superposition of |ψ_+⟩ and |ψ_-⟩
    3. Phase estimation on G gives ±2θ
    4. From θ, compute M = N·sin²(θ)

Precision:
    With t counting qubits: error in θ is O(1/2^t)
    Error in M: O(√(M·N)/2^t)

Complexity:
    O(√N) queries to Grover oracle (same as search)
    But we learn COUNT, not specific solutions!
    """)


def demonstrate_counting() -> None:
    """
    Demonstrate quantum counting on examples.
    """
    print("\n" + "=" * 60)
    print("Quantum Counting Demonstrations")
    print("=" * 60)

    examples = [
        (["101"], 3, "1 marked state"),
        (["00", "11"], 2, "2 marked states"),
        (["001", "010", "100"], 3, "3 marked states"),
        (["0011", "0101", "0110", "1001"], 4, "4 marked states"),
    ]

    print("\n| Example | N | M (true) | Estimated | θ (rad) |")
    print("|---------|---|----------|-----------|---------|")

    for marked, n, description in examples:
        N = 2 ** n
        M_true = len(marked)
        theta = np.arcsin(np.sqrt(M_true / N))

        # In a real implementation, QPE would give us theta
        # Here we compute it directly for demonstration
        estimated_M = N * np.sin(theta) ** 2

        print(f"| {description:<7} | {N:>1} | {M_true:>8} | {estimated_M:>9.2f} | {theta:>7.4f} |")

    print("""
Note: In practice, QPE gives θ with some uncertainty.
Multiple runs or higher precision counting qubits improve accuracy.
    """)


def amplitude_estimation_explanation() -> None:
    """
    Explain amplitude estimation (generalization of counting).
    """
    print("\n" + "=" * 60)
    print("Amplitude Estimation")
    print("=" * 60)

    print("""
Amplitude Estimation is a generalization of Quantum Counting:

Problem:
    Given a unitary A and state |ψ⟩ = A|0⟩ = sin(θ)|good⟩ + cos(θ)|bad⟩
    Estimate θ (equivalently, sin²(θ) = probability of |good⟩)

Classical approach:
    Sample N times, count successes
    Error: O(1/√N)

Quantum approach (Amplitude Estimation):
    Use phase estimation on the Grover-like iterator
    Error: O(1/N) with N queries!

    This is a QUADRATIC speedup in precision!

Applications:
    - Monte Carlo simulation
    - Option pricing in finance
    - Risk analysis
    - Integration problems
    """)


def counting_vs_search() -> None:
    """
    Compare quantum counting with quantum search.
    """
    print("\n" + "=" * 60)
    print("Counting vs Search Comparison")
    print("=" * 60)

    print("""
Quantum Search (Grover):
    - Goal: FIND a marked item
    - Output: One solution x* with f(x*) = 1
    - Queries: O(√(N/M))
    - If M unknown, may overshoot optimal iterations

Quantum Counting:
    - Goal: COUNT how many marked items
    - Output: Estimate of M = |{x : f(x) = 1}|
    - Queries: O(√N)
    - Gives M without finding the solutions!

Synergy:
    1. Run quantum counting to estimate M
    2. Use M to set optimal iterations for search
    3. Run Grover's search with known optimal iterations

This solves the "unknown number of solutions" problem!
    """)


def visualize_counting() -> None:
    """
    Visualize quantum counting concepts.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Grover angle vs number of solutions
    n_qubits = 4
    N = 2 ** n_qubits

    M_values = np.arange(1, N)
    theta_values = np.arcsin(np.sqrt(M_values / N))

    axes[0].plot(M_values, theta_values, 'b-', linewidth=2)
    axes[0].set_xlabel('Number of Solutions (M)')
    axes[0].set_ylabel('Grover Angle θ (radians)')
    axes[0].set_title(f'Grover Angle vs Solutions (N={N})')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=np.pi/4, color='r', linestyle='--', label='θ = π/4')
    axes[0].legend()

    # Plot 2: Precision vs counting qubits
    n_counting_values = np.arange(2, 10)
    errors = [1 / (2 ** t) for t in n_counting_values]

    axes[1].semilogy(n_counting_values, errors, 'go-', markersize=8)
    axes[1].set_xlabel('Number of Counting Qubits')
    axes[1].set_ylabel('Angle Error (radians)')
    axes[1].set_title('Precision vs Counting Qubits')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "counting_analysis.png", dpi=150)
    print("Saved: counting_analysis.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point.
    """
    print("=" * 60)
    print("  QUANTUM COUNTING")
    print("  Project 10: Counting Solutions Quantumly")
    print("=" * 60)

    # Part 1: Mathematical analysis
    analyze_quantum_counting()

    # Part 2: Demonstrations
    demonstrate_counting()

    # Part 3: Amplitude estimation
    amplitude_estimation_explanation()

    # Part 4: Comparison with search
    counting_vs_search()

    # Part 5: Visualizations
    visualize_counting()

    print("\n" + "=" * 60)
    print("🎉 Quantum Counting Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Counting combines Grover with Phase Estimation
2. Grover iterator has eigenvalues e^{±2iθ} where sin²(θ) = M/N
3. QPE extracts θ, giving us M = N·sin²(θ)
4. Complexity: O(√N) queries for counting
5. Amplitude estimation generalizes this to probability estimation

Next: Project 11 - Shor's Algorithm (The Big One!)
    """)


if __name__ == "__main__":
    main()
