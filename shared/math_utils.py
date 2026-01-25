"""
Mathematical utilities for quantum computing projects.

Provides functions for:
- Bloch sphere coordinate conversion
- Quantum state fidelity and distance measures
- Number theory (for Shor's algorithm)
- Continued fraction expansion
"""

from typing import List, Tuple, Optional, Union
import numpy as np
from fractions import Fraction
import math


def state_to_bloch(state: np.ndarray) -> Tuple[float, float, float]:
    """
    Convert a single-qubit state vector to Bloch sphere coordinates.

    For state |ψ⟩ = α|0⟩ + β|1⟩, we can write it as:
    |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ}sin(θ/2)|1⟩

    The Bloch vector is (sin(θ)cos(φ), sin(θ)sin(φ), cos(θ)).

    Args:
        state: 2-element complex numpy array [α, β]

    Returns:
        Tuple (x, y, z) on Bloch sphere
    """
    if len(state) != 2:
        raise ValueError("State must be a 2-element array for single qubit")

    alpha, beta = state

    # Normalize
    norm = np.sqrt(np.abs(alpha)**2 + np.abs(beta)**2)
    alpha, beta = alpha / norm, beta / norm

    # Remove global phase (make alpha real and positive)
    if np.abs(alpha) > 1e-10:
        phase = np.exp(-1j * np.angle(alpha))
        alpha = alpha * phase
        beta = beta * phase

    # Calculate theta and phi
    # cos(theta/2) = |alpha|, sin(theta/2) = |beta|
    theta = 2 * np.arccos(np.clip(np.abs(alpha), 0, 1))

    if np.abs(beta) > 1e-10:
        phi = np.angle(beta)
    else:
        phi = 0

    # Bloch coordinates
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return float(x), float(y), float(z)


def fidelity(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Calculate the fidelity between two pure quantum states.

    Fidelity F(|ψ⟩, |φ⟩) = |⟨ψ|φ⟩|²

    For pure states, fidelity = 1 means identical states,
    fidelity = 0 means orthogonal states.

    Args:
        state1: First state vector
        state2: Second state vector

    Returns:
        Fidelity value between 0 and 1
    """
    # Normalize states
    state1 = state1 / np.linalg.norm(state1)
    state2 = state2 / np.linalg.norm(state2)

    # Calculate |⟨ψ|φ⟩|²
    overlap = np.abs(np.vdot(state1, state2)) ** 2

    return float(overlap)


def trace_distance(state1: np.ndarray, state2: np.ndarray) -> float:
    """
    Calculate the trace distance between two pure quantum states.

    For pure states: D(|ψ⟩, |φ⟩) = √(1 - |⟨ψ|φ⟩|²)

    Trace distance is a metric: D = 0 for identical states,
    D = 1 for orthogonal states.

    Args:
        state1: First state vector
        state2: Second state vector

    Returns:
        Trace distance between 0 and 1
    """
    f = fidelity(state1, state2)
    return float(np.sqrt(1 - f))


def continued_fraction(
    x: float,
    max_terms: int = 20,
    tolerance: float = 1e-10
) -> List[int]:
    """
    Compute the continued fraction expansion of a real number.

    Any real number x can be written as:
    x = a₀ + 1/(a₁ + 1/(a₂ + 1/(a₃ + ...)))

    This is denoted [a₀; a₁, a₂, a₃, ...]

    This is crucial for Shor's algorithm to extract the period
    from the measured phase.

    Args:
        x: Real number to expand
        max_terms: Maximum number of terms
        tolerance: Stop when remainder is smaller than this

    Returns:
        List of continued fraction coefficients [a₀, a₁, a₂, ...]
    """
    coefficients = []
    remainder = x

    for _ in range(max_terms):
        integer_part = int(np.floor(remainder))
        coefficients.append(integer_part)

        fractional_part = remainder - integer_part

        if fractional_part < tolerance:
            break

        remainder = 1.0 / fractional_part

    return coefficients


def convergents(cf_coefficients: List[int]) -> List[Tuple[int, int]]:
    """
    Compute convergents from continued fraction coefficients.

    The k-th convergent p_k/q_k is computed using:
    p_k = a_k * p_{k-1} + p_{k-2}
    q_k = a_k * q_{k-1} + q_{k-2}

    With initial conditions: p_{-1} = 1, p_{-2} = 0
                            q_{-1} = 0, q_{-2} = 1

    Args:
        cf_coefficients: List of continued fraction coefficients

    Returns:
        List of (numerator, denominator) tuples for each convergent
    """
    if not cf_coefficients:
        return []

    # Initial values
    p_prev2, p_prev1 = 0, 1  # p_{-2}, p_{-1}
    q_prev2, q_prev1 = 1, 0  # q_{-2}, q_{-1}

    result = []

    for a in cf_coefficients:
        p = a * p_prev1 + p_prev2
        q = a * q_prev1 + q_prev2

        result.append((p, q))

        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q

    return result


def gcd(a: int, b: int) -> int:
    """
    Compute greatest common divisor using Euclidean algorithm.

    The GCD satisfies: gcd(a, b) = gcd(b, a mod b)
    with base case gcd(a, 0) = a.

    Time complexity: O(log(min(a, b)))

    Args:
        a: First integer
        b: Second integer

    Returns:
        Greatest common divisor
    """
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """
    Compute least common multiple.

    LCM(a, b) = |a * b| / GCD(a, b)

    Args:
        a: First integer
        b: Second integer

    Returns:
        Least common multiple
    """
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def mod_inverse(a: int, m: int) -> Optional[int]:
    """
    Compute modular multiplicative inverse using extended Euclidean algorithm.

    Find x such that (a * x) mod m = 1.
    Exists only if gcd(a, m) = 1.

    Uses the extended Euclidean algorithm:
    gcd(a, m) = a*x + m*y

    If gcd(a, m) = 1, then x is the modular inverse.

    Args:
        a: Number to invert
        m: Modulus

    Returns:
        Modular inverse if it exists, None otherwise
    """
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """Returns (gcd, x, y) such that a*x + b*y = gcd"""
        if a == 0:
            return b, 0, 1
        gcd_val, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd_val, x, y

    gcd_val, x, _ = extended_gcd(a % m, m)

    if gcd_val != 1:
        return None  # Inverse doesn't exist

    return (x % m + m) % m


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """
    Compute (base^exponent) mod modulus using fast exponentiation.

    Uses the square-and-multiply algorithm:
    - If exponent is even: base^exp = (base^(exp/2))^2
    - If exponent is odd: base^exp = base * base^(exp-1)

    Time complexity: O(log(exponent))

    Args:
        base: Base integer
        exponent: Exponent (non-negative)
        modulus: Modulus

    Returns:
        (base^exponent) mod modulus
    """
    result = 1
    base = base % modulus

    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus

    return result


def is_prime(n: int) -> bool:
    """
    Check if a number is prime using trial division.

    For production use, consider Miller-Rabin primality test.

    Args:
        n: Number to test

    Returns:
        True if prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    for i in range(3, int(np.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False

    return True


def classical_order_finding(a: int, N: int) -> int:
    """
    Find the multiplicative order of a modulo N classically.

    The order r is the smallest positive integer such that a^r ≡ 1 (mod N).

    This is the problem that Shor's algorithm solves exponentially faster
    on a quantum computer.

    Time complexity: O(N) in the worst case

    Args:
        a: Base (must be coprime to N)
        N: Modulus

    Returns:
        The order r, or -1 if gcd(a, N) != 1
    """
    if gcd(a, N) != 1:
        return -1  # Order undefined if not coprime

    r = 1
    current = a % N

    while current != 1:
        current = (current * a) % N
        r += 1

        if r > N:  # Safety check
            return -1

    return r


def factor_from_order(a: int, r: int, N: int) -> Optional[Tuple[int, int]]:
    """
    Attempt to find factors of N given the order r of a mod N.

    If r is even and a^(r/2) ≢ -1 (mod N), then:
    - gcd(a^(r/2) - 1, N) and gcd(a^(r/2) + 1, N)
    are likely to be non-trivial factors of N.

    This is the classical post-processing step in Shor's algorithm.

    Args:
        a: Base used for order finding
        r: Order of a mod N
        N: Number to factor

    Returns:
        Tuple of (factor1, factor2) if successful, None otherwise
    """
    if r % 2 != 0:
        return None  # Need even order

    x = mod_pow(a, r // 2, N)

    if x == N - 1:  # x ≡ -1 (mod N)
        return None

    factor1 = gcd(x - 1, N)
    factor2 = gcd(x + 1, N)

    if factor1 not in [1, N] and factor2 not in [1, N]:
        return (factor1, factor2)
    elif factor1 not in [1, N]:
        return (factor1, N // factor1)
    elif factor2 not in [1, N]:
        return (factor2, N // factor2)

    return None


def prime_factors(n: int) -> List[int]:
    """
    Find all prime factors of n.

    Args:
        n: Number to factorize

    Returns:
        List of prime factors (with repetition)
    """
    factors = []
    d = 2

    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1

    if n > 1:
        factors.append(n)

    return factors


def is_perfect_power(n: int) -> Optional[Tuple[int, int]]:
    """
    Check if n = a^b for some integers a, b with b > 1.

    This is a pre-processing step for Shor's algorithm.
    If N is a perfect power, we can factor it classically.

    Args:
        n: Number to check

    Returns:
        Tuple (a, b) if n = a^b, None otherwise
    """
    if n <= 1:
        return None

    for b in range(2, int(np.log2(n)) + 1):
        a = round(n ** (1/b))

        # Check nearby integers due to floating point errors
        for candidate in [a - 1, a, a + 1]:
            if candidate > 1 and candidate ** b == n:
                return (candidate, b)

    return None
