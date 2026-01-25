#!/usr/bin/env python3
"""
Project 2: Bell State - Quantum Entanglement

This project explores entanglement, Einstein's "spooky action at a distance."
Bell states are maximally entangled two-qubit states that exhibit correlations
impossible to achieve classically.

Key Concepts:
- Entanglement via CNOT gate
- The four Bell states (Bell basis)
- Perfect correlations in entangled states
- Bell inequality violation

Mathematical Foundation:
    The Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2 has the property that:
    - Measuring either qubit gives 50/50 random result
    - But the results are ALWAYS perfectly correlated
    - This correlation holds in ANY measurement basis

    This is fundamentally different from classical correlation!
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

from shared.visualization import (
    plot_measurement_results,
    plot_state_vector,
    visualize_circuit_results,
)
from shared.braket_utils import run_circuit, get_state_vector, parity_expectation


def create_bell_state(bell_type: str = "phi_plus") -> Circuit:
    """
    Create one of the four Bell states.

    The Bell states form a complete orthonormal basis for 2-qubit systems:
    |Φ+⟩ = (|00⟩ + |11⟩)/√2  (bell_type = "phi_plus")
    |Φ-⟩ = (|00⟩ - |11⟩)/√2  (bell_type = "phi_minus")
    |Ψ+⟩ = (|01⟩ + |10⟩)/√2  (bell_type = "psi_plus")
    |Ψ-⟩ = (|01⟩ - |10⟩)/√2  (bell_type = "psi_minus")

    Circuit construction:
    - Start with |00⟩
    - Apply H to qubit 0: (|0⟩ + |1⟩)/√2 ⊗ |0⟩
    - Apply CNOT: (|00⟩ + |11⟩)/√2 = |Φ+⟩
    - Apply X and/or Z gates to get other Bell states

    Args:
        bell_type: One of "phi_plus", "phi_minus", "psi_plus", "psi_minus"

    Returns:
        Braket Circuit object
    """
    circuit = Circuit()

    # Create |Φ+⟩ = (|00⟩ + |11⟩)/√2
    circuit.h(0)      # |0⟩|0⟩ → |+⟩|0⟩
    circuit.cnot(0, 1)  # |+⟩|0⟩ → |Φ+⟩

    # Transform to other Bell states
    if bell_type == "phi_plus":
        pass  # Already |Φ+⟩
    elif bell_type == "phi_minus":
        # |Φ-⟩ = Z₁|Φ+⟩ = (|00⟩ - |11⟩)/√2
        circuit.z(0)
    elif bell_type == "psi_plus":
        # |Ψ+⟩ = X₁|Φ+⟩ = (|01⟩ + |10⟩)/√2
        circuit.x(1)
    elif bell_type == "psi_minus":
        # |Ψ-⟩ = X₁Z₁|Φ+⟩ = (|01⟩ - |10⟩)/√2
        circuit.x(1)
        circuit.z(0)
    else:
        raise ValueError(f"Unknown bell_type: {bell_type}")

    return circuit


def demonstrate_entanglement_correlations() -> None:
    """
    Demonstrate that Bell state qubits are perfectly correlated.

    For |Φ+⟩ = (|00⟩ + |11⟩)/√2:
    - If we measure qubit 0 and get 0, qubit 1 is ALWAYS 0
    - If we measure qubit 0 and get 1, qubit 1 is ALWAYS 1

    This correlation is 100% - not 99.9%, but exactly 100%.
    """
    print("\n" + "=" * 60)
    print("Entanglement Correlations")
    print("=" * 60)

    circuit = create_bell_state("phi_plus")
    counts = run_circuit(circuit, shots=1000)

    print(f"\n|Φ+⟩ = (|00⟩ + |11⟩)/√2")
    print(f"\nMeasurement results ({sum(counts.values())} shots):")

    for outcome, count in sorted(counts.items()):
        print(f"  |{outcome}⟩: {count} ({100*count/sum(counts.values()):.1f}%)")

    # Check correlations
    correlated = counts.get('00', 0) + counts.get('11', 0)
    anticorrelated = counts.get('01', 0) + counts.get('10', 0)

    print(f"\n📊 Correlation Analysis:")
    print(f"  Correlated outcomes (00 or 11): {correlated}")
    print(f"  Anti-correlated outcomes (01 or 10): {anticorrelated}")

    if anticorrelated == 0:
        print("  ✓ Perfect correlation! Qubits always agree.")
    else:
        print(f"  Note: Some anti-correlation due to measurement noise.")


def compare_entangled_vs_product() -> None:
    """
    Compare entangled states with classically correlated product states.

    An entangled state cannot be written as a tensor product:
    |Φ+⟩ ≠ |ψ₁⟩ ⊗ |ψ₂⟩ for any single-qubit states |ψ₁⟩, |ψ₂⟩

    Classical probability distributions can be correlated, but
    quantum entanglement provides stronger correlations that
    violate Bell inequalities.
    """
    print("\n" + "=" * 60)
    print("Entangled vs Product States")
    print("=" * 60)

    # Product state: |+⟩|+⟩ = (|00⟩ + |01⟩ + |10⟩ + |11⟩)/2
    circuit_product = Circuit()
    circuit_product.h(0)
    circuit_product.h(1)

    # Entangled state: |Φ+⟩ = (|00⟩ + |11⟩)/√2
    circuit_entangled = create_bell_state("phi_plus")

    counts_product = run_circuit(circuit_product, shots=1000)
    counts_entangled = run_circuit(circuit_entangled, shots=1000)

    print("\n1. Product State |+⟩|+⟩:")
    print("   Each qubit is independently random.")
    print(f"   Results: {counts_product}")

    print("\n2. Entangled State |Φ+⟩:")
    print("   Qubits are correlated, but individually random.")
    print(f"   Results: {counts_entangled}")

    print("\n💡 Key Insight:")
    print("   In the product state, all 4 outcomes are equally likely.")
    print("   In the entangled state, only correlated outcomes occur.")
    print("   Yet EACH qubit appears uniformly random when measured alone!")


def demonstrate_all_bell_states() -> Dict[str, Dict[str, int]]:
    """
    Create and measure all four Bell states.

    The four Bell states form a complete orthonormal basis:
    - They span the 4-dimensional 2-qubit Hilbert space
    - Any 2-qubit state can be written as a linear combination
    - They are maximally entangled (max entropy of entanglement)

    Returns:
        Dictionary mapping bell state names to measurement counts
    """
    print("\n" + "=" * 60)
    print("All Four Bell States")
    print("=" * 60)

    bell_states = {
        "phi_plus": "|Φ+⟩ = (|00⟩ + |11⟩)/√2",
        "phi_minus": "|Φ-⟩ = (|00⟩ - |11⟩)/√2",
        "psi_plus": "|Ψ+⟩ = (|01⟩ + |10⟩)/√2",
        "psi_minus": "|Ψ-⟩ = (|01⟩ - |10⟩)/√2",
    }

    results = {}

    for bell_type, description in bell_states.items():
        circuit = create_bell_state(bell_type)
        state_vector = get_state_vector(circuit)
        counts = run_circuit(circuit, shots=1000)

        results[bell_type] = counts

        print(f"\n{description}")
        print(f"  State vector: {np.round(state_vector, 3)}")
        print(f"  Measurements: {counts}")

    return results


def bell_measurement() -> None:
    """
    Demonstrate Bell state measurement (distinguishing Bell states).

    To distinguish the 4 Bell states, we reverse the creation circuit:
    1. Apply CNOT
    2. Apply H to first qubit
    3. Measure both qubits

    This maps:
    |Φ+⟩ → |00⟩
    |Φ-⟩ → |10⟩
    |Ψ+⟩ → |01⟩
    |Ψ-⟩ → |11⟩
    """
    print("\n" + "=" * 60)
    print("Bell State Measurement")
    print("=" * 60)

    print("\nBell measurement circuit reverses the creation:")
    print("  CNOT → H on qubit 0 → Measure")
    print("\nMapping:")
    print("  |Φ+⟩ → |00⟩")
    print("  |Φ-⟩ → |10⟩")
    print("  |Ψ+⟩ → |01⟩")
    print("  |Ψ-⟩ → |11⟩")

    for bell_type in ["phi_plus", "phi_minus", "psi_plus", "psi_minus"]:
        # Create Bell state
        circuit = create_bell_state(bell_type)

        # Bell measurement (reverse the creation)
        circuit.cnot(0, 1)
        circuit.h(0)

        counts = run_circuit(circuit, shots=1000)
        dominant_outcome = max(counts, key=counts.get)

        print(f"\n  {bell_type}: measured predominantly |{dominant_outcome}⟩")


def calculate_concurrence(state_vector: np.ndarray) -> float:
    """
    Calculate the concurrence of a 2-qubit pure state.

    Concurrence is a measure of entanglement:
    - C = 0 for product states
    - C = 1 for maximally entangled states (Bell states)

    For a pure state |ψ⟩ = Σᵢⱼ aᵢⱼ|ij⟩:
    C = 2|a₀₀a₁₁ - a₀₁a₁₀|

    Args:
        state_vector: 4-element complex array

    Returns:
        Concurrence value in [0, 1]
    """
    a00, a01, a10, a11 = state_vector
    return 2 * abs(a00 * a11 - a01 * a10)


def entanglement_analysis() -> None:
    """
    Analyze entanglement using the concurrence measure.
    """
    print("\n" + "=" * 60)
    print("Entanglement Analysis (Concurrence)")
    print("=" * 60)

    # Test different states
    test_states = [
        ("Product |00⟩", Circuit()),
        ("Product |+⟩|0⟩", Circuit().h(0)),
        ("Product |+⟩|+⟩", Circuit().h(0).h(1)),
        ("Bell |Φ+⟩", create_bell_state("phi_plus")),
        ("Bell |Ψ-⟩", create_bell_state("psi_minus")),
    ]

    print("\nConcurrence measures entanglement:")
    print("  C = 0: Product state (no entanglement)")
    print("  C = 1: Maximally entangled (Bell state)")

    for name, circuit in test_states:
        # Ensure 2 qubits
        if circuit.qubit_count < 2:
            circuit.i(1)  # Add identity on qubit 1

        state_vector = get_state_vector(circuit)
        concurrence = calculate_concurrence(state_vector)

        print(f"\n  {name}:")
        print(f"    State: {np.round(state_vector, 3)}")
        print(f"    Concurrence: {concurrence:.4f}")


def chsh_inequality_simulation() -> None:
    """
    Simulate the CHSH Bell inequality test.

    The CHSH inequality (Clauser-Horne-Shimony-Holt) is:
    |S| = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| ≤ 2

    For classical (local hidden variable) theories.

    Quantum mechanics predicts |S| ≤ 2√2 ≈ 2.83, and with optimal
    measurement settings on a Bell state, we achieve this maximum.

    This simulation shows the quantum violation of the classical bound.
    """
    print("\n" + "=" * 60)
    print("CHSH Bell Inequality Simulation")
    print("=" * 60)

    # Optimal measurement angles for maximum CHSH violation
    # Alice: 0 and π/4
    # Bob: π/8 and 3π/8
    alice_angles = [0, np.pi/4]
    bob_angles = [np.pi/8, 3*np.pi/8]

    def measure_correlation(theta_a: float, theta_b: float, shots: int = 1000) -> float:
        """
        Measure correlation ⟨A⊗B⟩ for measurement angles theta_a, theta_b.

        This measures in rotated bases:
        A(θ) = cos(θ)Z + sin(θ)X
        """
        circuit = create_bell_state("phi_plus")

        # Rotate to measurement basis
        # Ry(-2θ) followed by Z measurement is equivalent to measuring in rotated basis
        circuit.ry(0, -2*theta_a)
        circuit.ry(1, -2*theta_b)

        counts = run_circuit(circuit, shots=shots)

        # Calculate expectation value of parity
        expectation = parity_expectation(counts)
        return expectation

    print("\nClassical bound: |S| ≤ 2")
    print("Quantum bound:   |S| ≤ 2√2 ≈ 2.83")
    print("\nMeasuring correlations...")

    E = {}
    for i, a in enumerate(alice_angles):
        for j, b in enumerate(bob_angles):
            E[(i, j)] = measure_correlation(a, b, shots=2000)
            print(f"  E(a{i}, b{j}) = {E[(i,j)]:.4f}")

    # CHSH value
    S = E[(0, 0)] - E[(0, 1)] + E[(1, 0)] + E[(1, 1)]

    print(f"\n📊 CHSH Value: S = {S:.4f}")

    if abs(S) > 2:
        print(f"   ✓ Quantum violation! |S| = {abs(S):.4f} > 2")
        print("   This proves the correlations cannot be explained classically.")
    else:
        print("   Result within classical bound (statistical fluctuation).")

    theoretical_max = 2 * np.sqrt(2)
    print(f"\n   Theoretical quantum maximum: {theoretical_max:.4f}")
    print(f"   Achieved: {abs(S)/theoretical_max*100:.1f}% of maximum")


def visualize_bell_states() -> None:
    """
    Create visualizations of Bell states.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    bell_types = [
        ("phi_plus", "|Φ+⟩ = (|00⟩ + |11⟩)/√2"),
        ("phi_minus", "|Φ-⟩ = (|00⟩ - |11⟩)/√2"),
        ("psi_plus", "|Ψ+⟩ = (|01⟩ + |10⟩)/√2"),
        ("psi_minus", "|Ψ-⟩ = (|01⟩ - |10⟩)/√2"),
    ]

    for ax, (bell_type, title) in zip(axes.flat, bell_types):
        circuit = create_bell_state(bell_type)
        counts = run_circuit(circuit, shots=1000)

        labels = ['00', '01', '10', '11']
        values = [counts.get(l, 0) / 1000 for l in labels]

        ax.bar(labels, values, color='steelblue', edgecolor='black')
        ax.set_xlabel("Measurement Outcome")
        ax.set_ylabel("Probability")
        ax.set_title(title)
        ax.set_ylim(0, 0.7)

    plt.suptitle("The Four Bell States", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "bell_states.png", dpi=150)
    print("Saved: bell_states.png")

    # State vector visualization
    circuit = create_bell_state("phi_plus")
    state_vector = get_state_vector(circuit)
    counts = run_circuit(circuit, shots=1000)

    fig = visualize_circuit_results(
        counts, state_vector,
        title="Bell State |Φ+⟩ Analysis"
    )
    plt.savefig(Path(__file__).parent / "bell_analysis.png", dpi=150)
    print("Saved: bell_analysis.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for Bell state exploration.
    """
    print("=" * 60)
    print("  QUANTUM ENTANGLEMENT: BELL STATES")
    print("  Project 2: Spooky Action at a Distance")
    print("=" * 60)

    # Part 1: Create Bell state
    print("\n📌 Part 1: Creating a Bell State")
    print("-" * 40)

    circuit = create_bell_state("phi_plus")
    print(f"\nCircuit to create |Φ+⟩:\n{circuit}")

    state_vector = get_state_vector(circuit)
    print(f"\nState vector: {state_vector}")
    print("This is (|00⟩ + |11⟩)/√2")

    # Part 2: Demonstrate correlations
    demonstrate_entanglement_correlations()

    # Part 3: Compare with product states
    compare_entangled_vs_product()

    # Part 4: All four Bell states
    demonstrate_all_bell_states()

    # Part 5: Bell measurement
    bell_measurement()

    # Part 6: Entanglement analysis
    entanglement_analysis()

    # Part 7: CHSH inequality
    chsh_inequality_simulation()

    # Part 8: Visualizations
    visualize_bell_states()

    print("\n" + "=" * 60)
    print("🎉 Bell State Exploration Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Entanglement creates correlations impossible classically
2. Bell states are maximally entangled 2-qubit states
3. Each qubit appears random, but outcomes are correlated
4. CHSH inequality violation proves quantum non-locality
5. Entanglement is a resource for quantum protocols

Next: Project 3 - Quantum Teleportation
    """)


if __name__ == "__main__":
    main()
