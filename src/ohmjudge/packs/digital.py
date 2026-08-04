from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def combinational_path_delay(rng: Random, seed: int) -> Task:
    delays_ns = [
        rng.choice([0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 2.5])
        for _ in range(rng.choice([3, 4, 5, 6]))
    ]
    value = sum(delays_ns)
    rendered = ", ".join(f"{delay:g}" for delay in delays_ns)
    return make_task(
        pack="digital",
        template="combinational_path_delay",
        seed=seed,
        question=(
            f"A combinational timing path contains gates with propagation "
            f"delays {rendered} ns in series. Ignoring interconnect and loading "
            "changes, what is the total path delay in ns?"
        ),
        value=value,
        unit="ns",
        difficulty="introductory",
        parameters={"delays_ns": delays_ns},
    )


def synchronous_max_clock(rng: Random, seed: int) -> Task:
    clock_to_q_ns = rng.choice([0.2, 0.4, 0.6, 0.8, 1.0])
    logic_ns = rng.choice([1.0, 2.0, 3.0, 5.0, 8.0, 12.0])
    setup_ns = rng.choice([0.2, 0.4, 0.5, 0.8, 1.0])
    skew_ns = rng.choice([0.0, 0.1, 0.2, 0.4, 0.5])
    period_ns = clock_to_q_ns + logic_ns + setup_ns + skew_ns
    value = 1000.0 / period_ns
    return make_task(
        pack="digital",
        template="synchronous_max_clock",
        seed=seed,
        question=(
            f"A register-to-register path has clock-to-Q {clock_to_q_ns:g} ns, "
            f"maximum combinational delay {logic_ns:g} ns, setup time "
            f"{setup_ns:g} ns, and an adverse skew allowance of {skew_ns:g} ns. "
            "Using Tclk >= tcq + tlogic + tsetup + tskew, what is the maximum "
            "clock frequency in MHz?"
        ),
        value=value,
        unit="MHz",
        difficulty="intermediate",
        parameters={
            "clock_to_q_ns": clock_to_q_ns,
            "logic_ns": logic_ns,
            "setup_ns": setup_ns,
            "skew_ns": skew_ns,
        },
    )


def counter_width(rng: Random, seed: int) -> Task:
    states = rng.choice([3, 5, 10, 16, 25, 60, 100, 256, 1000, 4096])
    value = math.ceil(math.log2(states))
    return make_task(
        pack="digital",
        template="counter_width",
        seed=seed,
        question=(
            f"A binary counter must represent {states} distinct states numbered "
            "from zero. What is the minimum register width in bits?"
        ),
        value=value,
        unit="bits",
        difficulty="introductory",
        parameters={"states": states},
        rel_tol=0.0,
        abs_tol=0.0,
    )


def twos_complement_value(rng: Random, seed: int) -> Task:
    width = rng.choice([8, 10, 12, 16])
    unsigned = rng.randint(2 ** (width - 1), 2**width - 1)
    digits = math.ceil(width / 4)
    value = unsigned - 2**width
    return make_task(
        pack="digital",
        template="twos_complement_value",
        seed=seed,
        question=(
            f"Interpret 0x{unsigned:0{digits}X} as a {width}-bit two's-complement "
            "integer. What is its signed decimal value? Report a unitless "
            "integer."
        ),
        value=value,
        unit="unitless",
        difficulty="introductory",
        parameters={"width_bits": width, "unsigned_value": unsigned},
        rel_tol=0.0,
        abs_tol=0.0,
    )


def hamming_distance(rng: Random, seed: int) -> Task:
    width = rng.choice([8, 12, 16, 24])
    first = rng.getrandbits(width)
    second = rng.getrandbits(width)
    first_bits = f"{first:0{width}b}"
    second_bits = f"{second:0{width}b}"
    value = (first ^ second).bit_count()
    return make_task(
        pack="digital",
        template="hamming_distance",
        seed=seed,
        question=(
            f"What is the Hamming distance between {first_bits} and "
            f"{second_bits}, in differing bits?"
        ),
        value=value,
        unit="bits",
        difficulty="introductory",
        parameters={"width_bits": width, "first": first_bits, "second": second_bits},
        rel_tol=0.0,
        abs_tol=0.0,
    )


GENERATORS = (
    combinational_path_delay,
    synchronous_max_clock,
    counter_width,
    twos_complement_value,
    hamming_distance,
)
