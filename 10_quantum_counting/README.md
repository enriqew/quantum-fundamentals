# Project 10: Quantum Counting

## Overview

Quantum Counting combines Grover's search with Phase Estimation to **count** the number of solutions without finding them all. This is useful when you need to know how many solutions exist before committing to a full search.

## The Problem

Given oracle $f: \{0,1\}^n \rightarrow \{0,1\}$, estimate $M = |\{x : f(x) = 1\}|$.

## Key Insight

The Grover iterator $G = D \cdot O$ has eigenvalues $e^{\pm 2i\theta}$ where:
$$\sin^2(\theta) = \frac{M}{N}$$

Phase estimation on $G$ gives $\theta$, from which we compute $M$.

## Algorithm Steps

1. Prepare counting register in superposition
2. Prepare search register in uniform superposition
3. Apply controlled-$G^{2^k}$ operations
4. Apply inverse QFT to counting register
5. Measure to get $\theta$
6. Compute $M = N \cdot \sin^2(\theta)$

## Amplitude Estimation

Generalization: Given state $|\psi\rangle = \sin(\theta)|good\rangle + \cos(\theta)|bad\rangle$, estimate $\sin^2(\theta)$ with quadratic speedup over classical sampling.

## Applications

- Pre-counting before search
- Monte Carlo integration
- Financial modeling
