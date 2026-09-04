# Quantum Computing Fundamentals

**Live demo:** [eredonda.com/projects/quantum-lab](https://eredonda.com/projects/quantum-lab?utm_source=github&utm_medium=referral)

Twelve quantum algorithms implemented from their gates rather than called from a
library, ordered so each depends only on the ones before it, ending with the
machinery applied to computational biology.

## Scope: stated plainly

Everything runs on Braket's **local** simulators (`braket_sv`, `braket_dm`).
Nothing here has been submitted to a managed simulator or to QPU hardware, so
there are no device ARNs and no task costs. An AWS account is not required to
run any of it.

One project does not deliver what its name promises. Project 11 (Shor's
algorithm) implements the QFT and the full classical half, but the controlled
modular arithmetic that would make period-finding quantum is a stub, so
order-finding runs classically. The file says so at the top. Projects 8 (Grover),
9 (Trotterised simulation) and 12 (swap test) do build and run real circuits.

## Prerequisites

- Python 3.9+
- Strong foundation in linear algebra and complex numbers
- Familiarity with probability theory

## Repository Structure

```
quantum-fundamentals/
├── shared/                          # Shared utilities and visualization tools
├── 01_hello_world/                  # Superposition and measurement basics
├── 02_bell_state/                   # Quantum entanglement
├── 03_quantum_teleportation/        # Quantum state transfer
├── 04_deutsch_algorithm/            # First quantum speedup
├── 05_bernstein_vazirani/           # Hidden string problem
├── 06_quantum_fourier_transform/    # Foundation for advanced algorithms
├── 07_phase_estimation/             # Eigenvalue extraction
├── 08_grovers_search/               # Quadratic speedup for search
├── 09_quantum_simulation/           # Simulating quantum systems
├── 10_quantum_counting/             # Combining Grover with QPE
├── 11_shors_algorithm/              # Integer factorization
└── 12_quantum_bioinformatics/       # Real-world application
```

## Learning Path

### Beginner Level (Projects 1-5)

| Project | Concept | Quantum Advantage |
|---------|---------|-------------------|
| 01 | Superposition & Measurement | Parallel state exploration |
| 02 | Entanglement | Non-classical correlations |
| 03 | Teleportation | Quantum state transfer |
| 04 | Deutsch Algorithm | Exponential query reduction |
| 05 | Bernstein-Vazirani | Linear vs exponential queries |

### Intermediate Level (Projects 6-10)

| Project | Concept | Quantum Advantage |
|---------|---------|-------------------|
| 06 | Quantum Fourier Transform | O(n²) vs O(n·2ⁿ) classical |
| 07 | Phase Estimation | Eigenvalue extraction |
| 08 | Grover's Search | O(√N) vs O(N) classical |
| 09 | Quantum Simulation | Exponential speedup for physics |
| 10 | Quantum Counting | Amplitude estimation |

### Advanced Level (Projects 11-12)

| Project | Concept | Quantum Advantage |
|---------|---------|-------------------|
| 11 | Shor's Algorithm | Exponential speedup for factoring |
| 12 | Bioinformatics | Practical application |

## Mathematical Foundations

### State Space (Hilbert Space)

A quantum bit (qubit) lives in a 2-dimensional complex Hilbert space ℂ². The computational basis states are:

$$|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad |1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$$

A general qubit state is:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad \alpha, \beta \in \mathbb{C}, \quad |\alpha|^2 + |\beta|^2 = 1$$

### Quantum Gates (Unitary Operators)

Quantum gates are unitary matrices (U†U = I). Key single-qubit gates:

**Pauli Gates:**
$$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$

**Hadamard Gate:**
$$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

**Phase Gates:**
$$S = \begin{pmatrix} 1 & 0 \\ 0 & i \end{pmatrix}, \quad T = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$$

### Measurement

Measurement in the computational basis projects onto |0⟩ or |1⟩:
- Probability of measuring |0⟩: |α|²
- Probability of measuring |1⟩: |β|²

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID: Secret Access Key, and region
```

### 3. Run Your First Quantum Program

```bash
cd 01_hello_world
python hello_quantum.py
```

## AWS Braket Simulators

This repository uses AWS Braket simulators:

| Simulator | Description | Use Case |
|-----------|-------------|----------|
| `braket_sv` | State vector simulator | Small circuits, debugging |
| `braket_dm` | Density matrix simulator | Noise modeling |

**Cost Note:** Local simulators are free. Managed simulators have per-task costs.

## Notation Guide

| Symbol | Meaning |
|--------|---------|
| \|ψ⟩ | Quantum state (ket) |
| ⟨ψ\| | Dual state (bra) |
| ⟨ψ\|φ⟩ | Inner product |
| \|ψ⟩⊗\|φ⟩ | Tensor product |
| U† | Hermitian conjugate |
| [A, B] | Commutator AB - BA |

## References

1. Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*
2. Preskill, J. (2018). *Quantum Computing in the NISQ era and beyond*
3. AWS Braket Documentation: https://docs.aws.amazon.com/braket/

## License

MIT License - See LICENSE file for details.
