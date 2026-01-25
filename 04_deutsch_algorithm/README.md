# Project 4: Deutsch and Deutsch-Jozsa Algorithm

## Overview

The Deutsch algorithm (1985) is the **first quantum algorithm to demonstrate a speedup** over classical computation. It determines whether a Boolean function is constant or balanced using only ONE query, whereas classical algorithms require TWO.

The Deutsch-Jozsa algorithm generalizes this to n-bit inputs, achieving an **exponential speedup**.

## Learning Objectives

- Understand quantum parallelism
- Master the phase kickback technique
- See how interference extracts global properties
- Compare quantum vs classical query complexity

## The Problem

### Deutsch Problem (1 bit)
Given a function $f: \{0,1\} \rightarrow \{0,1\}$, determine:
- Is $f$ **constant**? ($f(0) = f(1)$)
- Is $f$ **balanced**? ($f(0) \neq f(1)$)

### Deutsch-Jozsa Problem (n bits)
Given $f: \{0,1\}^n \rightarrow \{0,1\}$, **promised** to be either:
- **Constant**: $f(x)$ is the same for all $x$
- **Balanced**: $f(x) = 0$ for exactly half of all inputs

Determine which case applies.

## Query Complexity

| Algorithm | Classical Queries | Quantum Queries |
|-----------|------------------|-----------------|
| Deutsch (n=1) | 2 | 1 |
| Deutsch-Jozsa (n bits) | $2^{n-1} + 1$ worst case | 1 |

This is an **exponential speedup**!

## Mathematical Foundation

### Phase Kickback

The oracle implements: $U_f|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle$

When the ancilla is in state $|-\rangle = \frac{1}{\sqrt{2}}(|0\rangle - |1\rangle)$:

$$U_f|x\rangle|-\rangle = (-1)^{f(x)}|x\rangle|-\rangle$$

The function value $f(x)$ becomes a **phase** on $|x\rangle$.

### Deutsch Algorithm Analysis

**Step 1**: Start with $|0\rangle|1\rangle$

**Step 2**: Apply $H \otimes H$:
$$|+\rangle|-\rangle = \frac{1}{2}(|0\rangle + |1\rangle)(|0\rangle - |1\rangle)$$

**Step 3**: Apply oracle $U_f$:
$$\frac{1}{\sqrt{2}}((-1)^{f(0)}|0\rangle + (-1)^{f(1)}|1\rangle)|-\rangle$$

$$= \frac{(-1)^{f(0)}}{\sqrt{2}}(|0\rangle + (-1)^{f(0) \oplus f(1)}|1\rangle)|-\rangle$$

**Step 4**: Apply $H$ to first qubit:
- If $f(0) \oplus f(1) = 0$ (constant): $H|+\rangle = |0\rangle$
- If $f(0) \oplus f(1) = 1$ (balanced): $H|-\rangle = |1\rangle$

**Step 5**: Measure first qubit → reveals answer with certainty!

### Deutsch-Jozsa Analysis

For n input qubits, after Step 2:
$$\frac{1}{\sqrt{2^n}}\sum_{x=0}^{2^n-1}|x\rangle \otimes |-\rangle$$

After oracle:
$$\frac{1}{\sqrt{2^n}}\sum_{x=0}^{2^n-1}(-1)^{f(x)}|x\rangle \otimes |-\rangle$$

After Hadamard on input register:
$$\frac{1}{2^n}\sum_{y=0}^{2^n-1}\left(\sum_{x=0}^{2^n-1}(-1)^{f(x)+x \cdot y}\right)|y\rangle$$

The amplitude of $|0\rangle^{\otimes n}$ is:
$$\frac{1}{2^n}\sum_{x=0}^{2^n-1}(-1)^{f(x)}$$

- **Constant $f$**: All terms have same sign → amplitude = $\pm 1$
- **Balanced $f$**: Half +1, half -1 → amplitude = 0

Measuring $|0\rangle^{\otimes n}$ with certainty means constant; any other outcome means balanced.

## Circuit Diagram

```
Deutsch Algorithm:
q0: ──H──────●────H──M
             │
q1: ──X──H───┼───────
             Uf

Deutsch-Jozsa (n=3):
q0: ──H──────┬────H──M
             │
q1: ──H──────┼────H──M
             │
q2: ──H──────┼────H──M
             Uf
q3: ──X──H───┴───────
```

## Running the Code

```bash
cd 04_deutsch_algorithm
python deutsch.py
```

## Why This Matters

1. **First proof of quantum advantage**: Even for a simple problem, quantum wins
2. **Introduces key techniques**: Phase kickback, interference
3. **Foundation for other algorithms**: Bernstein-Vazirani, Simon's algorithm
4. **Conceptual importance**: Shows quantum parallelism is real

## Limitations

- **Promise problem**: We're promised the function is constant or balanced
- **Black-box model**: We only count oracle queries, not gate complexity
- **Artificial problem**: Not directly useful for practical applications

But it proves: **Quantum computers can outperform classical computers!**

## Exercises

1. **Verify the math**: Work through the Deutsch-Jozsa algorithm for n=2 by hand.

2. **Create a random balanced function**: Design an oracle for a randomly chosen balanced function on 4 bits.

3. **Error analysis**: What happens if the function is neither constant nor balanced?

## References

1. Deutsch, D. (1985): "Quantum theory, the Church-Turing principle and the universal quantum computer"
2. Deutsch, D. & Jozsa, R. (1992): "Rapid solution of problems by quantum computation"
3. Nielsen & Chuang, Section 1.4.4: "Deutsch's algorithm"
