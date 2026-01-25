#!/usr/bin/env python3
"""
Project 3: Quantum Teleportation

Quantum teleportation transfers an unknown quantum state from one qubit (Alice)
to another qubit (Bob) using shared entanglement and classical communication.

Key Concepts:
- No-cloning theorem (can't copy quantum states)
- Entanglement as a resource
- Classical communication is required (no FTL information transfer)
- State is destroyed at source, recreated at destination

Mathematical Foundation:
    Given: Alice has |ψ⟩ = α|0⟩ + β|1⟩ to teleport to Bob
    Resource: Shared Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2

    The protocol:
    1. Alice performs Bell measurement on her two qubits
    2. Alice sends 2 classical bits to Bob (measurement result)
    3. Bob applies correction based on classical bits
    4. Bob's qubit is now in state |ψ⟩

    The key insight: The total 3-qubit state can be rewritten to show
    that Bob's qubit is always in a state related to |ψ⟩ by a Pauli gate.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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
from shared.math_utils import fidelity, state_to_bloch


def prepare_state(theta: float, phi: float) -> Circuit:
    """
    Prepare an arbitrary single-qubit state.

    |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩

    This uses Ry(θ) followed by Rz(φ):
    Rz(φ)Ry(θ)|0⟩ = |ψ⟩

    Args:
        theta: Polar angle (0 to π)
        phi: Azimuthal angle (0 to 2π)

    Returns:
        Circuit preparing the state on qubit 0
    """
    circuit = Circuit()
    circuit.ry(0, theta)   # Rotate around Y by theta
    circuit.rz(0, phi)     # Rotate around Z by phi
    return circuit


def create_teleportation_circuit(
    theta: float,
    phi: float,
    measure_and_correct: bool = True
) -> Circuit:
    """
    Create the quantum teleportation circuit.

    Qubits:
    - q0: Alice's qubit (the state to teleport)
    - q1: Alice's half of the entangled pair
    - q2: Bob's half of the entangled pair (destination)

    Circuit structure:
    1. Prepare |ψ⟩ on q0
    2. Create Bell pair between q1 and q2
    3. Bell measurement on q0, q1
    4. Conditional corrections on q2

    Args:
        theta: Polar angle for the state to teleport
        phi: Azimuthal angle for the state to teleport
        measure_and_correct: If True, include corrections (full protocol)

    Returns:
        Braket Circuit object
    """
    circuit = Circuit()

    # Step 1: Prepare the state to teleport on qubit 0
    circuit.ry(0, theta)
    circuit.rz(0, phi)

    # Step 2: Create Bell pair between qubits 1 and 2
    # Bob holds qubit 2, Alice holds qubit 1
    circuit.h(1)
    circuit.cnot(1, 2)

    # Step 3: Bell measurement on Alice's qubits (0 and 1)
    # This is done by: CNOT(0,1) then H(0)
    circuit.cnot(0, 1)
    circuit.h(0)

    if measure_and_correct:
        # Step 4: Classical communication and corrections
        # In a real implementation, this would be conditional on measurement
        # In simulation, we use controlled gates

        # If qubit 1 measures |1⟩, apply X to qubit 2
        circuit.cnot(1, 2)

        # If qubit 0 measures |1⟩, apply Z to qubit 2
        circuit.cz(0, 2)

    return circuit


def analyze_teleportation_math() -> None:
    """
    Detailed mathematical analysis of the teleportation protocol.

    Shows the step-by-step state evolution and why it works.
    """
    print("\n" + "=" * 60)
    print("Mathematical Analysis of Quantum Teleportation")
    print("=" * 60)

    print("""
Initial state:
    |ψ⟩₀ ⊗ |Φ+⟩₁₂ = (α|0⟩ + β|1⟩)₀ ⊗ (|00⟩ + |11⟩)₁₂ / √2

Expanding:
    = (α|000⟩ + α|011⟩ + β|100⟩ + β|111⟩) / √2

Now we rewrite in the Bell basis for qubits 0 and 1:
    |00⟩ = (|Φ+⟩ + |Φ-⟩) / √2
    |01⟩ = (|Ψ+⟩ + |Ψ-⟩) / √2
    |10⟩ = (|Φ+⟩ - |Φ-⟩) / √2
    |11⟩ = (|Ψ+⟩ - |Ψ-⟩) / √2

Substituting and regrouping:
    = ½|Φ+⟩₀₁ ⊗ (α|0⟩ + β|1⟩)₂
    + ½|Φ-⟩₀₁ ⊗ (α|0⟩ - β|1⟩)₂
    + ½|Ψ+⟩₀₁ ⊗ (β|0⟩ + α|1⟩)₂
    + ½|Ψ-⟩₀₁ ⊗ (β|0⟩ - α|1⟩)₂

Rewriting Bob's states with Pauli corrections:
    = ½|Φ+⟩₀₁ ⊗ |ψ⟩₂           (no correction needed)
    + ½|Φ-⟩₀₁ ⊗ Z|ψ⟩₂          (apply Z)
    + ½|Ψ+⟩₀₁ ⊗ X|ψ⟩₂          (apply X)
    + ½|Ψ-⟩₀₁ ⊗ XZ|ψ⟩₂         (apply X then Z)

After Bell measurement, Bob knows which correction to apply:
    |Φ+⟩ → 00 → I   (do nothing)
    |Φ-⟩ → 10 → Z
    |Ψ+⟩ → 01 → X
    |Ψ-⟩ → 11 → XZ (equivalently ZX)
    """)


def verify_teleportation(theta: float, phi: float, shots: int = 1000) -> Dict:
    """
    Verify teleportation by comparing initial and final states.

    Args:
        theta: Polar angle of state to teleport
        phi: Azimuthal angle of state to teleport
        shots: Number of measurement shots

    Returns:
        Dictionary with verification results
    """
    # Create the original state
    original_circuit = prepare_state(theta, phi)
    original_state = get_state_vector(original_circuit)

    # Create teleportation circuit
    teleport_circuit = create_teleportation_circuit(theta, phi)

    # Get state after teleportation (before any measurement)
    # We need to trace out qubits 0 and 1 to see qubit 2's state
    # In our simulation with corrections, qubit 2 should be in |ψ⟩

    # To verify, we'll create a circuit that:
    # 1. Teleports the state
    # 2. Applies the inverse preparation to qubit 2
    # 3. Measures qubit 2 - should get |0⟩ if teleportation worked

    verify_circuit = create_teleportation_circuit(theta, phi)
    # Inverse of Rz(phi)Ry(theta) is Ry(-theta)Rz(-phi)
    verify_circuit.rz(2, -phi)
    verify_circuit.ry(2, -theta)

    # Measure qubit 2
    counts = run_circuit(verify_circuit, shots=shots)

    # Count how often qubit 2 is in |0⟩ (after tracing out qubits 0,1)
    success_count = 0
    for outcome, count in counts.items():
        # Qubit 2 is the rightmost bit in our convention
        if outcome[-1] == '0':
            success_count += count

    success_rate = success_count / shots

    return {
        'theta': theta,
        'phi': phi,
        'success_rate': success_rate,
        'original_state': original_state,
    }


def demonstrate_teleportation() -> None:
    """
    Demonstrate teleportation with various states.
    """
    print("\n" + "=" * 60)
    print("Teleportation Demonstrations")
    print("=" * 60)

    test_states = [
        (0, 0, "|0⟩"),
        (np.pi, 0, "|1⟩"),
        (np.pi/2, 0, "|+⟩"),
        (np.pi/2, np.pi, "|-⟩"),
        (np.pi/2, np.pi/2, "|+i⟩"),
        (np.pi/3, np.pi/4, "arbitrary state"),
    ]

    print("\nTeleporting various quantum states:")
    print("-" * 50)

    for theta, phi, name in test_states:
        result = verify_teleportation(theta, phi, shots=2000)
        print(f"\n  State: {name}")
        print(f"    θ = {theta:.4f}, φ = {phi:.4f}")
        print(f"    Original state vector: {result['original_state']}")
        print(f"    Verification success rate: {result['success_rate']*100:.1f}%")

        if result['success_rate'] > 0.95:
            print("    ✓ Teleportation successful!")
        else:
            print("    ⚠ Some deviation (expected due to measurement statistics)")


def no_cloning_demonstration() -> None:
    """
    Demonstrate why teleportation doesn't violate no-cloning.

    The no-cloning theorem states: There is no unitary U such that
    U(|ψ⟩|0⟩) = |ψ⟩|ψ⟩ for all |ψ⟩.

    Teleportation doesn't clone because the original state is destroyed
    during the Bell measurement.
    """
    print("\n" + "=" * 60)
    print("No-Cloning Theorem and Teleportation")
    print("=" * 60)

    print("""
The No-Cloning Theorem:
    It is impossible to create an identical copy of an arbitrary
    unknown quantum state.

Proof sketch:
    Suppose a cloning unitary U exists: U|ψ⟩|0⟩ = |ψ⟩|ψ⟩

    For two states |ψ⟩ and |φ⟩:
        ⟨ψ|φ⟩ = ⟨ψ|⟨0|U†U|φ⟩|0⟩ = ⟨ψ|φ⟩²

    This means ⟨ψ|φ⟩ = 0 or 1 for all pairs.
    But we can have 0 < ⟨ψ|φ⟩ < 1. Contradiction! ∎

Why teleportation is allowed:
    1. The original state is DESTROYED during Bell measurement
    2. Only 1 copy exists at any time
    3. Classical information (2 bits) is required
    4. The "transfer" is not instantaneous (limited by classical comm)

Teleportation = State TRANSFER, not state COPYING
    """)

    # Demonstrate that measurement destroys the original
    print("\nDemonstration: Original state is destroyed")
    print("-" * 40)

    circuit = create_teleportation_circuit(np.pi/4, np.pi/3)

    # Get the full 3-qubit state after Bell measurement
    # (before we would trace out)
    full_state = get_state_vector(circuit)

    print("\nAfter teleportation protocol, the 3-qubit state is:")
    print(f"  {np.round(full_state, 4)}")
    print("\nQubit 0 (original) is entangled with the measurement record,")
    print("not in a pure state. The original |ψ⟩ no longer exists!")


def information_transfer_analysis() -> None:
    """
    Analyze why teleportation doesn't enable FTL communication.
    """
    print("\n" + "=" * 60)
    print("Teleportation and Faster-Than-Light Communication")
    print("=" * 60)

    print("""
Why can't we use teleportation for FTL communication?

Scenario:
    - Alice and Bob share entanglement
    - They're light-years apart
    - Alice wants to send a message to Bob

The problem:
    1. Without classical bits, Bob's qubit is in a RANDOM state
       (maximally mixed, ρ = I/2)

    2. Bob cannot distinguish his qubit's state without knowing
       Alice's measurement result

    3. Alice must send 2 classical bits to Bob
       - These travel at ≤ speed of light
       - They carry NO information about |ψ⟩ by themselves
       - But they're essential for Bob to "decode" the state

Analysis:
    Before classical bits arrive:
        Bob's qubit: ρ_B = Tr_A(|Ψ⟩⟨Ψ|) = I/2

    After classical bits arrive:
        Bob applies correction → gets |ψ⟩

    The quantum information "arrives" only when classical bits do.
    Entanglement is a RESOURCE, not a communication channel.
    """)


def superdense_coding() -> None:
    """
    Demonstrate superdense coding - the "dual" of teleportation.

    Teleportation: 1 qubit + 2 cbits → transfer 1 qubit
    Superdense:    1 qubit + entanglement → transfer 2 cbits
    """
    print("\n" + "=" * 60)
    print("Superdense Coding (Dual of Teleportation)")
    print("=" * 60)

    print("""
Superdense coding is the "inverse" of teleportation:
    - Share 1 entangled pair
    - Send 1 qubit
    - Transfer 2 classical bits

Protocol:
    1. Alice and Bob share |Φ+⟩
    2. Alice encodes 2 bits by applying I, X, Z, or XZ to her qubit:
       00 → I  → |Φ+⟩
       01 → X  → |Ψ+⟩
       10 → Z  → |Φ-⟩
       11 → XZ → |Ψ-⟩
    3. Alice sends her qubit to Bob
    4. Bob performs Bell measurement to decode

This "uses up" the entanglement (1 ebit) to send 2 bits.
    """)

    print("\nDemonstrating superdense coding:")
    print("-" * 40)

    messages = [
        ("00", Circuit().h(0).cnot(0, 1)),                    # I
        ("01", Circuit().h(0).cnot(0, 1).x(0)),               # X
        ("10", Circuit().h(0).cnot(0, 1).z(0)),               # Z
        ("11", Circuit().h(0).cnot(0, 1).x(0).z(0)),          # XZ
    ]

    for msg, encode_circuit in messages:
        # Bob's decoding: Bell measurement
        decode_circuit = encode_circuit.copy()
        decode_circuit.cnot(0, 1)
        decode_circuit.h(0)

        counts = run_circuit(decode_circuit, shots=1000)

        # The measurement result should match the encoded message
        dominant = max(counts, key=counts.get)
        print(f"\n  Encoded: {msg}, Decoded: {dominant}, Counts: {counts}")


def visualize_teleportation() -> None:
    """
    Create visualizations of the teleportation protocol.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    # Visualize Bloch sphere trajectory
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Various states to teleport
    states = [
        (np.pi/4, 0, "|ψ₁⟩: θ=π/4, φ=0"),
        (np.pi/2, np.pi/4, "|ψ₂⟩: θ=π/2, φ=π/4"),
        (2*np.pi/3, np.pi, "|ψ₃⟩: θ=2π/3, φ=π"),
    ]

    for ax, (theta, phi, title) in zip(axes, states):
        result = verify_teleportation(theta, phi, shots=2000)

        # Plot the state on Bloch sphere
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)

        # Draw sphere wireframe
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        xs = 0.95 * np.outer(np.cos(u), np.sin(v))
        ys = 0.95 * np.outer(np.sin(u), np.sin(v))
        zs = 0.95 * np.outer(np.ones(np.size(u)), np.cos(v))

        ax = fig.add_subplot(1, 3, list(axes).index(ax) + 1, projection='3d')
        ax.plot_wireframe(xs, ys, zs, color='lightgray', alpha=0.3, linewidth=0.5)

        # Plot state vector
        ax.quiver(0, 0, 0, x, y, z, color='purple', linewidth=3,
                  arrow_length_ratio=0.15)
        ax.scatter([x], [y], [z], color='purple', s=100)

        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_title(f"{title}\nSuccess: {result['success_rate']*100:.0f}%")

    plt.suptitle("Teleported States on Bloch Sphere", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "teleportation_states.png", dpi=150)
    print("Saved: teleportation_states.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for quantum teleportation demonstration.
    """
    print("=" * 60)
    print("  QUANTUM TELEPORTATION")
    print("  Project 3: Beam Me Up, Quantum Style")
    print("=" * 60)

    # Part 1: Show the circuit
    print("\n📌 Part 1: Teleportation Circuit")
    print("-" * 40)

    circuit = create_teleportation_circuit(np.pi/4, np.pi/6)
    print(f"\nTeleportation circuit:\n{circuit}")

    # Part 2: Mathematical analysis
    analyze_teleportation_math()

    # Part 3: Demonstrate with various states
    demonstrate_teleportation()

    # Part 4: No-cloning theorem
    no_cloning_demonstration()

    # Part 5: Why no FTL
    information_transfer_analysis()

    # Part 6: Superdense coding
    superdense_coding()

    # Part 7: Visualizations
    visualize_teleportation()

    print("\n" + "=" * 60)
    print("🎉 Quantum Teleportation Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
1. Teleportation transfers quantum states using entanglement + 2 cbits
2. The original state is destroyed (no cloning violation)
3. Classical communication is required (no FTL)
4. Superdense coding is the "dual" protocol
5. Entanglement is a resource that gets "consumed"

Next: Project 4 - Deutsch Algorithm (First Quantum Speedup!)
    """)


if __name__ == "__main__":
    main()
