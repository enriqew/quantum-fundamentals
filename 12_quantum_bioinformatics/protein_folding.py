#!/usr/bin/env python3
"""
Project 12: Quantum Computing for Bioinformatics

This project demonstrates quantum computing applications in computational biology,
specifically protein structure prediction and molecular simulation.

Key Applications:
1. Protein folding energy minimization (QUBO formulation)
2. Molecular similarity search (quantum fingerprints)
3. Drug-target binding affinity prediction
4. Sequence alignment optimization

This showcases how quantum computing could revolutionize drug discovery
and personalized medicine.

Note: Current quantum hardware is limited, so we demonstrate concepts
that will become practical with larger, error-corrected devices.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.braket_utils import run_circuit, get_state_vector


# =============================================================================
# PART 1: PROTEIN FOLDING - LATTICE MODEL
# =============================================================================

class Direction(Enum):
    """Directions on 2D lattice."""
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class AminoAcid:
    """Represents an amino acid in the chain."""
    index: int
    type: str  # 'H' (hydrophobic) or 'P' (polar)
    position: Tuple[int, int] = (0, 0)


def hp_model_energy(sequence: str, positions: List[Tuple[int, int]]) -> int:
    """
    Calculate energy of HP model protein configuration.

    The HP model simplifies amino acids to:
    - H (hydrophobic): prefers to be in contact with other H
    - P (polar): neutral

    Energy = -1 for each H-H contact (non-sequential neighbors)

    Args:
        sequence: String of 'H' and 'P' characters
        positions: List of (x, y) coordinates for each amino acid

    Returns:
        Energy value (more negative = more stable)
    """
    energy = 0
    n = len(sequence)

    for i in range(n):
        if sequence[i] != 'H':
            continue

        for j in range(i + 2, n):  # Skip sequential neighbors
            if sequence[j] != 'H':
                continue

            # Check if they are lattice neighbors
            dx = abs(positions[i][0] - positions[j][0])
            dy = abs(positions[i][1] - positions[j][1])

            if dx + dy == 1:  # Adjacent on lattice
                energy -= 1

    return energy


def is_valid_configuration(positions: List[Tuple[int, int]]) -> bool:
    """Check if configuration is self-avoiding."""
    return len(positions) == len(set(positions))


def encode_fold_to_qubits(n_acids: int) -> int:
    """
    Determine number of qubits needed to encode a fold.

    Each direction choice (except first) needs 2 qubits.
    First amino acid at origin, second to the right.

    Args:
        n_acids: Number of amino acids

    Returns:
        Number of qubits needed
    """
    return 2 * (n_acids - 2)  # Each turn needs 2 qubits


def decode_qubits_to_directions(
    bitstring: str,
    n_acids: int
) -> List[Direction]:
    """
    Decode qubit measurement to fold directions.

    Encoding:
    00 -> UP
    01 -> RIGHT
    10 -> LEFT
    11 -> DOWN (or continue straight)

    Args:
        bitstring: Measured qubit string
        n_acids: Number of amino acids

    Returns:
        List of directions
    """
    directions = [Direction.RIGHT]  # First step fixed

    for i in range(n_acids - 2):
        bits = bitstring[2*i:2*i+2]
        if bits == '00':
            directions.append(Direction.UP)
        elif bits == '01':
            directions.append(Direction.RIGHT)
        elif bits == '10':
            directions.append(Direction.LEFT)
        else:
            directions.append(Direction.DOWN)

    return directions


def directions_to_positions(directions: List[Direction]) -> List[Tuple[int, int]]:
    """Convert directions to amino acid positions."""
    positions = [(0, 0)]
    x, y = 0, 0

    for d in directions:
        dx, dy = d.value
        x, y = x + dx, y + dy
        positions.append((x, y))

    return positions


def quantum_folding_search(sequence: str, n_iterations: int = 100) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Use quantum-inspired optimization for protein folding.

    This demonstrates the concept using a variational approach.
    Real implementations would use QAOA or VQE on quantum hardware.

    Args:
        sequence: HP sequence (e.g., "HPHPPHHPHPPH")
        n_iterations: Number of optimization iterations

    Returns:
        Tuple of (best_energy, best_positions)
    """
    n = len(sequence)
    n_qubits = encode_fold_to_qubits(n)

    best_energy = 0
    best_positions = None

    # Quantum-inspired search using parameterized circuits
    for iteration in range(n_iterations):
        # Create variational circuit
        circuit = Circuit()

        # Initialize with random angles (simulating variational optimization)
        angles = np.random.uniform(0, 2*np.pi, n_qubits)

        for i in range(n_qubits):
            circuit.rx(i, angles[i])
            circuit.ry(i, angles[i] * 0.7)

        # Add entanglement
        for i in range(n_qubits - 1):
            circuit.cnot(i, i + 1)

        # Measure
        counts = run_circuit(circuit, shots=10)

        # Evaluate configurations
        for bitstring, count in counts.items():
            if len(bitstring) < n_qubits:
                bitstring = bitstring.zfill(n_qubits)

            directions = decode_qubits_to_directions(bitstring, n)
            positions = directions_to_positions(directions)

            if is_valid_configuration(positions):
                energy = hp_model_energy(sequence, positions)
                if energy < best_energy:
                    best_energy = energy
                    best_positions = positions

    return best_energy, best_positions


def classical_exhaustive_fold(sequence: str, max_configs: int = 10000) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Classical exhaustive search for comparison.

    Args:
        sequence: HP sequence
        max_configs: Maximum configurations to try

    Returns:
        Tuple of (best_energy, best_positions)
    """
    import itertools

    n = len(sequence)
    directions_list = list(Direction)

    best_energy = 0
    best_positions = None
    configs_tried = 0

    # Try all possible direction sequences
    for dirs in itertools.product(directions_list, repeat=n-1):
        if configs_tried >= max_configs:
            break

        positions = directions_to_positions(list(dirs))

        if is_valid_configuration(positions):
            energy = hp_model_energy(sequence, positions)
            if energy < best_energy:
                best_energy = energy
                best_positions = positions

        configs_tried += 1

    return best_energy, best_positions


# =============================================================================
# PART 2: MOLECULAR SIMILARITY
# =============================================================================

def molecular_fingerprint(smiles: str) -> np.ndarray:
    """
    Create a simple molecular fingerprint.

    In real applications, this would use RDKit or similar.
    Here we create a simplified fingerprint for demonstration.

    Args:
        smiles: SMILES string (simplified molecular input)

    Returns:
        Binary fingerprint array
    """
    # Simple hash-based fingerprint
    fingerprint = np.zeros(64, dtype=int)

    # Hash character pairs
    for i in range(len(smiles) - 1):
        pair = smiles[i:i+2]
        idx = hash(pair) % 64
        fingerprint[idx] = 1

    return fingerprint


def quantum_similarity_circuit(fp1: np.ndarray, fp2: np.ndarray) -> float:
    """
    Quantum circuit for molecular similarity estimation.

    Uses swap test to estimate overlap between fingerprint states.

    Args:
        fp1, fp2: Binary fingerprints

    Returns:
        Similarity score (0 to 1)
    """
    # Encode fingerprints as quantum states
    n_qubits = min(6, len(fp1))  # Limit for simulation

    circuit = Circuit()

    # Ancilla qubit for swap test
    ancilla = 2 * n_qubits
    circuit.h(ancilla)

    # Prepare fingerprint 1
    for i in range(n_qubits):
        if fp1[i] == 1:
            circuit.x(i)

    # Prepare fingerprint 2
    for i in range(n_qubits):
        if fp2[i] == 1:
            circuit.x(n_qubits + i)

    # Controlled swaps (swap test)
    for i in range(n_qubits):
        circuit.cswap(ancilla, i, n_qubits + i)

    # Final Hadamard on ancilla
    circuit.h(ancilla)

    # Measure
    counts = run_circuit(circuit, shots=1000)

    # Calculate probability of measuring 0 on ancilla
    p0 = sum(c for k, c in counts.items() if k[0] == '0') / sum(counts.values())

    # Similarity = 2*P(0) - 1 (for swap test)
    similarity = 2 * p0 - 1

    return max(0, similarity)


def tanimoto_similarity(fp1: np.ndarray, fp2: np.ndarray) -> float:
    """Classical Tanimoto similarity for comparison."""
    intersection = np.sum(np.logical_and(fp1, fp2))
    union = np.sum(np.logical_or(fp1, fp2))
    return intersection / union if union > 0 else 0


# =============================================================================
# PART 3: DRUG BINDING AFFINITY
# =============================================================================

def binding_hamiltonian(n_sites: int) -> np.ndarray:
    """
    Create a simplified Hamiltonian for drug-receptor binding.

    Models interaction between drug molecule and binding site
    as an Ising-like model.

    Args:
        n_sites: Number of interaction sites

    Returns:
        Hamiltonian matrix
    """
    dim = 2 ** n_sites
    H = np.zeros((dim, dim), dtype=complex)

    # Pauli Z matrices
    I = np.eye(2)
    Z = np.array([[1, 0], [0, -1]])

    # Single-site terms (binding energy at each site)
    for i in range(n_sites):
        ops = [I] * n_sites
        ops[i] = Z
        term = ops[0]
        for op in ops[1:]:
            term = np.kron(term, op)
        H += -0.5 * term  # Favorable binding

    # Two-site interaction terms
    for i in range(n_sites - 1):
        ops = [I] * n_sites
        ops[i] = Z
        ops[i + 1] = Z
        term = ops[0]
        for op in ops[1:]:
            term = np.kron(term, op)
        H += 0.2 * term  # Steric hindrance

    return H


def estimate_binding_energy(n_sites: int = 3) -> float:
    """
    Estimate binding energy using VQE-like approach.

    Args:
        n_sites: Number of binding sites

    Returns:
        Estimated ground state energy
    """
    H = binding_hamiltonian(n_sites)

    # Simple variational ansatz
    best_energy = float('inf')

    for _ in range(50):
        circuit = Circuit()

        # Random angles
        for i in range(n_sites):
            theta = np.random.uniform(0, 2*np.pi)
            circuit.ry(i, theta)

        # Entanglement
        for i in range(n_sites - 1):
            circuit.cnot(i, i + 1)

        # Get state
        state = get_state_vector(circuit)

        # Calculate energy
        energy = np.real(state.conj() @ H @ state)

        if energy < best_energy:
            best_energy = energy

    return best_energy


# =============================================================================
# PART 4: VISUALIZATION AND DEMONSTRATIONS
# =============================================================================

def visualize_protein_fold(sequence: str, positions: List[Tuple[int, int]],
                          energy: int, save_path: str) -> None:
    """Visualize protein fold on 2D lattice."""
    fig, ax = plt.subplots(figsize=(10, 10))

    # Draw grid
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]

    margin = 2
    ax.set_xlim(min(xs) - margin, max(xs) + margin)
    ax.set_ylim(min(ys) - margin, max(ys) + margin)

    # Draw backbone
    ax.plot(xs, ys, 'k-', linewidth=2, alpha=0.5)

    # Draw amino acids
    for i, (x, y) in enumerate(positions):
        color = 'red' if sequence[i] == 'H' else 'blue'
        ax.scatter([x], [y], c=color, s=500, zorder=5, edgecolors='black')
        ax.annotate(f'{sequence[i]}{i+1}', (x, y), ha='center', va='center',
                   fontsize=10, fontweight='bold', color='white')

    # Draw H-H contacts
    n = len(sequence)
    for i in range(n):
        if sequence[i] != 'H':
            continue
        for j in range(i + 2, n):
            if sequence[j] != 'H':
                continue
            dx = abs(positions[i][0] - positions[j][0])
            dy = abs(positions[i][1] - positions[j][1])
            if dx + dy == 1:
                ax.plot([positions[i][0], positions[j][0]],
                       [positions[i][1], positions[j][1]],
                       'g--', linewidth=3, alpha=0.7)

    ax.set_title(f'Protein Fold: {sequence}\nEnergy: {energy}', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label='Hydrophobic (H)'),
        Patch(facecolor='blue', label='Polar (P)'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def demonstrate_protein_folding() -> None:
    """Demonstrate protein folding optimization."""
    print("\n" + "=" * 60)
    print("PROTEIN FOLDING DEMONSTRATION")
    print("=" * 60)

    sequences = [
        "HPHH",
        "HPPHPH",
        "HPHPPHHPHP",
    ]

    for seq in sequences:
        print(f"\nSequence: {seq} (length {len(seq)})")

        # Quantum-inspired optimization
        energy, positions = quantum_folding_search(seq, n_iterations=200)

        if positions:
            print(f"  Best energy found: {energy}")
            print(f"  Configuration: {positions}")

            # Visualize
            save_path = Path(__file__).parent / f"fold_{seq}.png"
            visualize_protein_fold(seq, positions, energy, str(save_path))
            print(f"  Saved: {save_path.name}")
        else:
            print("  No valid configuration found")


def demonstrate_molecular_similarity() -> None:
    """Demonstrate molecular similarity search."""
    print("\n" + "=" * 60)
    print("MOLECULAR SIMILARITY DEMONSTRATION")
    print("=" * 60)

    # Example "molecules" (simplified)
    molecules = {
        "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "acetaminophen": "CC(=O)NC1=CC=C(C=C1)O",
        "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    }

    print("\nCalculating pairwise similarities:")
    print("-" * 50)

    fingerprints = {name: molecular_fingerprint(smiles)
                   for name, smiles in molecules.items()}

    names = list(molecules.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            fp1 = fingerprints[names[i]]
            fp2 = fingerprints[names[j]]

            # Classical Tanimoto
            tanimoto = tanimoto_similarity(fp1, fp2)

            # Quantum similarity (swap test)
            quantum = quantum_similarity_circuit(fp1, fp2)

            print(f"\n  {names[i]} vs {names[j]}:")
            print(f"    Tanimoto: {tanimoto:.3f}")
            print(f"    Quantum:  {quantum:.3f}")


def demonstrate_binding_affinity() -> None:
    """Demonstrate binding affinity estimation."""
    print("\n" + "=" * 60)
    print("BINDING AFFINITY ESTIMATION")
    print("=" * 60)

    print("""
This demonstrates VQE-like estimation of drug-receptor binding energy.
Lower energy = stronger binding = more effective drug.
    """)

    for n_sites in [2, 3, 4]:
        energy = estimate_binding_energy(n_sites)
        print(f"  {n_sites} binding sites: E = {energy:.4f}")


def main() -> None:
    """Main entry point."""
    print("╔" + "═" * 62 + "╗")
    print("║" + " " * 14 + "QUANTUM BIOINFORMATICS" + " " * 26 + "║")
    print("║" + " " * 8 + "Project 12: Computational Biology Applications" + " " * 8 + "║")
    print("╚" + "═" * 62 + "╝")

    print("""
Quantum computing promises to revolutionize computational biology:

1. PROTEIN FOLDING
   - Find minimum energy configurations
   - Drug design and discovery
   - Understanding disease mechanisms

2. MOLECULAR SIMILARITY
   - Virtual screening for drug candidates
   - Toxicity prediction
   - Lead optimization

3. BINDING AFFINITY
   - Predict drug-target interactions
   - Optimize drug candidates
   - Personalized medicine
    """)

    # Demonstrations
    demonstrate_protein_folding()
    demonstrate_molecular_similarity()
    demonstrate_binding_affinity()

    print("\n" + "=" * 64)
    print("🎉 QUANTUM BIOINFORMATICS COMPLETE!")
    print("=" * 64)
    print("""
KEY TAKEAWAYS:
1. Protein folding can be mapped to QUBO/Ising problems
2. Quantum similarity search uses swap test
3. VQE can estimate molecular energies
4. Current hardware is limited, but concepts are sound

FUTURE APPLICATIONS:
- AlphaFold + Quantum refinement
- Large-scale drug screening
- Personalized medicine
- Understanding protein misfolding diseases

REFERENCES:
1. Perdomo-Ortiz et al. (2012): "Finding low-energy conformations
   of lattice protein models by quantum annealing"
2. Cao et al. (2019): "Quantum Chemistry in the Age of Quantum Computing"
3. Outeiral et al. (2021): "The prospects of quantum computing in
   computational molecular biology"

CONGRATULATIONS!
You have completed the Quantum Computing Fundamentals course!
    """)


if __name__ == "__main__":
    main()
