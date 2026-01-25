#!/usr/bin/env python3
"""
Project 4: Deutsch and Deutsch-Jozsa Algorithm

The Deutsch algorithm is the first example of quantum speedup!
It determines a global property of a function with fewer queries
than any classical algorithm.

Key Concepts:
- Quantum parallelism (evaluate function on superposition)
- Phase kickback
- Interference to extract global information

Problem Statement (Deutsch):
    Given a function f: {0,1} → {0,1}
    Determine if f is constant (f(0)=f(1)) or balanced (f(0)≠f(1))

    Classical: Must query f twice (once for each input)
    Quantum: Only ONE query needed!

Generalization (Deutsch-Jozsa):
    Given f: {0,1}ⁿ → {0,1}, promised to be constant or balanced
    Classical: Need up to 2^(n-1) + 1 queries (worst case)
    Quantum: Only ONE query needed!
"""

import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import plot_measurement_results
from shared.braket_utils import run_circuit, get_state_vector


def create_oracle(f_type: str, n_qubits: int = 1) -> Callable[[Circuit, List[int], int], Circuit]:
    """
    Create an oracle Uf that implements f(x) via phase kickback.

    The oracle acts as: Uf|x⟩|y⟩ = |x⟩|y ⊕ f(x)⟩

    When y is in state |-⟩ = (|0⟩ - |1⟩)/√2:
    Uf|x⟩|-⟩ = (-1)^f(x)|x⟩|-⟩

    This encodes f(x) in the PHASE, not the computational basis.

    Args:
        f_type: Type of function ("constant_0", "constant_1", "balanced", or "balanced_alt")
        n_qubits: Number of input qubits

    Returns:
        Function that adds oracle gates to a circuit
    """
    def constant_0_oracle(circuit: Circuit, input_qubits: List[int], ancilla: int) -> Circuit:
        """f(x) = 0 for all x: Do nothing"""
        return circuit

    def constant_1_oracle(circuit: Circuit, input_qubits: List[int], ancilla: int) -> Circuit:
        """f(x) = 1 for all x: Always flip ancilla"""
        circuit.x(ancilla)
        return circuit

    def balanced_oracle(circuit: Circuit, input_qubits: List[int], ancilla: int) -> Circuit:
        """f(x) = x (for 1 qubit) or parity(x) for multiple qubits"""
        for qubit in input_qubits:
            circuit.cnot(qubit, ancilla)
        return circuit

    def balanced_alt_oracle(circuit: Circuit, input_qubits: List[int], ancilla: int) -> Circuit:
        """f(x) = NOT x (for 1 qubit) or NOT parity(x)"""
        for qubit in input_qubits:
            circuit.cnot(qubit, ancilla)
        circuit.x(ancilla)
        return circuit

    oracles = {
        "constant_0": constant_0_oracle,
        "constant_1": constant_1_oracle,
        "balanced": balanced_oracle,
        "balanced_alt": balanced_alt_oracle,
    }

    return oracles[f_type]


def deutsch_algorithm(f_type: str) -> Tuple[Circuit, Dict[str, int]]:
    """
    Implement the Deutsch algorithm for a single-bit function.

    Problem: Determine if f: {0,1} → {0,1} is constant or balanced.

    Algorithm:
    1. Initialize |01⟩ (input qubit |0⟩, ancilla |1⟩)
    2. Apply H to both: |+-⟩
    3. Apply oracle Uf
    4. Apply H to input qubit
    5. Measure input qubit

    Result:
    - |0⟩ means f is constant
    - |1⟩ means f is balanced

    Args:
        f_type: "constant_0", "constant_1", "balanced", or "balanced_alt"

    Returns:
        Tuple of (circuit, measurement_counts)
    """
    circuit = Circuit()

    # Step 1: Initialize |01⟩
    circuit.x(1)  # Set ancilla to |1⟩

    # Step 2: Apply Hadamard to both qubits
    circuit.h(0)  # Input: |0⟩ → |+⟩
    circuit.h(1)  # Ancilla: |1⟩ → |-⟩

    # Step 3: Apply oracle
    oracle = create_oracle(f_type, n_qubits=1)
    oracle(circuit, [0], 1)

    # Step 4: Apply Hadamard to input qubit
    circuit.h(0)

    # Step 5: Measure input qubit (qubit 0)
    counts = run_circuit(circuit, shots=100)

    return circuit, counts


def deutsch_jozsa_algorithm(f_type: str, n_qubits: int = 3) -> Tuple[Circuit, Dict[str, int]]:
    """
    Implement the Deutsch-Jozsa algorithm for n-bit functions.

    Problem: Given f: {0,1}ⁿ → {0,1}, promised to be constant or balanced,
             determine which one.

    A function is balanced if f(x) = 1 for exactly half of all inputs.

    Algorithm:
    1. Initialize |0⟩^⊗n |1⟩
    2. Apply H to all qubits
    3. Apply oracle Uf
    4. Apply H to input qubits
    5. Measure input qubits

    Result:
    - All 0s means f is constant
    - Any 1 means f is balanced

    Args:
        f_type: "constant_0", "constant_1", "balanced", or "balanced_alt"
        n_qubits: Number of input qubits

    Returns:
        Tuple of (circuit, measurement_counts)
    """
    circuit = Circuit()
    ancilla = n_qubits  # Ancilla is the last qubit

    # Step 1: Initialize ancilla to |1⟩
    circuit.x(ancilla)

    # Step 2: Apply Hadamard to all qubits
    for i in range(n_qubits + 1):
        circuit.h(i)

    # Step 3: Apply oracle
    oracle = create_oracle(f_type, n_qubits=n_qubits)
    oracle(circuit, list(range(n_qubits)), ancilla)

    # Step 4: Apply Hadamard to input qubits
    for i in range(n_qubits):
        circuit.h(i)

    # Step 5: Measure
    counts = run_circuit(circuit, shots=100)

    return circuit, counts


def analyze_phase_kickback() -> None:
    """
    Explain the phase kickback mechanism in detail.
    """
    print("\n" + "=" * 60)
    print("Phase Kickback: The Secret Sauce")
    print("=" * 60)

    print("""
Phase kickback is how the oracle encodes f(x) into a phase:

Setup:
    - Input register: |x⟩
    - Ancilla: |-⟩ = (|0⟩ - |1⟩)/√2

Oracle action:
    Uf|x⟩|y⟩ = |x⟩|y ⊕ f(x)⟩

When ancilla is |-⟩:
    Uf|x⟩|-⟩ = Uf|x⟩(|0⟩ - |1⟩)/√2
             = |x⟩(|0 ⊕ f(x)⟩ - |1 ⊕ f(x)⟩)/√2

    If f(x) = 0: |x⟩(|0⟩ - |1⟩)/√2 = |x⟩|-⟩
    If f(x) = 1: |x⟩(|1⟩ - |0⟩)/√2 = -|x⟩|-⟩

So: Uf|x⟩|-⟩ = (-1)^f(x)|x⟩|-⟩

The oracle "kicks back" the function value as a PHASE on |x⟩!
The ancilla is unchanged (still |-⟩).

This is crucial: phases can interfere, but classical bits cannot.
    """)


def analyze_deutsch_algorithm() -> None:
    """
    Step-by-step analysis of the Deutsch algorithm.
    """
    print("\n" + "=" * 60)
    print("Deutsch Algorithm: Step-by-Step Analysis")
    print("=" * 60)

    print("""
Initial state: |0⟩|1⟩

After H⊗H:
    |+⟩|-⟩ = (|0⟩ + |1⟩)/√2 ⊗ (|0⟩ - |1⟩)/√2

After oracle (using phase kickback):
    [(-1)^f(0)|0⟩ + (-1)^f(1)|1⟩]/√2 ⊗ |-⟩

Factor out (-1)^f(0):
    (-1)^f(0) · [|0⟩ + (-1)^(f(0)⊕f(1))|1⟩]/√2 ⊗ |-⟩

Define: f(0) ⊕ f(1) = 0 if constant, 1 if balanced

If f is constant (f(0)⊕f(1) = 0):
    Input state: (|0⟩ + |1⟩)/√2 = |+⟩

If f is balanced (f(0)⊕f(1) = 1):
    Input state: (|0⟩ - |1⟩)/√2 = |-⟩

After H on input qubit:
    H|+⟩ = |0⟩  (constant)
    H|-⟩ = |1⟩  (balanced)

Measurement reveals the answer with certainty!
    """)


def classical_vs_quantum_comparison(n_qubits: int = 5) -> None:
    """
    Compare classical and quantum query complexity.
    """
    print("\n" + "=" * 60)
    print("Classical vs Quantum Query Complexity")
    print("=" * 60)

    print(f"""
For n = {n_qubits} input bits:

Classical Algorithm:
    - Worst case: Must query 2^(n-1) + 1 = {2**(n_qubits-1) + 1} times
    - If all queries return same value, could be balanced
    - Only when >50% queried can we be certain

Quantum Algorithm (Deutsch-Jozsa):
    - Always exactly 1 query!
    - Determines constant vs balanced with certainty

Speedup: Exponential in n!
    - Classical: O(2^n) queries
    - Quantum: O(1) queries

This is the first example of quantum advantage.
    """)


def run_all_cases() -> None:
    """
    Run Deutsch algorithm on all possible function types.
    """
    print("\n" + "=" * 60)
    print("Deutsch Algorithm: All Cases")
    print("=" * 60)

    cases = [
        ("constant_0", "constant", "f(0)=0, f(1)=0"),
        ("constant_1", "constant", "f(0)=1, f(1)=1"),
        ("balanced", "balanced", "f(0)=0, f(1)=1"),
        ("balanced_alt", "balanced", "f(0)=1, f(1)=0"),
    ]

    print("\nTesting all function types:")
    print("-" * 50)

    for f_type, expected_type, description in cases:
        circuit, counts = deutsch_algorithm(f_type)

        # Determine result (only look at qubit 0)
        # Sum counts where qubit 0 is '0'
        constant_votes = sum(c for k, c in counts.items() if k[-1] == '0')
        balanced_votes = sum(c for k, c in counts.items() if k[-1] == '1')

        detected_type = "constant" if constant_votes > balanced_votes else "balanced"

        status = "✓" if detected_type == expected_type else "✗"
        print(f"\n  {description}")
        print(f"    Expected: {expected_type}")
        print(f"    Detected: {detected_type} {status}")
        print(f"    Measurements: {counts}")


def run_deutsch_jozsa() -> None:
    """
    Demonstrate the Deutsch-Jozsa algorithm with multiple qubits.
    """
    print("\n" + "=" * 60)
    print("Deutsch-Jozsa Algorithm (n qubits)")
    print("=" * 60)

    for n in [2, 3, 4]:
        print(f"\n--- n = {n} qubits ---")

        for f_type in ["constant_0", "balanced"]:
            circuit, counts = deutsch_jozsa_algorithm(f_type, n_qubits=n)

            # Check if all input qubits measure to 0
            # In our convention, input qubits are leftmost
            all_zeros = "0" * n
            is_constant = any(
                k[:n] == all_zeros
                for k in counts.keys()
            )

            detected = "constant" if is_constant else "balanced"
            expected = "constant" if "constant" in f_type else "balanced"

            print(f"\n  Function type: {f_type}")
            print(f"    Expected: {expected}, Detected: {detected}")
            print(f"    Measurement counts: {counts}")


def visualize_results() -> None:
    """
    Create visualizations of the Deutsch and Deutsch-Jozsa algorithms.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    cases = [
        ("constant_0", "f(x) = 0 (Constant)"),
        ("constant_1", "f(x) = 1 (Constant)"),
        ("balanced", "f(x) = x (Balanced)"),
        ("balanced_alt", "f(x) = NOT x (Balanced)"),
    ]

    for ax, (f_type, title) in zip(axes.flat, cases):
        _, counts = deutsch_algorithm(f_type)

        labels = sorted(counts.keys())
        values = [counts[l] for l in labels]

        ax.bar(labels, values, color='steelblue', edgecolor='black')
        ax.set_xlabel("Measurement Outcome")
        ax.set_ylabel("Counts")
        ax.set_title(title)

    plt.suptitle("Deutsch Algorithm Results", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "deutsch_results.png", dpi=150)
    print("Saved: deutsch_results.png")

    # Deutsch-Jozsa visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, f_type, title in zip(axes, ["constant_0", "balanced"],
                                  ["Constant Function", "Balanced Function"]):
        _, counts = deutsch_jozsa_algorithm(f_type, n_qubits=3)

        labels = sorted(counts.keys())
        values = [counts[l] for l in labels]

        ax.bar(labels, values, color='coral', edgecolor='black')
        ax.set_xlabel("Measurement Outcome")
        ax.set_ylabel("Counts")
        ax.set_title(title)
        ax.tick_params(axis='x', rotation=45)

    plt.suptitle("Deutsch-Jozsa Algorithm (3 qubits)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "deutsch_jozsa_results.png", dpi=150)
    print("Saved: deutsch_jozsa_results.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for Deutsch algorithm demonstration.
    """
    print("=" * 60)
    print("  DEUTSCH & DEUTSCH-JOZSA ALGORITHM")
    print("  Project 4: First Quantum Speedup")
    print("=" * 60)

    # Part 1: Explain phase kickback
    analyze_phase_kickback()

    # Part 2: Analyze the algorithm
    analyze_deutsch_algorithm()

    # Part 3: Run all cases
    run_all_cases()

    # Part 4: Query complexity comparison
    classical_vs_quantum_comparison(5)

    # Part 5: Deutsch-Jozsa generalization
    run_deutsch_jozsa()

    # Part 6: Visualizations
    visualize_results()

    print("\n" + "=" * 60)
    print("🎉 Deutsch Algorithm Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Phase kickback encodes function values as phases
2. Quantum parallelism evaluates f on all inputs simultaneously
3. Interference extracts GLOBAL property (constant vs balanced)
4. Quantum: 1 query vs Classical: 2^(n-1)+1 queries
5. This is an EXPONENTIAL speedup!

Limitation: The problem is somewhat artificial (promise problem).
But it proves quantum computers can outperform classical ones!

Next: Project 5 - Bernstein-Vazirani Algorithm
    """)


if __name__ == "__main__":
    main()
