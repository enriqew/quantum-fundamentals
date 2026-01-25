# Project 9: Quantum Simulation

## Overview

Simulating quantum systems is one of the most promising applications of quantum computers. As Feynman observed: "Nature isn't classical, dammit, and if you want to make a simulation of nature, you'd better make it quantum mechanical."

## The Problem

Simulate the time evolution of a quantum system:
$$|\psi(t)\rangle = e^{-iHt}|\psi(0)\rangle$$

| Method | Complexity |
|--------|------------|
| Classical | $O(2^n)$ - exponential in system size |
| Quantum | $O(\text{poly}(n, t, 1/\epsilon))$ |

## Trotterization

Decompose $e^{-iHt}$ into implementable gates using the Suzuki-Trotter formula:
$$e^{-i(A+B)t} \approx (e^{-iAt/n}e^{-iBt/n})^n + O(t^2/n)$$

## Key Models

1. **Ising Model**: $H = -J\sum_i Z_iZ_{i+1} - h\sum_i X_i$
2. **Heisenberg Model**: $H = J\sum_i (\vec{\sigma}_i \cdot \vec{\sigma}_{i+1})$
3. **Molecular Hamiltonians**: Chemistry simulations

## VQE (Variational Quantum Eigensolver)

Hybrid quantum-classical algorithm for finding ground states:
1. Prepare parameterized quantum state $|\psi(\theta)\rangle$
2. Measure energy expectation $\langle\psi|H|\psi\rangle$
3. Classical optimizer updates $\theta$
4. Repeat until convergence
