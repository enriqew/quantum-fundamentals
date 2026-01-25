# Project 6: Quantum Fourier Transform

## Overview

The Quantum Fourier Transform (QFT) is the quantum analog of the classical Discrete Fourier Transform. It's the key subroutine in Shor's factoring algorithm, quantum phase estimation, and many other quantum algorithms.

## The Transform

The QFT maps computational basis states to Fourier basis states:

$$\text{QFT}|j\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi ijk/N}|k\rangle$$

where $N = 2^n$ for $n$ qubits.

## Product Representation

The key insight enabling efficient implementation:

$$\text{QFT}|j_1 j_2 \cdots j_n\rangle = \bigotimes_{m=1}^{n} \frac{|0\rangle + e^{2\pi i \cdot 0.j_m j_{m+1}\cdots j_n}|1\rangle}{\sqrt{2}}$$

where $0.j_m j_{m+1}\cdots j_n = j_m/2 + j_{m+1}/4 + \cdots + j_n/2^{n-m+1}$.

## Circuit Complexity

| Operation | Classical FFT | Quantum QFT |
|-----------|--------------|-------------|
| Operations/Gates | $O(n \cdot 2^n)$ | $O(n^2)$ |
| Space | $O(2^n)$ | $O(n)$ qubits |

**Exponential speedup in gate count!**

## Circuit Structure

```
QFT on 3 qubits:
q0: ──H──R₂──R₃──────────────×──
         │   │               │
q1: ─────●───┼───H──R₂──────×──
             │       │       │
q2: ─────────●───────●───H───×──
```

Where $R_k = \text{diag}(1, e^{2\pi i/2^k})$.

## Running the Code

```bash
cd 06_quantum_fourier_transform
python qft.py
```

## Key Properties

1. **Unitarity**: $\text{QFT}^\dagger \cdot \text{QFT} = I$
2. **Symmetry**: QFT matrix is symmetric
3. **Periodicity detection**: QFT reveals periodicities in quantum states

## References

1. Nielsen & Chuang, Section 5.1: "The quantum Fourier transform"
2. Coppersmith (1994): "An approximate Fourier transform useful in quantum factoring"
