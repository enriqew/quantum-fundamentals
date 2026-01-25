# Project 11: Shor's Algorithm

## Overview

Shor's algorithm (1994) factors integers in **polynomial time**, providing an exponential speedup over the best known classical algorithms. This breaks RSA, Diffie-Hellman, and elliptic curve cryptography.

## Complexity Comparison

| Algorithm | Complexity |
|-----------|------------|
| Classical (GNFS) | $O(\exp(c \cdot n^{1/3} (\ln n)^{2/3}))$ |
| Quantum (Shor) | $O(n^3)$ |

For $n$-bit numbers, this is an **exponential speedup**.

---

## Mathematical Foundations

### Theorem 1: Reduction from Factoring to Order-Finding

**Statement**: Given an oracle for finding multiplicative orders modulo $N$, we can factor $N$ with probability $\geq 1/2$.

**Proof**:

Let $N = pq$ where $p, q$ are distinct odd primes.

1. Choose random $a$ with $\gcd(a, N) = 1$
2. Find $r = \text{ord}_N(a)$, the smallest positive integer with $a^r \equiv 1 \pmod{N}$
3. If $r$ is even, compute $x = a^{r/2} \mod N$
4. We have $x^2 \equiv 1 \pmod{N}$, so $(x-1)(x+1) \equiv 0 \pmod{N}$
5. Unless $x \equiv \pm 1 \pmod{N}$, $\gcd(x \pm 1, N)$ yields a non-trivial factor

**Key Lemma**: For random $a$ coprime to $N = pq$:
$$P(r \text{ is even} \land a^{r/2} \not\equiv \pm 1 \pmod{N}) \geq \frac{1}{2}$$

### Theorem 2: Quantum Order-Finding

**Goal**: Find $r$ such that $a^r \equiv 1 \pmod{N}$.

**Method**: Use phase estimation on the unitary $U|y\rangle = |ay \mod N\rangle$.

**Key Insight**: The eigenstates of $U$ are:
$$|u_s\rangle = \frac{1}{\sqrt{r}} \sum_{k=0}^{r-1} e^{-2\pi i sk/r} |a^k \mod N\rangle$$

with eigenvalues $e^{2\pi i s/r}$ for $s = 0, 1, \ldots, r-1$.

**Critical Observation**:
$$|1\rangle = \frac{1}{\sqrt{r}} \sum_{s=0}^{r-1} |u_s\rangle$$

Starting from $|1\rangle$, phase estimation gives a random phase $s/r$.

### Theorem 3: Continued Fractions

**Best Rational Approximation Theorem**: If $|x - p/q| < 1/(2q^2)$, then $p/q$ is a convergent of the continued fraction expansion of $x$.

**Application**: With $t$ precision qubits where $2^t > N^2$:
- Measured value: $m \approx 2^t \cdot s/r$
- Approximation: $|m/2^t - s/r| < 1/(2 \cdot 2^t) < 1/(2r^2)$
- Therefore $s/r$ appears as a convergent!

---

## The Complete Algorithm

```
Algorithm: SHOR(N)
───────────────────
1. If N is even, return (2, N/2)
2. Check if N = a^b for integers a, b ≥ 2
3. Repeat:
   a. Choose random a ∈ [2, N-2]
   b. If gcd(a, N) > 1, return (gcd(a, N), N/gcd(a, N))
   c. Use quantum order-finding to get r = ord_N(a)
   d. If r is odd, goto step 3
   e. Compute x = a^(r/2) mod N
   f. If x ≡ -1 (mod N), goto step 3
   g. Return (gcd(x-1, N), gcd(x+1, N))
```

---

## Quantum Circuit

```
Precision Register:   |0⟩─H─────●─────●─────●─────┬─QFT†─M
                      |0⟩─H────┼────●─────●──────┤
                      |0⟩─H───┼───┼────●────────┤
                           ...                   │
                                                 │
Work Register:        |1⟩─────U¹───U²───U⁴──────┴───────
                             ↑     ↑     ↑
                        a mod N  a² mod N  a⁴ mod N
```

---

## Cryptographic Implications

### Algorithms Broken by Shor:
1. **RSA** (integer factorization)
2. **Diffie-Hellman** (discrete logarithm)
3. **ECDSA/ECDH** (elliptic curve discrete log)

### Post-Quantum Cryptography

NIST PQC Standards (2024):
- **CRYSTALS-Kyber** (key encapsulation) - lattice-based
- **CRYSTALS-Dilithium** (signatures) - lattice-based
- **FALCON** (signatures) - lattice-based
- **SPHINCS+** (signatures) - hash-based

---

## Running the Code

```bash
cd 11_shors_algorithm
python shors.py
```

---

## References

1. Shor, P. (1994): "Algorithms for quantum computation: discrete logarithms and factoring"
2. Nielsen & Chuang, Chapter 5.3: "Applications: order-finding and factoring"
3. Ekert, A. & Jozsa, R. (1996): "Quantum computation and Shor's factoring algorithm"
4. NIST Post-Quantum Cryptography: https://csrc.nist.gov/projects/post-quantum-cryptography
