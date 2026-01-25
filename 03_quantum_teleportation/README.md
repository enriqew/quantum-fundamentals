# Project 3: Quantum Teleportation

## Overview

Quantum teleportation is a protocol that transfers an unknown quantum state from one location to another using shared entanglement and classical communication. Despite the science-fiction name, it doesn't transport matter or enable faster-than-light communication.

## Learning Objectives

By completing this project, you will understand:
- How entanglement serves as a resource for quantum protocols
- The complete teleportation protocol and why it works
- Why teleportation doesn't violate no-cloning or enable FTL communication
- Superdense coding as the "dual" protocol
- The role of classical communication in quantum protocols

## Mathematical Foundation

### The Setup

- **Alice** has qubit 0 in an unknown state $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$
- **Alice** has qubit 1 (her half of an entangled pair)
- **Bob** has qubit 2 (his half of the entangled pair)

The shared entanglement is $|\Phi^+\rangle_{12} = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$

### Initial State

$$|\Psi_{initial}\rangle = |\psi\rangle_0 \otimes |\Phi^+\rangle_{12}$$

$$= (\alpha|0\rangle + \beta|1\rangle)_0 \otimes \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)_{12}$$

$$= \frac{1}{\sqrt{2}}(\alpha|000\rangle + \alpha|011\rangle + \beta|100\rangle + \beta|111\rangle)$$

### The Key Identity

We can rewrite the computational basis in terms of Bell states:

$$|00\rangle = \frac{1}{\sqrt{2}}(|\Phi^+\rangle + |\Phi^-\rangle)$$
$$|01\rangle = \frac{1}{\sqrt{2}}(|\Psi^+\rangle + |\Psi^-\rangle)$$
$$|10\rangle = \frac{1}{\sqrt{2}}(|\Phi^+\rangle - |\Phi^-\rangle)$$
$$|11\rangle = \frac{1}{\sqrt{2}}(|\Psi^+\rangle - |\Psi^-\rangle)$$

### State After Rewriting

Substituting and regrouping by Bell state on qubits 0 and 1:

$$|\Psi\rangle = \frac{1}{2}\Big[|\Phi^+\rangle_{01}(\alpha|0\rangle + \beta|1\rangle)_2 + |\Phi^-\rangle_{01}(\alpha|0\rangle - \beta|1\rangle)_2$$
$$+ |\Psi^+\rangle_{01}(\beta|0\rangle + \alpha|1\rangle)_2 + |\Psi^-\rangle_{01}(\beta|0\rangle - \alpha|1\rangle)_2\Big]$$

Using Pauli gates:

$$= \frac{1}{2}\Big[|\Phi^+\rangle_{01} \cdot I|\psi\rangle_2 + |\Phi^-\rangle_{01} \cdot Z|\psi\rangle_2 + |\Psi^+\rangle_{01} \cdot X|\psi\rangle_2 + |\Psi^-\rangle_{01} \cdot XZ|\psi\rangle_2\Big]$$

### The Protocol

1. **Bell Measurement**: Alice measures qubits 0 and 1 in the Bell basis
   - This is done by applying CNOT(0,1) then H(0), then measuring

2. **Classical Communication**: Alice sends her 2-bit result to Bob

3. **Correction**: Bob applies the appropriate Pauli gate:

| Measurement | Bell State | Correction |
|-------------|------------|------------|
| 00 | $\|\Phi^+\rangle$ | $I$ (do nothing) |
| 10 | $\|\Phi^-\rangle$ | $Z$ |
| 01 | $\|\Psi^+\rangle$ | $X$ |
| 11 | $\|\Psi^-\rangle$ | $XZ$ |

### Why It Works

After Alice's measurement collapses the state, Bob's qubit is in one of:
- $|\psi\rangle$, $Z|\psi\rangle$, $X|\psi\rangle$, or $XZ|\psi\rangle$

Each occurs with probability 1/4. Once Bob knows which one (via classical bits), he applies the inverse gate to recover $|\psi\rangle$.

## Circuit Diagram

```
Alice's qubit:     q0: ─────────●──H──M═══╗
(state to send)                 │         ║
                                │         ║   Classical
Alice's EPR half:  q1: ──H──●───X─────M═══╬═══╗ Communication
                        │                 ║   ║
                        │                 ║   ║
Bob's EPR half:    q2: ─X─────────────X───Z───╨── (output: |ψ⟩)
                                      │   │
                                      └───┴── (corrections based on measurements)
```

## The No-Cloning Theorem

**Theorem**: There is no unitary operation that can copy an arbitrary unknown quantum state.

**Proof**: Suppose $U|ψ\rangle|0\rangle = |ψ\rangle|ψ\rangle$ for all $|ψ\rangle$.

For states $|ψ\rangle$ and $|φ\rangle$:
$$\langle ψ|φ\rangle = \langle ψ|\langle 0|U^\dagger U|φ\rangle|0\rangle = \langle ψ|φ\rangle^2$$

This implies $\langle ψ|φ\rangle \in \{0, 1\}$ for all pairs. But we can have $0 < \langle ψ|φ\rangle < 1$.

Contradiction! ∎

**Teleportation doesn't violate no-cloning** because the original state is destroyed during Bell measurement.

## Why No Faster-Than-Light Communication?

Before receiving classical bits, Bob's qubit is in a maximally mixed state:

$$\rho_B = \text{Tr}_{01}(|\Psi\rangle\langle\Psi|) = \frac{I}{2}$$

This state carries no information about $|\psi\rangle$. Only after classical bits arrive can Bob recover the state.

Information transfer speed is limited by classical communication speed.

## Superdense Coding

The "dual" protocol to teleportation:

| Protocol | Consumes | Transmits | Achieves |
|----------|----------|-----------|----------|
| Teleportation | 1 ebit + 2 cbits | 1 qubit | 1 qubit transfer |
| Superdense | 1 ebit + 1 qubit | 1 qubit | 2 cbit transfer |

(ebit = entangled bit pair)

## Running the Code

```bash
cd 03_quantum_teleportation
python teleportation.py
```

## Exercises

1. **Verify teleportation fidelity**: Teleport 1000 random states and measure the average fidelity.

2. **Imperfect entanglement**: What happens if the shared state is not maximally entangled?

3. **Multi-qubit teleportation**: Extend the protocol to teleport a 2-qubit state.

4. **Entanglement swapping**: Use teleportation to create entanglement between particles that never interacted.

## Applications

1. **Quantum Networks**: Transfer quantum states between nodes
2. **Quantum Repeaters**: Extend quantum communication distance
3. **Quantum Error Correction**: Move logical qubits between locations
4. **Measurement-Based Quantum Computing**: Teleportation as a computational primitive

## References

1. Bennett et al. (1993): "Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels"
2. Bouwmeester et al. (1997): First experimental demonstration
3. Nielsen & Chuang, Chapter 1.3.7: "Quantum teleportation"
