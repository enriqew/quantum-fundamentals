"""
AWS Braket utilities for quantum computing projects.

Provides convenient wrappers for:
- Running circuits on simulators
- Extracting state vectors
- Converting results to probabilities
"""

from typing import Dict, Optional, Tuple, Union
import numpy as np

from braket.circuits import Circuit
from braket.devices import LocalSimulator


def get_local_simulator(backend: str = "braket_sv") -> LocalSimulator:
    """
    Get an AWS Braket local simulator.

    Available backends:
    - "braket_sv": State vector simulator (default)
      Best for: Small circuits, accessing full quantum state
    - "braket_dm": Density matrix simulator
      Best for: Noisy simulations, mixed states

    Args:
        backend: Simulator backend name

    Returns:
        LocalSimulator instance
    """
    return LocalSimulator(backend=backend)


def run_circuit(
    circuit: Circuit,
    shots: int = 1000,
    backend: str = "braket_sv"
) -> Dict[str, int]:
    """
    Run a quantum circuit and return measurement counts.

    Args:
        circuit: Braket Circuit object
        shots: Number of measurement shots
        backend: Simulator backend

    Returns:
        Dictionary mapping bitstrings to counts
    """
    device = get_local_simulator(backend)
    task = device.run(circuit, shots=shots)
    result = task.result()

    return dict(result.measurement_counts)


def get_state_vector(circuit: Circuit) -> np.ndarray:
    """
    Get the state vector after running a circuit (without measurement).

    Note: This only works with state vector simulator and requires
    the circuit to NOT have measurements.

    Args:
        circuit: Braket Circuit object (without measurements)

    Returns:
        Complex numpy array representing the quantum state
    """
    device = get_local_simulator("braket_sv")

    # Create a copy without measurements to get state vector
    if len(circuit.result_types) == 0:
        circuit = circuit.state_vector()

    task = device.run(circuit, shots=0)
    result = task.result()

    # Extract state vector from result
    state_vector = result.values[0]

    return np.array(state_vector)


def counts_to_probabilities(counts: Dict[str, int]) -> Dict[str, float]:
    """
    Convert measurement counts to probabilities.

    Args:
        counts: Dictionary mapping bitstrings to counts

    Returns:
        Dictionary mapping bitstrings to probabilities
    """
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}


def get_all_probabilities(
    counts: Dict[str, int],
    n_qubits: int
) -> Dict[str, float]:
    """
    Get probability for all possible bitstrings (including zero counts).

    Useful for comparing with theoretical predictions.

    Args:
        counts: Dictionary mapping bitstrings to counts
        n_qubits: Number of qubits in circuit

    Returns:
        Dictionary with all 2^n_qubits bitstrings and their probabilities
    """
    total = sum(counts.values())
    all_probs = {}

    for i in range(2 ** n_qubits):
        bitstring = format(i, f'0{n_qubits}b')
        all_probs[bitstring] = counts.get(bitstring, 0) / total

    return all_probs


def compare_with_theory(
    counts: Dict[str, int],
    theoretical_probs: Dict[str, float],
    n_qubits: int
) -> Tuple[float, Dict[str, Tuple[float, float]]]:
    """
    Compare measured results with theoretical predictions.

    Calculates the total variation distance and per-state comparison.

    Args:
        counts: Measurement counts
        theoretical_probs: Theoretical probabilities
        n_qubits: Number of qubits

    Returns:
        Tuple of (total_variation_distance, per_state_comparison)
        where per_state_comparison maps bitstring to (measured, theoretical)
    """
    measured = get_all_probabilities(counts, n_qubits)

    tvd = 0.0
    comparison = {}

    for bitstring in measured.keys():
        m_prob = measured[bitstring]
        t_prob = theoretical_probs.get(bitstring, 0)
        tvd += abs(m_prob - t_prob)
        comparison[bitstring] = (m_prob, t_prob)

    return tvd / 2, comparison


def expectation_value(
    counts: Dict[str, int],
    observable_fn
) -> float:
    """
    Calculate expectation value of an observable from measurement counts.

    The observable is specified as a function that maps bitstrings to values.

    Args:
        counts: Measurement counts
        observable_fn: Function mapping bitstring to observable value

    Returns:
        Expectation value
    """
    total = sum(counts.values())
    exp_val = 0.0

    for bitstring, count in counts.items():
        exp_val += (count / total) * observable_fn(bitstring)

    return exp_val


def parity_expectation(counts: Dict[str, int]) -> float:
    """
    Calculate Z parity expectation value.

    Parity is +1 for even number of 1s, -1 for odd number of 1s.
    This corresponds to measuring ⟨Z₁⊗Z₂⊗...⊗Zₙ⟩.

    Args:
        counts: Measurement counts

    Returns:
        Parity expectation value in [-1, 1]
    """
    def parity(bitstring: str) -> float:
        return 1.0 if bitstring.count('1') % 2 == 0 else -1.0

    return expectation_value(counts, parity)


def statistical_uncertainty(
    counts: Dict[str, int],
    bitstring: str
) -> float:
    """
    Calculate statistical uncertainty in probability estimate.

    For binomial sampling: σ = √(p(1-p)/n)

    Args:
        counts: Measurement counts
        bitstring: Bitstring to calculate uncertainty for

    Returns:
        Standard deviation of probability estimate
    """
    total = sum(counts.values())
    count = counts.get(bitstring, 0)
    p = count / total

    return np.sqrt(p * (1 - p) / total)
