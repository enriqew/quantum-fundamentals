#!/usr/bin/env python3
"""
Project 11: Shor's Algorithm

Shor's algorithm factors integers in polynomial time, breaking RSA encryption.
This is the most famous quantum algorithm and the primary motivation for
building large-scale quantum computers.

Key Concepts:
- Reduction from factoring to order-finding
- Quantum Fourier Transform for period detection
- Continued fractions for period extraction
- Modular exponentiation

Complexity:
    Classical (Number Field Sieve): O(exp((64/9)^(1/3) (ln N)^(1/3) (ln ln N)^(2/3)))
    Quantum (Shor): O((log N)^3) with polynomial space

Scope, stated up front. The classical half of Shor is complete and rigorous:
reduction to order-finding, continued fractions, and factor recovery. The
quantum half is not. `qft_circuit` and `inverse_qft_circuit` are implemented
and correct, but `controlled_modular_multiplication` is a stub, nothing calls
the QFT helpers from main(), and order-finding runs through
`classical_order_finding`. So this file demonstrates the structure of the
algorithm and computes correct factorisations, but it does not factor anything
quantumly. Building the controlled modular arithmetic is the open work here.
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from fractions import Fraction
import random

import numpy as np
import matplotlib.pyplot as plt

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from braket.circuits import Circuit
from braket.devices import LocalSimulator

from shared.braket_utils import run_circuit, get_state_vector
from shared.math_utils import (
    gcd, mod_pow, is_prime, continued_fraction, convergents,
    classical_order_finding, factor_from_order, is_perfect_power
)


# =============================================================================
# PART 1: MATHEMATICAL FOUNDATIONS
# =============================================================================

def factoring_to_order_finding_proof() -> None:
    """
    Rigorous proof that factoring reduces to order-finding.

    Theorem: Given an algorithm for order-finding, we can factor N
    in polynomial time with high probability.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║        THEOREM: Reduction from Factoring to Order-Finding        ║
╚══════════════════════════════════════════════════════════════════╝

STATEMENT:
    If we can find the multiplicative order r of a random a mod N,
    then we can factor N with probability ≥ 1/2.

DEFINITIONS:
    • Multiplicative order: r is the smallest positive integer where
      a^r ≡ 1 (mod N)
    • For this to exist, gcd(a, N) = 1

PROOF:

    Given: N = p·q (product of two distinct odd primes)
           a random element with gcd(a, N) = 1
           r = ord_N(a) (the order of a modulo N)

    Step 1: Structure of r
    ─────────────────────
    By the Chinese Remainder Theorem:
        a^r ≡ 1 (mod N) ⟺ a^r ≡ 1 (mod p) AND a^r ≡ 1 (mod q)

    Let r_p = ord_p(a), r_q = ord_q(a).
    Then r = lcm(r_p, r_q).

    Step 2: When r is even
    ──────────────────────
    Suppose r is even. Then consider x = a^(r/2) mod N.

    We have: x² ≡ a^r ≡ 1 (mod N)
    So: x² - 1 ≡ 0 (mod N)
    Thus: (x-1)(x+1) ≡ 0 (mod N)

    This means N | (x-1)(x+1).

    Step 3: Excluding trivial cases
    ────────────────────────────────
    Case x ≡ 1 (mod N): Then gcd(x-1, N) = N. No factor found.
    Case x ≡ -1 (mod N): Then gcd(x+1, N) = N. No factor found.

    Otherwise: gcd(x-1, N) or gcd(x+1, N) is a non-trivial factor!

    Step 4: Probability analysis
    ────────────────────────────
    The key lemma (proof in references):
        For random a coprime to N = p·q:
        P(r is even AND a^(r/2) ≢ ±1 (mod N)) ≥ 1/2

    This is because:
    • r = lcm(r_p, r_q) is even unless both r_p and r_q are odd
    • The probability both are odd is at most 1/2
    • Even if r is even, a^(r/2) ≡ -1 (mod N) only if special conditions hold

    CONCLUSION:
    ───────────
    With probability ≥ 1/2, a random a gives:
    1. An even order r
    2. gcd(a^(r/2) ± 1, N) is a non-trivial factor

    Repeating O(log(1/ε)) times gives success probability 1-ε. ∎
    """)


def order_finding_with_qft_proof() -> None:
    """
    Prove how QFT extracts the period in order-finding.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║            THEOREM: Order-Finding via Phase Estimation           ║
╚══════════════════════════════════════════════════════════════════╝

GOAL: Find r such that a^r ≡ 1 (mod N), given a and N.

QUANTUM APPROACH:
    Define unitary U: |y⟩ ↦ |ay mod N⟩ for y < N
                      |y⟩ ↦ |y⟩ for y ≥ N

    Eigenvalues: U|u_s⟩ = e^(2πis/r)|u_s⟩ for s = 0, 1, ..., r-1
    where |u_s⟩ = (1/√r) Σ_{k=0}^{r-1} e^(-2πisk/r)|a^k mod N⟩

PROOF THAT |1⟩ ENCODES ALL EIGENPHASES:
    Claim: |1⟩ = (1/√r) Σ_{s=0}^{r-1} |u_s⟩

    Proof:
    (1/√r) Σ_s |u_s⟩ = (1/√r) Σ_s (1/√r) Σ_k e^(-2πisk/r)|a^k⟩
                     = (1/r) Σ_k |a^k⟩ Σ_s e^(-2πisk/r)
                     = (1/r) Σ_k |a^k⟩ · r·δ_{k,0}
                     = |a^0⟩ = |1⟩ ✓

PHASE ESTIMATION CIRCUIT:
    1. Initialize: |0⟩^⊗t |1⟩  (t precision qubits, 1 work register)

    2. Hadamard: (1/√2^t) Σ_j |j⟩ |1⟩

    3. Controlled-U^(2^k):
       (1/√2^t) Σ_j |j⟩ U^j|1⟩

       Since |1⟩ = (1/√r) Σ_s |u_s⟩:
       = (1/√2^t) (1/√r) Σ_j Σ_s |j⟩ e^(2πijs/r)|u_s⟩
       = (1/√r) Σ_s [(1/√2^t) Σ_j e^(2πijs/r)|j⟩] |u_s⟩

    4. Inverse QFT on first register:
       QFT^{-1}[(1/√2^t) Σ_j e^(2πijs/r)|j⟩] ≈ |⌊2^t · s/r⌉⟩

       for some s ∈ {0, 1, ..., r-1}

MEASUREMENT OUTCOME:
    We measure m ≈ 2^t · s/r for random s.
    Thus m/2^t ≈ s/r is a rational approximation to s/r.

EXTRACTING r VIA CONTINUED FRACTIONS:
    The continued fraction algorithm finds the best rational approximation
    p/q to m/2^t with q < 2^t.

    If gcd(s, r) = 1 (probability ≥ φ(r)/r ≥ 1/log(r)):
        The convergent s/r is found exactly!
        We get r as the denominator.
    """)


def continued_fraction_theory() -> None:
    """
    Explain continued fraction expansion theory.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                  CONTINUED FRACTION EXPANSION                     ║
╚══════════════════════════════════════════════════════════════════╝

DEFINITION:
    Any real x can be written as:
    x = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + ...)))

    Notation: x = [a₀; a₁, a₂, a₃, ...]
    The aᵢ are called partial quotients.

ALGORITHM:
    a₀ = ⌊x⌋
    x₁ = 1/(x - a₀)
    a₁ = ⌊x₁⌋
    x₂ = 1/(x₁ - a₁)
    ... and so on until xₙ is an integer.

CONVERGENTS:
    The k-th convergent pₖ/qₖ is [a₀; a₁, ..., aₖ].

    Recurrence relations:
        p₋₁ = 1, p₀ = a₀
        q₋₁ = 0, q₀ = 1
        pₖ = aₖ·pₖ₋₁ + pₖ₋₂
        qₖ = aₖ·qₖ₋₁ + qₖ₋₂

KEY THEOREM (Best Rational Approximation):
    If |x - p/q| < 1/(2q²), then p/q is a convergent of x.

APPLICATION TO SHOR:
    Measured value: m
    Precision: 2^t where 2^t > N²
    True fraction: s/r where r < N

    We have: |m/2^t - s/r| < 1/(2·2^t) < 1/(2N²) < 1/(2r²)

    By the theorem, s/r appears as a convergent of m/2^t!

EXAMPLE:
    Suppose r = 7, s = 3, t = 10 (so 2^t = 1024)
    True value: 3/7 = 0.428571...
    Measured: m = 439 (closest to 1024 × 3/7 ≈ 438.86)
    m/2^t = 439/1024 = 0.428711...

    Continued fraction of 439/1024:
    [0; 2, 3, 12, 2, 2] with convergents:
    0/1, 1/2, 3/7, 37/86, 77/180, ...

    The convergent 3/7 gives us r = 7! ✓
    """)


def complexity_analysis() -> None:
    """
    Detailed complexity analysis of Shor's algorithm.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                      COMPLEXITY ANALYSIS                          ║
╚══════════════════════════════════════════════════════════════════╝

CLASSICAL FACTORING:
────────────────────
    Best known: General Number Field Sieve (GNFS)
    Time: O(exp((64/9)^(1/3) · (ln N)^(1/3) · (ln ln N)^(2/3)))

    This is SUB-EXPONENTIAL but SUPER-POLYNOMIAL.

    For N = 2^n (n-bit number):
    GNFS: O(exp(c · n^(1/3) · (ln n)^(2/3)))

    Example: For a 2048-bit RSA modulus:
    Estimated classical time: ~10^12 years with current hardware

QUANTUM FACTORING (SHOR):
─────────────────────────
    Components:
    1. Modular exponentiation: O((log N)³) gates
    2. QFT: O((log N)²) gates
    3. Classical post-processing: O((log N)³) operations

    Total: O((log N)³) = O(n³) quantum gates

    For a 2048-bit number:
    Quantum: ~10^10 gates (feasible with error correction)

QUBIT REQUIREMENTS:
───────────────────
    Standard implementation:
    - 2n qubits for phase estimation register
    - n qubits for modular exponentiation workspace
    - Total: ~3n qubits + ancilla for error correction

    For 2048-bit RSA: ~6000-8000 logical qubits
    With error correction: ~millions of physical qubits

SPEEDUP:
────────
    | n (bits) | Classical (years) | Quantum (ops)  |
    |----------|-------------------|----------------|
    | 512      | ~10^4             | ~10^8          |
    | 1024     | ~10^8             | ~10^9          |
    | 2048     | ~10^12            | ~10^10         |
    | 4096     | ~10^18            | ~10^11         |

    EXPONENTIAL speedup!
    """)


def cryptographic_implications() -> None:
    """
    Discuss the cryptographic implications of Shor's algorithm.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                  CRYPTOGRAPHIC IMPLICATIONS                       ║
╚══════════════════════════════════════════════════════════════════╝

ALGORITHMS BROKEN BY SHOR:
──────────────────────────
    1. RSA (factoring)
    2. Diffie-Hellman (discrete log)
    3. Elliptic Curve Cryptography (discrete log on curves)
    4. DSA, ECDSA (digital signatures)

WHY RSA IS VULNERABLE:
──────────────────────
    RSA Security:
    - Public key: (N, e) where N = p·q
    - Private key: d ≡ e^(-1) (mod φ(N))
    - φ(N) = (p-1)(q-1) requires knowing p, q

    Shor's attack:
    1. Factor N to get p, q
    2. Compute φ(N) = (p-1)(q-1)
    3. Compute d ≡ e^(-1) (mod φ(N))
    4. Decrypt any message!

TIMELINE CONCERNS:
──────────────────
    Current state (2024):
    - Largest number factored quantumly: 21 (on small devices)
    - Error-corrected qubits: ~tens
    - Needed for RSA-2048: ~millions of physical qubits

    Projections:
    - 2030s: Possibly break RSA-1024
    - 2040s: Possibly break RSA-2048

    "HARVEST NOW, DECRYPT LATER":
    - Adversaries collect encrypted data today
    - Decrypt when quantum computers arrive
    - Critical for long-term secrets!

POST-QUANTUM CRYPTOGRAPHY:
──────────────────────────
    NIST PQC Standards (2024):
    1. CRYSTALS-Kyber (key encapsulation)
    2. CRYSTALS-Dilithium (signatures)
    3. FALCON (signatures)
    4. SPHINCS+ (signatures, hash-based)

    Based on problems believed quantum-resistant:
    - Lattice problems (LWE, RLWE)
    - Hash-based signatures
    - Code-based cryptography
    """)


# =============================================================================
# PART 2: IMPLEMENTATION
# =============================================================================

def controlled_modular_multiplication(
    circuit: Circuit,
    control: int,
    target_qubits: List[int],
    a: int,
    N: int
) -> Circuit:
    """
    Apply controlled multiplication by a modulo N.

    |y⟩ → |a·y mod N⟩ if control is |1⟩

    This is simplified for demonstration. Full implementation requires
    reversible arithmetic circuits.
    """
    # For demonstration, we use a simplified approach
    # Real implementation would use modular multiplication circuits
    n = len(target_qubits)

    # This is a placeholder - real implementation is complex
    # Would need reversible adders, subtractors, and comparators
    pass

    return circuit


def qft_circuit(circuit: Circuit, qubits: List[int]) -> Circuit:
    """Apply QFT to specified qubits."""
    n = len(qubits)

    for i in range(n):
        circuit.h(qubits[i])
        for j in range(i + 1, n):
            angle = 2 * np.pi / (2 ** (j - i + 1))
            circuit.cphaseshift(qubits[j], qubits[i], angle)

    # Swap for correct ordering
    for i in range(n // 2):
        circuit.swap(qubits[i], qubits[n - 1 - i])

    return circuit


def inverse_qft_circuit(circuit: Circuit, qubits: List[int]) -> Circuit:
    """Apply inverse QFT to specified qubits."""
    n = len(qubits)

    # Swap for correct ordering
    for i in range(n // 2):
        circuit.swap(qubits[i], qubits[n - 1 - i])

    for i in range(n - 1, -1, -1):
        for j in range(n - 1, i, -1):
            angle = -2 * np.pi / (2 ** (j - i + 1))
            circuit.cphaseshift(qubits[j], qubits[i], angle)
        circuit.h(qubits[i])

    return circuit


def classical_part_of_shor(N: int, max_attempts: int = 10) -> Optional[Tuple[int, int]]:
    """
    The classical part of Shor's algorithm.

    1. Check for trivial factors
    2. Check if N is a perfect power
    3. Choose random a and check gcd
    4. Call quantum order-finding (simulated classically here)
    5. Use continued fractions to extract r
    6. Attempt to factor using r

    Args:
        N: Number to factor

    Returns:
        Tuple of factors, or None if failed
    """
    print(f"\nFactoring N = {N}")
    print("-" * 40)

    # Step 1: Trivial checks
    if N % 2 == 0:
        return (2, N // 2)

    # Step 2: Check if perfect power
    power_result = is_perfect_power(N)
    if power_result:
        base, exp = power_result
        print(f"  N = {base}^{exp} is a perfect power")
        return (base, N // base)

    # Step 3: Main loop
    for attempt in range(max_attempts):
        print(f"\n  Attempt {attempt + 1}:")

        # Choose random a
        a = random.randint(2, N - 2)
        print(f"    Chose a = {a}")

        # Check gcd
        g = gcd(a, N)
        if g > 1:
            print(f"    Lucky! gcd(a, N) = {g} is a factor")
            return (g, N // g)

        # Find order (quantum part - simulated classically)
        r = classical_order_finding(a, N)
        print(f"    Order r = {r}")

        if r == -1:
            continue

        # Check if r is even
        if r % 2 != 0:
            print(f"    Order {r} is odd, trying another a")
            continue

        # Compute a^(r/2) mod N
        x = mod_pow(a, r // 2, N)
        print(f"    a^(r/2) mod N = {x}")

        # Check if x ≡ -1 (mod N)
        if x == N - 1:
            print(f"    x ≡ -1 (mod N), trying another a")
            continue

        # Attempt factorization
        result = factor_from_order(a, r, N)
        if result:
            p, q = result
            print(f"    SUCCESS! Found factors: {p} × {q}")
            return result

    print("  Failed to factor after max attempts")
    return None


def simulate_quantum_order_finding(a: int, N: int, n_precision: int = 8) -> int:
    """
    Simulate the quantum order-finding part of Shor's algorithm.

    In a real implementation, this would:
    1. Create superposition over all exponents
    2. Apply controlled modular exponentiation
    3. Apply inverse QFT
    4. Measure and use continued fractions

    For demonstration, we simulate the measurement outcomes.

    Args:
        a: Base for modular exponentiation
        N: Modulus
        n_precision: Number of precision qubits

    Returns:
        Estimated order r
    """
    # Get the true order (classically, for simulation)
    true_r = classical_order_finding(a, N)
    if true_r == -1:
        return -1

    # Simulate quantum measurement
    # QPE would give us m ≈ 2^n · s/r for random s coprime to r
    n = 2 ** n_precision

    # Choose random s coprime to r
    s = random.randint(1, true_r - 1)
    while gcd(s, true_r) != 1:
        s = random.randint(1, true_r - 1)

    # Simulated measurement
    m = round(n * s / true_r)
    measured_phase = m / n

    print(f"    Simulated QPE: measured phase ≈ {m}/{n} = {measured_phase:.6f}")
    print(f"    True value: s/r = {s}/{true_r} = {s/true_r:.6f}")

    # Use continued fractions to extract r
    cf = continued_fraction(measured_phase, max_terms=20)
    convs = convergents(cf)

    print(f"    Continued fraction: {cf[:5]}...")
    print(f"    Convergents: {convs[:5]}...")

    # Find convergent with denominator < N
    for num, denom in convs:
        if denom > 0 and denom < N:
            # Check if this is the order
            if mod_pow(a, denom, N) == 1:
                print(f"    Found order candidate: {denom}")
                return denom

    # If exact match not found, return the best guess
    for num, denom in reversed(convs):
        if denom < N and denom > 0:
            return denom

    return -1


def run_shors_algorithm(N: int) -> Optional[Tuple[int, int]]:
    """
    Run complete Shor's algorithm (simulated quantum part).

    Args:
        N: Number to factor

    Returns:
        Tuple of factors, or None if failed
    """
    print("\n" + "=" * 60)
    print(f"SHOR'S ALGORITHM: Factoring N = {N}")
    print("=" * 60)

    # Pre-checks
    if is_prime(N):
        print(f"{N} is prime!")
        return None

    if N % 2 == 0:
        print(f"N is even: {N} = 2 × {N//2}")
        return (2, N // 2)

    # Run the algorithm
    result = classical_part_of_shor(N, max_attempts=10)

    if result:
        p, q = result
        assert p * q == N, "Factorization verification failed!"
        print(f"\n✓ Verified: {p} × {q} = {N}")

    return result


# =============================================================================
# PART 3: DEMONSTRATIONS
# =============================================================================

def demonstrate_small_examples() -> None:
    """
    Demonstrate Shor's algorithm on small numbers.
    """
    print("\n" + "=" * 60)
    print("SMALL NUMBER DEMONSTRATIONS")
    print("=" * 60)

    test_numbers = [15, 21, 35, 77, 91, 143, 221, 323]

    for N in test_numbers:
        result = run_shors_algorithm(N)
        print()


def visualize_phase_distribution() -> None:
    """
    Visualize the phase measurement distribution.
    """
    print("\n" + "=" * 60)
    print("Generating Visualizations")
    print("=" * 60)

    # Example: a=7, N=15, r=4
    a, N, r = 7, 15, 4
    n_precision = 8
    n = 2 ** n_precision

    # Theoretical measurement probabilities
    phases = [s/r for s in range(r)]
    measurements = [round(n * phase) for phase in phases]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Measurement distribution
    all_m = np.arange(n)
    probs = np.zeros(n)
    for s in range(r):
        m = round(n * s / r)
        probs[m] = 1/r

    axes[0].bar(all_m, probs, color='steelblue', alpha=0.7)
    axes[0].set_xlabel('Measurement m')
    axes[0].set_ylabel('Probability')
    axes[0].set_title(f'QPE Measurement Distribution\na={a}, N={N}, r={r}')
    axes[0].set_xlim(-5, n+5)

    # Mark the peaks
    for s in range(r):
        m = round(n * s / r)
        axes[0].annotate(f's={s}', (m, 1/r + 0.02), ha='center')

    # Plot 2: Continued fraction convergence
    # For measured value m=192 (corresponding to s=3, r=4)
    m = 192
    measured_phase = m / n

    cf = continued_fraction(measured_phase, max_terms=10)
    convs = convergents(cf)

    indices = range(len(convs))
    values = [p/q if q > 0 else 0 for p, q in convs]
    denominators = [q for p, q in convs]

    axes[1].plot(indices, values, 'bo-', markersize=8, label='Convergent value')
    axes[1].axhline(y=3/4, color='r', linestyle='--', label=f'True value s/r={3}/{4}')
    axes[1].set_xlabel('Convergent index')
    axes[1].set_ylabel('Value p/q')
    axes[1].set_title(f'Continued Fraction Convergence\nm={m}, m/2^{n_precision}={measured_phase}')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "shor_analysis.png", dpi=150)
    print("Saved: shor_analysis.png")

    plt.close('all')


def main() -> None:
    """
    Main entry point for Shor's algorithm demonstration.
    """
    print("╔" + "═" * 62 + "╗")
    print("║" + " " * 20 + "SHOR'S ALGORITHM" + " " * 26 + "║")
    print("║" + " " * 15 + "Project 11: Breaking RSA" + " " * 23 + "║")
    print("╚" + "═" * 62 + "╝")

    # Part 1: Mathematical Foundations
    print("\n" + "▓" * 64)
    print("▓" + " " * 20 + "PART 1: MATHEMATICS" + " " * 23 + "▓")
    print("▓" * 64)

    factoring_to_order_finding_proof()
    order_finding_with_qft_proof()
    continued_fraction_theory()
    complexity_analysis()
    cryptographic_implications()

    # Part 2: Demonstrations
    print("\n" + "▓" * 64)
    print("▓" + " " * 18 + "PART 2: DEMONSTRATIONS" + " " * 22 + "▓")
    print("▓" * 64)

    demonstrate_small_examples()

    # Part 3: Visualizations
    visualize_phase_distribution()

    print("\n" + "═" * 64)
    print("🎉 SHOR'S ALGORITHM COMPLETE!")
    print("═" * 64)
    print("""
KEY TAKEAWAYS:
1. Factoring reduces to order-finding with probability ≥ 1/2
2. Quantum phase estimation extracts the period
3. Continued fractions recover exact period from approximate measurement
4. Complexity: O((log N)³) quantum vs O(exp(n^(1/3))) classical
5. Breaks RSA, Diffie-Hellman, and ECC

CRYPTOGRAPHIC IMPACT:
- RSA, DH, ECC will be broken by large quantum computers
- Post-quantum cryptography standards (Kyber, Dilithium) are the solution
- "Harvest now, decrypt later" is a current threat

REFERENCES:
1. Shor, P. (1994): "Algorithms for quantum computation"
2. Nielsen & Chuang, Chapter 5.3: "Applications: order-finding and factoring"
3. NIST Post-Quantum Cryptography: https://csrc.nist.gov/projects/post-quantum-cryptography

Next: Project 12 - Quantum Bioinformatics Application
    """)


if __name__ == "__main__":
    main()
