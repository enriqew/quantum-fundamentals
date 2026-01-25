# Project 5: Bernstein-Vazirani Algorithm

## Overview

The Bernstein-Vazirani algorithm (1993) finds a hidden n-bit string with **one quantum query**, whereas classically you need **n queries**. This demonstrates a linear quantum speedup.

## The Problem

Given oracle access to $f(x) = s \cdot x \pmod{2}$ where $s \in \{0,1\}^n$ is unknown, find $s$.

Here $s \cdot x = s_1x_1 \oplus s_2x_2 \oplus \cdots \oplus s_nx_n$ is the bitwise inner product.

## Query Complexity

| Approach | Queries Required |
|----------|-----------------|
| Classical | $n$ |
| Quantum | $1$ |

## Mathematical Analysis

Using the Hadamard identity:
$$H^{\otimes n}|x\rangle = \frac{1}{\sqrt{2^n}}\sum_y (-1)^{x \cdot y}|y\rangle$$

The algorithm proceeds:

1. **Initialize**: $|0\rangle^{\otimes n}|1\rangle$

2. **Hadamard all**: $\frac{1}{\sqrt{2^n}}\sum_x|x\rangle \otimes |-\rangle$

3. **Oracle (phase kickback)**: $\frac{1}{\sqrt{2^n}}\sum_x(-1)^{s \cdot x}|x\rangle \otimes |-\rangle$

4. **Hadamard input register**:
$$\frac{1}{2^n}\sum_x\sum_y(-1)^{s \cdot x + x \cdot y}|y\rangle = \frac{1}{2^n}\sum_y\left[\sum_x(-1)^{x \cdot (s \oplus y)}\right]|y\rangle$$

5. **Key identity**: $\sum_x(-1)^{x \cdot z} = 2^n$ if $z=0$, else $0$

6. **Result**: Only $y = s$ survives → measure $|s\rangle$ with certainty!

## Running the Code

```bash
cd 05_bernstein_vazirani
python bernstein_vazirani.py
```

## Exercises

1. Extend to find two hidden strings: $f(x) = s_1 \cdot x \oplus s_2 \cdot x$

2. What if the oracle has noise (small probability of returning wrong value)?

## References

1. Bernstein, E. & Vazirani, U. (1993): "Quantum Complexity Theory"
2. Nielsen & Chuang, Section 1.4.4
