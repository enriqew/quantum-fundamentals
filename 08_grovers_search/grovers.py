#!/usr/bin/env python3
"""
Project 8: Grover's Search Algorithm

Grover's algorithm provides a quadratic speedup for unstructured search.
Find a marked item in an unsorted database of N items with O(√N) queries
instead of O(N) classically.

Key Concepts:
- Amplitude amplification
- Oracle and diffusion operators
- Optimal number of iterations
- Geometric interpretation

Problem Statement:
    Given oracle access to f: {0,1}ⁿ → {0,1} where f(x) = 1 for exactly one x*
    Find x* using as few oracle calls as possible.

    Classical: O(N) queries (must check ~N/2 items on average)
    Quantum: O(√N) queries
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

from shared.visualization import plot_measurement_results, plot_state_vector
from shared.braket_utils import run_circuit, get_state_vector


def create_oracle(marked_states: List[str]) -> Callable[[Circuit, int], Circuit]:
    """
    Create an oracle that marks specified states with a phase flip.

    The oracle implements: O|x⟩ = (-1)^f(x)|x⟩
    where f(x) = 1 if x is a marked state.

    Args:
        marked_states: List of bitstrings to mark (e.g., ["101", "011"])

    Returns:
        Function that applies oracle to a circuit
    """
    def oracle(circuit: Circuit, n_qubits: int) -> Circuit:
        for marked in marked_states:
            # Apply X gates to qubits that should be 0 in the marked state
            for i, bit in enumerate(marked):
                if bit == '0':
                    circuit.x(i)

            # Multi-controlled Z gate (flip phase if all qubits are 1)
            if n_qubits == 1:
                circuit.z(0)
            elif n_qubits == 2:
                circuit.cz(0, 1)
            else:
                # For n > 2, use multi-controlled Z
                # Decompose using ancilla or direct multi-controlled gate
                # Here we use a simplified approach with CCZ for n=3
                if n_qubits == 3:
                    circuit.ccnot(0, 1, 2)
                    circuit.cz(1, 2)
                    circuit.ccnot(0, 1, 2)
                else:
                    # General case: use phase oracle construction
                    # Apply multi-controlled Z via decomposition
                    controls = list(range(n_qubits - 1))
                    target = n_qubits - 1
                    circuit.h(target)
                    # Apply multi-controlled NOT
                    for i in range(n_qubits - 2, -1, -1):
                        circuit.ccnot(i, (i + 1) % (n_qubits - 1) if i < n_qubits - 2 else target,
                                      target if i == n_qubits - 2 else (i + 2) % n_qubits)
                    circuit.h(target)

            # Undo X gates
            for i, bit in enumerate(marked):
                if bit == '0':
                    circuit.x(i)

        return circuit

    return oracle


def diffusion_operator(circuit: Circuit, n_qubits: int) -> Circuit:
    """
    Apply the Grover diffusion operator.

    D = 2|ψ⟩⟨ψ| - I where |ψ⟩ = H^⊗n|0⟩^⊗n

    This can be implemented as: H^⊗n · (2|0⟩⟨0| - I) · H^⊗n

    The operator 2|0⟩⟨0| - I flips the phase of all states except |0...0⟩.

    Args:
        circuit: Braket Circuit
        n_qubits: Number of qubits
    """
    # Apply H to all qubits
    for i in range(n_qubits):
        circuit.h(i)

    # Apply X to all qubits (to mark |0...0⟩ as |1...1⟩)
    for i in range(n_qubits):
        circuit.x(i)

    # Multi-controlled Z (phase flip on |1...1⟩)
    if n_qubits == 1:
        circuit.z(0)
    elif n_qubits == 2:
        circuit.cz(0, 1)
    elif n_qubits == 3:
        # CCZ implementation
        circuit.h(2)
        circuit.ccnot(0, 1, 2)
        circuit.h(2)
    else:
        # For larger n, decompose
        circuit.h(n_qubits - 1)
        # Toffoli cascade
        circuit.ccnot(0, 1, n_qubits - 1)
        circuit.h(n_qubits - 1)

    # Undo X gates
    for i in range(n_qubits):
        circuit.x(i)

    # Apply H to all qubits
    for i in range(n_qubits):
        circuit.h(i)

    return circuit


def grover_iteration(
    circuit: Circuit,
    n_qubits: int,
    oracle_fn: Callable[[Circuit, int], Circuit]
) -> Circuit:
    """
    Apply one Grover iteration (oracle + diffusion).

    Args:
        circuit: Braket Circuit
        n_qubits: Number of qubits
        oracle_fn: Oracle function

    Returns:
        Modified circuit
    """
    oracle_fn(circuit, n_qubits)
    diffusion_operator(circuit, n_qubits)
    return circuit


def optimal_iterations(n_qubits: int, n_marked: int = 1) -> int:
    """
    Calculate the optimal number of Grover iterations.

    The optimal number is approximately (π/4)√(N/M) where
    N = 2^n is the search space size and M is the number of marked items.

    Args:
        n_qubits: Number of qubits
        n_marked: Number of marked states

    Returns:
        Optimal number of iterations
    """
    N = 2 ** n_qubits
    return int(np.round(np.pi / 4 * np.sqrt(N / n_marked)))


def grovers_algorithm(
    marked_states: List[str],
    n_qubits: int = None,
    n_iterations: int = None
) -> Tuple[Circuit, Dict[str, int], str]:
    """
    Run Grover's search algorithm.

    Args:
        marked_states: States to search for
        n_qubits: Number of qubits (inferred from marked_states if None)
        n_iterations: Number of iterations (optimal if None)

    Returns:
        Tuple of (circuit, counts, most_likely_result)
    """
    if n_qubits is None:
        n_qubits = len(marked_states[0])

    if n_iterations is None:
        n_iterations = optimal_iterations(n_qubits, len(marked_states))

    circuit = Circuit()

    # Step 1: Initialize uniform superposition
    for i in range(n_qubits):
        circuit.h(i)

    # Step 2: Apply Grover iterations
    oracle = create_oracle(marked_states)
    for _ in range(n_iterations):
        grover_iteration(circuit, n_qubits, oracle)

    # Step 3: Measure
    counts = run_circuit(circuit, shots=1000)

    # Find most likely result
    most_likely = max(counts.keys(), key=lambda k: counts[k])

    return circuit, counts, most_likely


def analyze_grover_math() -> None:
    """
    Mathematical analysis of Grover's algorithm.
    """
    print("\n" + "=" * 60)
    print("Mathematical Analysis of Grover's Algorithm")
    print("=" * 60)

    print("""
Grover's algorithm amplifies the amplitude of marked states.

Geometric Interpretation:
    Let |w⟩ = marked state, |s⟩ = uniform superposition of unmarked states
    Initial state: |ψ⟩ = sin(θ)|w⟩ + cos(θ)|s⟩
    where sin(θ) = √(M/N) for M marked items among N total

    Grover iteration rotates by 2θ toward |w⟩:
    G|ψ⟩ = sin(3θ)|w⟩ + cos(3θ)|s⟩

    After k iterations:
    G^k|ψ⟩ = sin((2k+1)θ)|w⟩ + cos((2k+1)θ)|s⟩

    Maximum probability when (2k+1)θ = π/2:
    k ≈ (π/4)√(N/M)

Algorithm Components:
    1. Oracle O: Marks solution states
       O|x⟩ = (-1)^f(x)|x⟩

    2. Diffusion D: Reflects about the mean
       D = 2|ψ⟩⟨ψ| - I = H^⊗n(2|0⟩⟨0| - I)H^⊗n

    Grover iteration: G = D · O

Success Probability:
    After optimal iterations: P(success) ≥ 1 - M/N
    For single marked item: P ≥ 1 - 1/N ≈ 1
    """)


def complexity_analysis() -> None:
    """
    Compare quantum vs classical search complexity.
    """
    print("\n" + "=" * 60)
    print("Complexity Analysis")
    print("=" * 60)

    print("\n| n qubits | N = 2^n | Classical | Quantum | Speedup |")
    print("|----------|---------|-----------|---------|---------|")

    for n in [5, 10, 15, 20, 25, 30]:
        N = 2 ** n
        classical = N // 2  # Average case
        quantum = optimal_iterations(n)
        speedup = classical / quantum if quantum > 0 else float('inf')

        print(f"| {n:8} | 2^{n:<5} | {classical:>9,} | {quantum:>7} | {speedup:>7.0f}x |")

    print("""
Key insights:
- Quantum speedup is QUADRATIC: O(√N) vs O(N)
- For N = 10^6, quantum needs ~1000 iterations vs 500,000 classical
- This is the best possible for unstructured search (proven lower bound)
    """)


def demonstrate_grover() -> None:
    """
    Demonstrate Grover's algorithm on various examples.
    """
    print("\n" + "=" * 60)
    print("Grover's Algorithm Demonstrations")
    print("=" * 60)

    examples = [
        (["11"], 2, "2 qubits, single target"),
        (["101"], 3, "3 qubits, single target"),
        (["0110"], 4, "4 qubits, single target"),
        (["00", "11"], 2, "2 qubits, two targets"),
    ]

    for marked, n, description in examples:
        print(f"\n{description}:")
        print(f"  Searching for: {marked}")

        n_iter = optimal_iterations(n, len(marked))
        print(f"  Optimal iterations: {n_iter}")

        _, counts, result = grovers_algorithm(marked, n, n_iter)

        # Calculate success probability
        success = sum(counts.get(m, 0) for m in marked)
        total = sum(counts.values())
        prob = success / total

        print(f"  Most likely result: {result}")
        print(f"  Success probability: {prob:.2%}")
        print(f"  Top results: {dict(sorted(counts.items(), key=lambda x: -x[1])[:4])}")


def iteration_sweep() -> None:
    """
    Show how success probability varies with number of iterations.
    """
    print("\n" + "=" * 60)
    print("Iteration Sweep Analysis")
    print("=" * 60)

    marked = ["101"]
    n_qubits = 3
    N = 2 ** n_qubits

    print(f"\nSearching for {marked} in {N} items")
    print("\n| Iterations | P(success) | P(marked) |")
    print("|------------|------------|-----------|")

    for n_iter in range(10):
        _, counts, _ = grovers_algorithm(marked, n_qubits, n_iter)

        success = counts.get(marked[0], 0)
        total = sum(counts.values())
        prob = success / total

        # Theoretical probability
        theta = np.arcsin(np.sqrt(1/N))
        theoretical = np.sin((2*n_iter + 1) * theta) ** 2

        print(f"| {n_iter:10} | {prob:>10.3f} | {theoretical:>9.3f} |")

    optimal = optimal_iterations(n_qubits)
    print(f"\nOptimal iterations: {optimal}")


def visualize_grover() -> None:
    """
    Visualize Grover's algorithm.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    # 1. Success probability vs iterations
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    marked = ["101"]
    n_qubits = 3
    N = 2 ** n_qubits

    iterations = list(range(15))
    probs = []

    for n_iter in iterations:
        _, counts, _ = grovers_algorithm(marked, n_qubits, n_iter)
        probs.append(counts.get(marked[0], 0) / sum(counts.values()))

    # Theoretical curve
    theta = np.arcsin(np.sqrt(1/N))
    theoretical = [np.sin((2*k + 1) * theta) ** 2 for k in iterations]

    axes[0].plot(iterations, probs, 'bo-', label='Measured', markersize=8)
    axes[0].plot(iterations, theoretical, 'r--', label='Theoretical', linewidth=2)
    axes[0].axvline(x=optimal_iterations(n_qubits), color='green',
                   linestyle=':', label=f'Optimal ({optimal_iterations(n_qubits)})')
    axes[0].set_xlabel('Number of Iterations')
    axes[0].set_ylabel('Success Probability')
    axes[0].set_title('Success Probability vs Iterations')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # 2. Final state distribution
    _, counts, _ = grovers_algorithm(marked, n_qubits)
    labels = sorted(counts.keys())
    values = [counts[l] for l in labels]
    colors = ['green' if l in marked else 'steelblue' for l in labels]

    axes[1].bar(labels, values, color=colors, edgecolor='black')
    axes[1].set_xlabel('Measurement Outcome')
    axes[1].set_ylabel('Counts')
    axes[1].set_title(f'Grover Search for |{marked[0]}⟩')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "grover_results.png", dpi=150)
    print("Saved: grover_results.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point.
    """
    print("=" * 60)
    print("  GROVER'S SEARCH ALGORITHM")
    print("  Project 8: Quadratic Speedup for Search")
    print("=" * 60)

    # Part 1: Mathematical analysis
    analyze_grover_math()

    # Part 2: Complexity analysis
    complexity_analysis()

    # Part 3: Demonstrations
    demonstrate_grover()

    # Part 4: Iteration sweep
    iteration_sweep()

    # Part 5: Visualizations
    visualize_grover()

    print("\n" + "=" * 60)
    print("🎉 Grover's Algorithm Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Quadratic speedup: O(√N) vs O(N) for unstructured search
2. Amplitude amplification rotates state toward marked items
3. Optimal iterations: (π/4)√(N/M)
4. Oracle marks solutions, diffusion amplifies
5. This is provably optimal for black-box search!

Applications:
- Database search
- Satisfiability problems
- Optimization
- Cryptanalysis

Next: Project 9 - Quantum Simulation
    """)


if __name__ == "__main__":
    main()
