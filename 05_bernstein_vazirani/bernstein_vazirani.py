#!/usr/bin/env python3
"""
Project 5: Bernstein-Vazirani Algorithm

The Bernstein-Vazirani algorithm finds a hidden bitstring s with just ONE query,
while classical algorithms need n queries.

Key Concepts:
- Oracle encodes hidden string via dot product
- Phase kickback reveals the string
- Linear vs exponential query complexity

Problem Statement:
    Given oracle access to f(x) = s·x (mod 2) where s is unknown
    Find the hidden string s ∈ {0,1}ⁿ

    Classical: Need n queries (one per bit of s)
    Quantum: Only ONE query needed!

Mathematical Foundation:
    The oracle computes: f(x) = s·x = s₁x₁ ⊕ s₂x₂ ⊕ ... ⊕ sₙxₙ

    After applying Hadamard, oracle, and Hadamard again,
    measurement directly reveals s!
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import plot_measurement_results
from shared.braket_utils import run_circuit


def create_bv_oracle(secret_string: str) -> callable:
    """
    Create an oracle that computes f(x) = s·x (mod 2).

    The oracle implements CNOT gates from each input qubit where s_i = 1
    to the ancilla qubit.

    Args:
        secret_string: The hidden bitstring s (e.g., "1011")

    Returns:
        Function that adds oracle gates to a circuit
    """
    def oracle(circuit: Circuit, input_qubits: List[int], ancilla: int) -> Circuit:
        for i, bit in enumerate(secret_string):
            if bit == '1':
                circuit.cnot(input_qubits[i], ancilla)
        return circuit

    return oracle


def bernstein_vazirani(secret_string: str) -> Tuple[Circuit, Dict[str, int], str]:
    """
    Implement the Bernstein-Vazirani algorithm.

    Algorithm:
    1. Initialize |0⟩^⊗n |1⟩
    2. Apply H to all qubits
    3. Apply oracle U_f
    4. Apply H to input qubits
    5. Measure input qubits → directly gives s!

    Args:
        secret_string: The hidden bitstring to find

    Returns:
        Tuple of (circuit, measurement_counts, detected_string)
    """
    n = len(secret_string)
    circuit = Circuit()
    ancilla = n  # Ancilla is the last qubit

    # Step 1: Initialize ancilla to |1⟩
    circuit.x(ancilla)

    # Step 2: Apply Hadamard to all qubits
    for i in range(n + 1):
        circuit.h(i)

    # Step 3: Apply oracle
    oracle = create_bv_oracle(secret_string)
    oracle(circuit, list(range(n)), ancilla)

    # Step 4: Apply Hadamard to input qubits
    for i in range(n):
        circuit.h(i)

    # Step 5: Measure
    counts = run_circuit(circuit, shots=100)

    # Find the most common result (should be the secret string)
    # Note: We need to extract only the input qubit measurements
    detected = max(counts.keys(), key=lambda k: counts[k])
    # Remove ancilla bit (last position)
    detected_string = detected[:n]

    return circuit, counts, detected_string


def analyze_algorithm() -> None:
    """
    Detailed mathematical analysis of the Bernstein-Vazirani algorithm.
    """
    print("\n" + "=" * 60)
    print("Mathematical Analysis")
    print("=" * 60)

    print("""
The Bernstein-Vazirani algorithm uses the identity:

    H^⊗n |x⟩ = (1/√2ⁿ) Σ_y (-1)^(x·y) |y⟩

where x·y = Σᵢ xᵢyᵢ (mod 2) is the bitwise dot product.

Algorithm Analysis:

Initial state: |0⟩^⊗n |1⟩

After H^⊗(n+1):
    (1/√2ⁿ) Σ_x |x⟩ ⊗ |-⟩

After oracle (phase kickback):
    (1/√2ⁿ) Σ_x (-1)^(s·x) |x⟩ ⊗ |-⟩

After H^⊗n on input register:
    (1/2ⁿ) Σ_x Σ_y (-1)^(s·x + x·y) |y⟩ ⊗ |-⟩
    = (1/2ⁿ) Σ_y [Σ_x (-1)^(x·(s⊕y))] |y⟩ ⊗ |-⟩

The inner sum Σ_x (-1)^(x·z) equals:
    - 2ⁿ if z = 0^n (all terms are +1)
    - 0  if z ≠ 0^n (equal +1 and -1 terms cancel)

Therefore, s ⊕ y = 0^n only when y = s!

Final state: |s⟩ ⊗ |-⟩

Measurement reveals s with probability 1!
    """)


def classical_comparison() -> None:
    """
    Compare quantum and classical approaches.
    """
    print("\n" + "=" * 60)
    print("Classical vs Quantum Comparison")
    print("=" * 60)

    print("""
Classical Algorithm:
    To find s = s₁s₂...sₙ, query f on standard basis vectors:

    f(100...0) = s·(100...0) = s₁
    f(010...0) = s·(010...0) = s₂
    ...
    f(000...1) = s·(000...1) = sₙ

    Total queries: n (one per bit)

Quantum Algorithm:
    Single query reveals entire string s!
    Total queries: 1

Speedup: Linear (n → 1)

Why it works:
    - Quantum parallelism: Oracle evaluated on superposition of ALL x
    - Phase kickback: f(x) encoded in phases
    - Interference: Hadamard transform "decodes" the phases
    - Constructive interference only at |s⟩
    """)


def run_examples() -> None:
    """
    Run the algorithm on various secret strings.
    """
    print("\n" + "=" * 60)
    print("Running Examples")
    print("=" * 60)

    test_strings = [
        "0",
        "1",
        "00",
        "11",
        "101",
        "1011",
        "11010",
        "110101",
    ]

    print("\nFinding hidden strings:")
    print("-" * 50)

    all_correct = True
    for secret in test_strings:
        circuit, counts, detected = bernstein_vazirani(secret)

        match = "✓" if detected == secret else "✗"
        if detected != secret:
            all_correct = False

        print(f"\n  Secret: {secret}")
        print(f"  Detected: {detected} {match}")
        print(f"  Measurements: {counts}")

    if all_correct:
        print("\n🎉 All secret strings correctly identified!")


def demonstrate_single_query_power() -> None:
    """
    Show that we extract n bits of information with 1 query.
    """
    print("\n" + "=" * 60)
    print("Single Query Power")
    print("=" * 60)

    # Use a long secret string
    secret = "10110101"
    n = len(secret)

    circuit, counts, detected = bernstein_vazirani(secret)

    print(f"""
Secret string: {secret} ({n} bits)

Classical approach: Would need {n} queries
Quantum approach: Uses 1 query

Result: {detected}
Match: {"✓ Perfect!" if detected == secret else "✗ Mismatch"}

With a single quantum query, we extracted {n} bits of information
about the hidden string!
    """)


def visualize_results() -> None:
    """
    Create visualizations.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    test_cases = [
        ("101", "Secret: 101"),
        ("1100", "Secret: 1100"),
        ("01010", "Secret: 01010"),
        ("110011", "Secret: 110011"),
    ]

    for ax, (secret, title) in zip(axes.flat, test_cases):
        _, counts, detected = bernstein_vazirani(secret)

        # Take only top outcomes for readability
        sorted_counts = sorted(counts.items(), key=lambda x: -x[1])[:8]
        labels = [x[0] for x in sorted_counts]
        values = [x[1] for x in sorted_counts]

        colors = ['green' if l[:len(secret)] == secret else 'steelblue' for l in labels]

        ax.bar(labels, values, color=colors, edgecolor='black')
        ax.set_xlabel("Measurement Outcome")
        ax.set_ylabel("Counts")
        ax.set_title(f"{title}, Detected: {detected[:len(secret)]}")
        ax.tick_params(axis='x', rotation=45)

    plt.suptitle("Bernstein-Vazirani Algorithm Results", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "bv_results.png", dpi=150)
    print("Saved: bv_results.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for Bernstein-Vazirani algorithm demonstration.
    """
    print("=" * 60)
    print("  BERNSTEIN-VAZIRANI ALGORITHM")
    print("  Project 5: Finding Hidden Strings")
    print("=" * 60)

    # Part 1: Algorithm analysis
    analyze_algorithm()

    # Part 2: Classical comparison
    classical_comparison()

    # Part 3: Run examples
    run_examples()

    # Part 4: Single query power
    demonstrate_single_query_power()

    # Part 5: Visualizations
    visualize_results()

    print("\n" + "=" * 60)
    print("🎉 Bernstein-Vazirani Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Hidden string found with just ONE query
2. Classical requires n queries (one per bit)
3. Phase kickback encodes s·x in phases
4. Hadamard transform reveals s through interference
5. This is a linear speedup (n → 1)

Connection to other algorithms:
- Generalizes Deutsch-Jozsa (s=0 → constant, s≠0 → balanced)
- Simpler version of Simon's algorithm (next step toward Shor's)

Next: Project 6 - Quantum Fourier Transform
    """)


if __name__ == "__main__":
    main()
