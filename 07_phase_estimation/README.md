# Project 7: Quantum Phase Estimation

## Overview

Quantum Phase Estimation (QPE) extracts eigenvalues from unitary operators. Given $U|\psi\rangle = e^{2\pi i\phi}|\psi\rangle$, QPE estimates $\phi$ with $n$ bits of precision using $O(n)$ controlled operations.

## The Algorithm

1. **Initialize**: $|0\rangle^{\otimes n}|\psi\rangle$
2. **Hadamard**: Apply $H^{\otimes n}$ to precision register
3. **Controlled-$U^{2^k}$**: Apply controlled powers of $U$
4. **Inverse QFT**: Convert phase to binary
5. **Measure**: Read out $\phi$

## Mathematical Foundation

After controlled operations:
$$\frac{1}{\sqrt{2^n}}\sum_{j=0}^{2^n-1} e^{2\pi ij\phi}|j\rangle|\psi\rangle$$

Inverse QFT extracts $\phi$:
$$|\tilde{\phi}\rangle|\psi\rangle$$

where $\tilde{\phi}$ is the $n$-bit binary approximation.

## Precision

- **$n$ precision bits**: Error $\leq 1/2^n$
- **Success probability**: $\geq 4/\pi^2 \approx 0.405$ for exact representation

## Applications

1. **Shor's algorithm**: Extract period via order-finding
2. **Quantum simulation**: Eigenvalue problems
3. **HHL algorithm**: Linear systems solving
