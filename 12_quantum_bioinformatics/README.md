# Project 12: Quantum Computing for Bioinformatics

## Overview

This project demonstrates quantum computing applications in computational biology, specifically protein structure prediction, molecular similarity search, and drug-target binding affinity estimation.

## Applications

### 1. Protein Folding (HP Model)

The HP lattice model simplifies proteins to:
- **H** (Hydrophobic): prefers contact with other H
- **P** (Polar): neutral

**Energy Function**: $E = -\sum_{i<j} \delta_{H_iH_j} \cdot \text{contact}(i,j)$

**Quantum Approach**: Map to QUBO (Quadratic Unconstrained Binary Optimization), solve with QAOA or quantum annealing.

### 2. Molecular Similarity

**Goal**: Find similar molecules for drug discovery.

**Quantum Method**: Swap test for state overlap estimation:
$$\text{Similarity} = |\langle\psi_1|\psi_2\rangle|^2$$

### 3. Binding Affinity

**Goal**: Predict drug-receptor interaction strength.

**Quantum Method**: VQE (Variational Quantum Eigensolver) to find ground state energy of interaction Hamiltonian.

## Why Quantum?

| Problem | Classical | Quantum (Potential) |
|---------|-----------|---------------------|
| Protein folding | NP-hard | Polynomial (with error correction) |
| Molecular simulation | Exponential in electrons | Polynomial |
| Drug screening | O(N) per compound | O(√N) with Grover |

## Current Limitations

- Qubit count limits problem size
- Noise requires error correction
- Classical algorithms still competitive for small molecules

## Running the Code

```bash
cd 12_quantum_bioinformatics
python protein_folding.py
```

## References

1. Perdomo-Ortiz et al. (2012): "Finding low-energy conformations of lattice protein models by quantum annealing"
2. Cao et al. (2019): "Quantum Chemistry in the Age of Quantum Computing"
3. Google Quantum AI: Hartree-Fock on a superconducting qubit quantum computer (2020)
