# Project 8: Grover's Search Algorithm

## Overview

Grover's algorithm provides a **quadratic speedup** for unstructured search: finding a marked item among $N$ items with $O(\sqrt{N})$ queries instead of $O(N)$ classically.

## The Problem

Given oracle access to $f: \{0,1\}^n \rightarrow \{0,1\}$ where $f(x^*) = 1$ for a unique $x^*$, find $x^*$.

## Complexity

| Approach | Queries | For N = 1,000,000 |
|----------|---------|-------------------|
| Classical | $O(N)$ | ~500,000 |
| Quantum | $O(\sqrt{N})$ | ~785 |

## The Algorithm

1. **Initialize**: $|\psi\rangle = H^{\otimes n}|0\rangle^{\otimes n}$ (uniform superposition)
2. **Repeat** $\approx \frac{\pi}{4}\sqrt{N}$ times:
   - Apply **Oracle** $O$: $O|x\rangle = (-1)^{f(x)}|x\rangle$
   - Apply **Diffusion** $D$: $D = 2|\psi\rangle\langle\psi| - I$
3. **Measure**: High probability of getting $x^*$

## Geometric Interpretation

The Grover iteration rotates the state vector in a 2D plane spanned by:
- $|w\rangle$ = marked state(s)
- $|s\rangle$ = superposition of unmarked states

Each iteration rotates by angle $2\theta$ where $\sin\theta = \sqrt{M/N}$.

## Optimality

Grover's algorithm is **provably optimal**: no quantum algorithm can do better than $O(\sqrt{N})$ for unstructured search.

## Running the Code

```bash
cd 08_grovers_search
python grovers.py
```
