# Project 2: Bell State - Quantum Entanglement

## Overview

This project explores **quantum entanglement**, what Einstein famously called "spooky action at a distance." Entanglement is a uniquely quantum phenomenon where two or more qubits become correlated in ways that have no classical analog.

## Learning Objectives

By completing this project, you will understand:
- How to create entangled states using the CNOT gate
- The mathematical structure of Bell states
- Why entanglement cannot be explained by classical physics
- The CHSH Bell inequality and its quantum violation
- Measures of entanglement (concurrence)

## Mathematical Foundation

### Tensor Products and Composite Systems

For two qubits, the state space is $\mathbb{C}^2 \otimes \mathbb{C}^2 = \mathbb{C}^4$. The computational basis is:

$$|00\rangle = |0\rangle \otimes |0\rangle, \quad |01\rangle = |0\rangle \otimes |1\rangle$$
$$|10\rangle = |1\rangle \otimes |0\rangle, \quad |11\rangle = |1\rangle \otimes |1\rangle$$

A **product state** can be written as $|\psi_1\rangle \otimes |\psi_2\rangle$. An **entangled state** cannot.

### The CNOT Gate

The Controlled-NOT (CNOT) gate is essential for creating entanglement:

$$\text{CNOT} = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{pmatrix}$$

Its action: $|c, t\rangle \rightarrow |c, c \oplus t\rangle$ where $\oplus$ is XOR.

### The Four Bell States

The Bell states form a complete orthonormal basis for 2-qubit systems:

$$|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$$
$$|\Phi^-\rangle = \frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)$$
$$|\Psi^+\rangle = \frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)$$
$$|\Psi^-\rangle = \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)$$

### Creating a Bell State

Starting from $|00\rangle$:

1. Apply Hadamard to qubit 0:
   $$H \otimes I |00\rangle = |+\rangle|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)|0\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |10\rangle)$$

2. Apply CNOT (control=0, target=1):
   $$\text{CNOT}\frac{1}{\sqrt{2}}(|00\rangle + |10\rangle) = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle) = |\Phi^+\rangle$$

### Why Bell States Are Entangled

For $|\Phi^+\rangle$, we can prove it's not a product state. Suppose:

$$|\Phi^+\rangle = (a|0\rangle + b|1\rangle)(c|0\rangle + d|1\rangle) = ac|00\rangle + ad|01\rangle + bc|10\rangle + bd|11\rangle$$

Comparing with $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$:
- $ac = \frac{1}{\sqrt{2}}$
- $ad = 0$
- $bc = 0$
- $bd = \frac{1}{\sqrt{2}}$

From $ad = 0$: either $a = 0$ or $d = 0$.
From $bc = 0$: either $b = 0$ or $c = 0$.

If $a = 0$, then $ac = 0 \neq \frac{1}{\sqrt{2}}$. Contradiction.
If $d = 0$, then $bd = 0 \neq \frac{1}{\sqrt{2}}$. Contradiction.

Therefore, no such factorization exists. $|\Phi^+\rangle$ is entangled. ∎

### Reduced Density Matrices

When we trace out one qubit of $|\Phi^+\rangle$, we get a maximally mixed state:

$$\rho_A = \text{Tr}_B(|\Phi^+\rangle\langle\Phi^+|) = \frac{1}{2}(|0\rangle\langle 0| + |1\rangle\langle 1|) = \frac{I}{2}$$

This shows that:
- Each qubit individually is completely random
- But together, they are perfectly correlated
- The correlation exists only in the joint state

### Concurrence: Measuring Entanglement

For a pure 2-qubit state $|\psi\rangle = \sum_{ij} a_{ij}|ij\rangle$, the **concurrence** is:

$$C = 2|a_{00}a_{11} - a_{01}a_{10}|$$

- $C = 0$: Product state (no entanglement)
- $C = 1$: Maximally entangled (Bell state)

For $|\Phi^+\rangle$: $a_{00} = a_{11} = \frac{1}{\sqrt{2}}$, $a_{01} = a_{10} = 0$

$$C = 2 \cdot \frac{1}{\sqrt{2}} \cdot \frac{1}{\sqrt{2}} = 1$$ ✓

### The CHSH Bell Inequality

The CHSH inequality tests whether correlations can be explained by **local hidden variables** (classical physics):

$$|S| = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| \leq 2$$

where $E(a,b) = P(same) - P(different)$ is the correlation when Alice measures $a$ and Bob measures $b$.

**Quantum mechanics violates this bound!**

For optimal angles on $|\Phi^+\rangle$:
- Alice: $a = 0$, $a' = \pi/4$
- Bob: $b = \pi/8$, $b' = 3\pi/8$

$$|S|_{quantum} = 2\sqrt{2} \approx 2.83 > 2$$

This violation has been experimentally confirmed countless times. It proves that quantum correlations cannot be explained by any local realistic theory.

## Circuit Diagrams

```
Bell State |Φ+⟩ Creation:
q0: ──H──●──
         │
q1: ─────X──

Bell Measurement (reverse):
q0: ──●──H──M
      │
q1: ──X─────M
```

## Key Properties of Entanglement

| Property | Description |
|----------|-------------|
| Non-separability | Cannot write as product state |
| Perfect correlations | 100% correlation in matching bases |
| Monogamy | Max entanglement with one partner limits entanglement with others |
| Non-cloning | Cannot copy an entangled state |
| No signaling | Entanglement alone cannot transmit information faster than light |

## Running the Code

```bash
cd 02_bell_state
python bell_state.py
```

## Why Entanglement Matters

### Quantum Computing Applications

1. **Quantum Teleportation** (Project 3): Transfer quantum states using entanglement
2. **Superdense Coding**: Send 2 classical bits with 1 qubit + entanglement
3. **Quantum Key Distribution**: Secure communication (BB84, E91 protocols)
4. **Quantum Error Correction**: Entanglement between logical and ancilla qubits
5. **Quantum Algorithms**: Entanglement is essential for speedups (Shor's, Grover's)

### The "Spooky" Part

What makes entanglement seem "spooky"?

1. **Instant correlations**: Measuring one qubit instantly affects the statistics of the other, regardless of distance
2. **But no signaling**: You can't use this to send information faster than light
3. **Not predetermined**: The results aren't decided in advance (Bell inequality violation proves this)

The resolution: Entanglement is a correlation in the quantum probability amplitudes, not a physical influence traveling between particles.

## Exercises

1. **Create all Bell states**: Modify the circuit to create $|\Psi^-\rangle$ directly from $|00\rangle$.

2. **Verify orthonormality**: Show mathematically that $\langle\Phi^+|\Psi^+\rangle = 0$.

3. **GHZ state**: Create the 3-qubit GHZ state $|GHZ\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$ and measure its correlations.

4. **CHSH optimization**: What measurement angles maximize the CHSH violation? Derive them.

## Common Pitfalls

1. **Assuming faster-than-light communication**: Entanglement correlations require classical communication to be useful.

2. **Thinking measurement "causes" the other qubit's state**: Correlation is not causation. The joint state contains all information.

3. **Forgetting normalization**: When analyzing 2-qubit states, ensure $\sum_{ij}|a_{ij}|^2 = 1$.

## Next Steps

In [Project 3: Quantum Teleportation](../03_quantum_teleportation/), we'll use entanglement to transfer an unknown quantum state from one qubit to another—without physically moving the qubit!

## References

1. Einstein, Podolsky, Rosen (1935): "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?"
2. Bell, J.S. (1964): "On the Einstein Podolsky Rosen Paradox"
3. Aspect, A. et al. (1982): Experimental tests of Bell inequalities
4. Nielsen & Chuang, Chapter 2.6: "EPR and the Bell inequality"
