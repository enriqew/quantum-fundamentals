#!/usr/bin/env python3
"""
Project 9: Quantum Simulation

Simulating quantum systems is one of the most promising near-term applications
of quantum computers. As Feynman observed, nature is quantum mechanical, so
simulating it efficiently requires a quantum computer.

Key Concepts:
- Hamiltonian simulation
- Trotterization (Suzuki-Trotter decomposition)
- Time evolution operators
- VQE (Variational Quantum Eigensolver)

Problem Statement:
    Given a Hamiltonian H, simulate e^(-iHt)|ψ⟩ for time t.

    Classical: Exponential in system size (dimension 2^n)
    Quantum: Polynomial in system size and time
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Callable

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.visualization import plot_state_vector
from shared.braket_utils import run_circuit, get_state_vector


# Pauli matrices
I = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def tensor_product(*args: np.ndarray) -> np.ndarray:
    """Compute tensor product of multiple matrices."""
    result = args[0]
    for m in args[1:]:
        result = np.kron(result, m)
    return result


def ising_hamiltonian(n_qubits: int, J: float = 1.0, h: float = 0.5) -> np.ndarray:
    """
    Create the transverse-field Ising model Hamiltonian.

    H = -J Σᵢ ZᵢZᵢ₊₁ - h Σᵢ Xᵢ

    Args:
        n_qubits: Number of qubits (spins)
        J: Coupling strength
        h: Transverse field strength

    Returns:
        Hamiltonian matrix
    """
    dim = 2 ** n_qubits
    H = np.zeros((dim, dim), dtype=complex)

    # ZZ interactions
    for i in range(n_qubits - 1):
        ops = [I] * n_qubits
        ops[i] = Z
        ops[i + 1] = Z
        H -= J * tensor_product(*ops)

    # Transverse field
    for i in range(n_qubits):
        ops = [I] * n_qubits
        ops[i] = X
        H -= h * tensor_product(*ops)

    return H


def heisenberg_hamiltonian(n_qubits: int, J: float = 1.0) -> np.ndarray:
    """
    Create the Heisenberg model Hamiltonian.

    H = J Σᵢ (XᵢXᵢ₊₁ + YᵢYᵢ₊₁ + ZᵢZᵢ₊₁)

    Args:
        n_qubits: Number of qubits
        J: Coupling strength

    Returns:
        Hamiltonian matrix
    """
    dim = 2 ** n_qubits
    H = np.zeros((dim, dim), dtype=complex)

    for i in range(n_qubits - 1):
        for pauli in [X, Y, Z]:
            ops = [I] * n_qubits
            ops[i] = pauli
            ops[i + 1] = pauli
            H += J * tensor_product(*ops)

    return H


def exact_time_evolution(H: np.ndarray, psi0: np.ndarray, t: float) -> np.ndarray:
    """
    Compute exact time evolution e^(-iHt)|ψ₀⟩.

    Args:
        H: Hamiltonian matrix
        psi0: Initial state
        t: Time

    Returns:
        Final state
    """
    U = expm(-1j * H * t)
    return U @ psi0


def trotter_step(circuit: Circuit, n_qubits: int, dt: float,
                 J: float = 1.0, h: float = 0.5) -> Circuit:
    """
    Apply one Trotter step for the Ising model.

    First-order Trotter: e^(-iHdt) ≈ e^(-iH_Xdt) e^(-iH_ZZdt)

    Args:
        circuit: Braket Circuit
        n_qubits: Number of qubits
        dt: Time step
        J: Coupling strength
        h: Transverse field strength
    """
    # H_X terms: exp(-i h X dt) = Rx(2 h dt)
    for i in range(n_qubits):
        circuit.rx(i, 2 * h * dt)

    # H_ZZ terms: exp(-i J ZZ dt)
    # Implemented as: CNOT, Rz, CNOT
    for i in range(n_qubits - 1):
        circuit.cnot(i, i + 1)
        circuit.rz(i + 1, 2 * J * dt)
        circuit.cnot(i, i + 1)

    return circuit


def simulate_ising(n_qubits: int, t_total: float, n_steps: int,
                   J: float = 1.0, h: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Simulate Ising model time evolution using Trotterization.

    Args:
        n_qubits: Number of qubits
        t_total: Total simulation time
        n_steps: Number of Trotter steps
        J, h: Hamiltonian parameters

    Returns:
        Tuple of (trotter_state, exact_state)
    """
    dt = t_total / n_steps

    # Trotter simulation
    circuit = Circuit()

    # Initialize in |+⟩^⊗n state
    for i in range(n_qubits):
        circuit.h(i)

    # Apply Trotter steps
    for _ in range(n_steps):
        trotter_step(circuit, n_qubits, dt, J, h)

    trotter_state = get_state_vector(circuit)

    # Exact simulation
    H = ising_hamiltonian(n_qubits, J, h)
    psi0 = np.ones(2 ** n_qubits) / np.sqrt(2 ** n_qubits)  # |+⟩^⊗n
    exact_state = exact_time_evolution(H, psi0, t_total)

    return trotter_state, exact_state


def analyze_trotter_error() -> None:
    """
    Analyze Trotter error as a function of step count.
    """
    print("\n" + "=" * 60)
    print("Trotter Error Analysis")
    print("=" * 60)

    n_qubits = 3
    t_total = 1.0
    J, h = 1.0, 0.5

    H = ising_hamiltonian(n_qubits, J, h)
    psi0 = np.ones(2 ** n_qubits) / np.sqrt(2 ** n_qubits)
    exact_state = exact_time_evolution(H, psi0, t_total)

    print(f"\nSimulating {n_qubits}-qubit Ising model for t = {t_total}")
    print("\n| Trotter Steps | Fidelity | Error |")
    print("|---------------|----------|-------|")

    for n_steps in [1, 2, 5, 10, 20, 50, 100]:
        trotter_state, _ = simulate_ising(n_qubits, t_total, n_steps, J, h)

        # Calculate fidelity
        fidelity = np.abs(np.vdot(exact_state, trotter_state)) ** 2
        error = 1 - fidelity

        print(f"| {n_steps:13} | {fidelity:.6f} | {error:.2e} |")

    print("""
First-order Trotter error scales as O(dt²) per step, O(t²/n) total.
Second-order Trotter would give O(dt³) per step.
    """)


def vqe_demo() -> None:
    """
    Simple demonstration of Variational Quantum Eigensolver concept.
    """
    print("\n" + "=" * 60)
    print("VQE Concept Demonstration")
    print("=" * 60)

    print("""
Variational Quantum Eigensolver (VQE):
    1. Prepare parameterized state: |ψ(θ)⟩
    2. Measure expectation value: ⟨ψ(θ)|H|ψ(θ)⟩
    3. Classical optimizer adjusts θ to minimize energy
    4. Converges to ground state energy

This is a hybrid quantum-classical algorithm suitable for NISQ devices.

Example: Finding ground state of H = Z
    - Ground state: |1⟩ with eigenvalue -1
    - Ansatz: Ry(θ)|0⟩
    - Expectation: ⟨Z⟩ = cos(θ)
    - Minimum at θ = π: ⟨Z⟩ = -1 ✓
    """)

    # Simple VQE for H = Z
    def expectation(theta: float) -> float:
        circuit = Circuit()
        circuit.ry(0, theta)
        state = get_state_vector(circuit)
        # ⟨Z⟩ = |α|² - |β|² for state α|0⟩ + β|1⟩
        return np.abs(state[0])**2 - np.abs(state[1])**2

    print("\nVQE optimization (gradient descent):")
    theta = 0.0
    learning_rate = 0.5

    for i in range(10):
        E = expectation(theta)
        # Gradient: d⟨Z⟩/dθ = -sin(θ)
        grad = -np.sin(theta)
        theta = theta - learning_rate * grad

        print(f"  Step {i}: θ = {theta:.4f}, ⟨Z⟩ = {E:.4f}")

    print(f"\nFinal: θ = {theta:.4f} (should be ~π = {np.pi:.4f})")


def visualize_simulation() -> None:
    """
    Visualize quantum simulation results.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    n_qubits = 3
    J, h = 1.0, 0.5

    # Time evolution comparison
    times = np.linspace(0, 2, 20)
    trotter_fidelities = []
    exact_energies = []

    H = ising_hamiltonian(n_qubits, J, h)
    psi0 = np.ones(2 ** n_qubits) / np.sqrt(2 ** n_qubits)

    for t in times:
        if t == 0:
            trotter_fidelities.append(1.0)
            exact_energies.append(np.real(psi0.conj() @ H @ psi0))
        else:
            trotter_state, exact_state = simulate_ising(n_qubits, t, n_steps=20, J=J, h=h)
            fidelity = np.abs(np.vdot(exact_state, trotter_state)) ** 2
            trotter_fidelities.append(fidelity)
            exact_energies.append(np.real(exact_state.conj() @ H @ exact_state))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(times, trotter_fidelities, 'b-o', markersize=4)
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Fidelity')
    axes[0].set_title('Trotter Fidelity vs Exact (20 steps)')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(0.9, 1.01)

    axes[1].plot(times, exact_energies, 'r-', linewidth=2)
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('⟨H⟩')
    axes[1].set_title('Energy Expectation Value')
    axes[1].grid(True, alpha=0.3)

    plt.suptitle(f"Ising Model Simulation ({n_qubits} qubits)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "simulation_results.png", dpi=150)
    print("Saved: simulation_results.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point.
    """
    print("=" * 60)
    print("  QUANTUM SIMULATION")
    print("  Project 9: Simulating Nature with Quantum Computers")
    print("=" * 60)

    # Part 1: Trotter error analysis
    analyze_trotter_error()

    # Part 2: VQE demonstration
    vqe_demo()

    # Part 3: Visualizations
    visualize_simulation()

    print("\n" + "=" * 60)
    print("🎉 Quantum Simulation Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Quantum systems are exponentially hard to simulate classically
2. Trotterization decomposes e^(-iHt) into implementable gates
3. Error scales as O(t²/n_steps) for first-order Trotter
4. VQE is a hybrid algorithm for finding ground states
5. This is a key near-term application of quantum computers!

Next: Project 10 - Quantum Counting
    """)


if __name__ == "__main__":
    main()
