# Project 1: Hello World - Superposition and Measurement

## Overview

This is your first quantum program! We explore the most fundamental quantum phenomenon: **superposition**. Unlike classical bits that are either 0 or 1, a quantum bit (qubit) can exist in a coherent superposition of both states simultaneously.

## Learning Objectives

By completing this project, you will understand:
- How to create and run a quantum circuit on AWS Braket
- The mathematical representation of qubit states
- How the Hadamard gate creates superposition
- The probabilistic nature of quantum measurement
- The role of phases and interference in quantum computing

## Mathematical Foundation

### The Qubit State Space

A qubit lives in a 2-dimensional complex Hilbert space $\mathbb{C}^2$. The **computational basis** consists of two orthonormal states:

$$|0\rangle = \begin{pmatrix} 1 \\ 0 \end{pmatrix}, \quad |1\rangle = \begin{pmatrix} 0 \\ 1 \end{pmatrix}$$

A general qubit state is a **superposition**:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle = \begin{pmatrix} \alpha \\ \beta \end{pmatrix}$$

where $\alpha, \beta \in \mathbb{C}$ and the **normalization constraint** holds:

$$|\alpha|^2 + |\beta|^2 = 1$$

### The Hadamard Gate

The Hadamard gate is our primary tool for creating superposition:

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

Its action on basis states:

$$H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle$$

$$H|1\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle$$

**Key Properties:**
- $H$ is Hermitian: $H = H^\dagger$
- $H$ is unitary: $HH^\dagger = I$
- $H$ is its own inverse: $H^2 = I$

### Measurement: The Born Rule

When we measure a qubit in state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$:

$$P(\text{measure } 0) = |\alpha|^2$$
$$P(\text{measure } 1) = |\beta|^2$$

This is called the **Born rule**. After measurement, the state **collapses** to the measured outcome.

For the $|+\rangle$ state:
$$P(0) = \left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}$$
$$P(1) = \left|\frac{1}{\sqrt{2}}\right|^2 = \frac{1}{2}$$

### The Bloch Sphere

Any pure qubit state can be written as:

$$|\psi\rangle = \cos\frac{\theta}{2}|0\rangle + e^{i\phi}\sin\frac{\theta}{2}|1\rangle$$

This maps to a point on the **Bloch sphere**:
- $\theta \in [0, \pi]$: polar angle (latitude from north pole)
- $\phi \in [0, 2\pi)$: azimuthal angle (longitude)

| State | θ | φ | Location |
|-------|---|---|----------|
| \|0⟩ | 0 | - | North pole |
| \|1⟩ | π | - | South pole |
| \|+⟩ | π/2 | 0 | +X axis |
| \|-⟩ | π/2 | π | -X axis |
| \|+i⟩ | π/2 | π/2 | +Y axis |
| \|-i⟩ | π/2 | 3π/2 | -Y axis |

### Quantum Interference

Consider applying two Hadamards in sequence:

$$H \cdot H|0\rangle = H|+\rangle = H\left(\frac{|0\rangle + |1\rangle}{\sqrt{2}}\right)$$

$$= \frac{1}{\sqrt{2}}\left(\frac{|0\rangle + |1\rangle}{\sqrt{2}} + \frac{|0\rangle - |1\rangle}{\sqrt{2}}\right)$$

$$= \frac{1}{2}(2|0\rangle + 0|1\rangle) = |0\rangle$$

The $|1\rangle$ amplitudes **destructively interfere** (they cancel), while $|0\rangle$ amplitudes **constructively interfere**.

This is the essence of quantum computing: manipulating interference patterns to amplify correct answers and suppress wrong ones.

## Circuit Diagram

```
Single Qubit Superposition:
q0: ──H──M──

Multi-Qubit Uniform Superposition:
q0: ──H──┬──
q1: ──H──┼──
q2: ──H──┴──M
```

## Running the Code

```bash
# Navigate to project directory
cd 01_hello_world

# Run the hello world program
python hello_quantum.py
```

## Expected Output

```
================================================================
  QUANTUM HELLO WORLD
  Project 1: Superposition and Measurement
================================================================

📌 Part 1: Creating Superposition
----------------------------------------

Circuit:
T  : |0|
q0 : -H-

State vector: [0.70710678+0.j 0.70710678+0.j]
This represents: (1/√2)|0⟩ + (1/√2)|1⟩

Measurement results (1000 shots): {'0': ~500, '1': ~500}
```

## Why This Matters

### The Quantum Advantage Preview

A single qubit in superposition represents 2 values simultaneously. With $n$ qubits:

| n qubits | Classical states | Quantum superposition |
|----------|------------------|----------------------|
| 1 | 1 state at a time | 2 states simultaneously |
| 10 | 1 state at a time | 1,024 states simultaneously |
| 50 | 1 state at a time | ~10^15 states simultaneously |
| 300 | 1 state at a time | More than atoms in universe |

This **exponential parallelism** is the foundation of quantum speedups. However, extracting useful information requires clever use of interference—that's what quantum algorithms do!

### Classical vs Quantum Randomness

A measured qubit in superposition appears random, but it's fundamentally different from classical randomness:

| Property | Classical Random | Quantum Superposition |
|----------|-----------------|----------------------|
| Source | Pseudo-random or thermal noise | Fundamental physics |
| Predictability | Deterministic if you know the state | Inherently unpredictable |
| Interference | No | Yes |
| Correlated (entangled) | Limited by Bell inequalities | Can violate Bell inequalities |

## Code Structure

```
01_hello_world/
├── hello_quantum.py      # Main implementation
├── README.md             # This file
├── requirements.txt      # Project dependencies
└── *.png                 # Generated visualizations
```

## Exercises

1. **Modify the phase**: Replace `H` with `H → S → H` and observe how the results change. The $S$ gate adds a phase of $i$ to the $|1\rangle$ component.

2. **Statistical confidence**: How many shots do you need to be 95% confident that the measured probability is within 1% of the true value? (Hint: use the formula $n = \frac{z^2 p(1-p)}{\epsilon^2}$)

3. **Superposition of more qubits**: Modify the code to create a 5-qubit superposition. How many different outcomes do you observe?

4. **Verify unitarity**: Show mathematically that $H^\dagger H = I$ by computing the matrix multiplication.

## Common Pitfalls

1. **Forgetting normalization**: State vectors must have unit norm. If you manually create states, always normalize.

2. **Confusing amplitude and probability**: The amplitude is complex; the probability is $|\text{amplitude}|^2$.

3. **Thinking superposition = classical mixture**: A superposition is NOT "secretly in one state but we don't know which." It's genuinely in both states simultaneously, as evidenced by interference.

## Next Steps

In [Project 2: Bell State](../02_bell_state/), we'll explore **entanglement**—when two or more qubits become correlated in ways impossible classically.

## References

1. Nielsen & Chuang, Chapter 1.2: "The qubit"
2. Preskill Lecture Notes, Chapter 2: "Foundations I: States and Ensembles"
3. AWS Braket Documentation: [Getting Started with Circuits](https://docs.aws.amazon.com/braket/latest/developerguide/braket-get-started-hello-ahs.html)
