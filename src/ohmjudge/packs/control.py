from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def first_order_time_constant(rng: Random, seed: int) -> Task:
    pole = rng.choice([0.2, 0.5, 0.8, 1.0, 1.25, 2.0, 4.0, 5.0])
    value = 1.0 / pole
    return make_task(
        pack="control",
        template="first_order_time_constant",
        seed=seed,
        question=(
            f"A stable first-order continuous-time system has its only pole at "
            f"s = -{pole:g} rad/s. What is its time constant in seconds?"
        ),
        value=value,
        unit="s",
        difficulty="introductory",
        parameters={"pole_rad_s": -pole},
    )


def percent_overshoot(rng: Random, seed: int) -> Task:
    damping = rng.choice([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    value = 100.0 * math.exp(
        -damping * math.pi / math.sqrt(1.0 - damping * damping)
    )
    return make_task(
        pack="control",
        template="percent_overshoot",
        seed=seed,
        question=(
            "For a standard underdamped second-order system with damping ratio "
            f"ζ = {damping:g}, use Mp = 100 exp(-ζπ/sqrt(1-ζ²)). "
            "What is the percent overshoot in %?"
        ),
        value=value,
        unit="%",
        difficulty="intermediate",
        parameters={"damping_ratio": damping},
    )


def settling_time(rng: Random, seed: int) -> Task:
    damping = rng.choice([0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    natural_frequency = rng.choice([2.0, 3.0, 4.0, 5.0, 8.0, 10.0])
    value = 4.0 / (damping * natural_frequency)
    return make_task(
        pack="control",
        template="settling_time",
        seed=seed,
        question=(
            "Using the common 2% approximation Ts = 4/(ζωn), find the settling "
            f"time for ζ = {damping:g} and ωn = {natural_frequency:g} rad/s. "
            "Report seconds."
        ),
        value=value,
        unit="s",
        difficulty="intermediate",
        parameters={
            "damping_ratio": damping,
            "natural_frequency_rad_s": natural_frequency,
        },
    )


def discrete_pole_radius(rng: Random, seed: int) -> Task:
    poles = [
        complex(rng.choice([-0.9, -0.6, -0.3, 0.2, 0.5, 0.8]), 0.0),
        complex(
            rng.choice([-0.8, -0.5, 0.3, 0.6, 0.9]),
            rng.choice([0.1, 0.2, 0.4]),
        ),
    ]
    value = max(abs(pole) for pole in poles)
    rendered = ", ".join(
        f"{pole.real:g}{pole.imag:+g}j" if pole.imag else f"{pole.real:g}"
        for pole in poles
    )
    return make_task(
        pack="control",
        template="discrete_pole_radius",
        seed=seed,
        question=(
            f"A discrete-time LTI system has poles at {rendered}. What is the "
            "largest pole magnitude? Report a unitless number."
        ),
        value=value,
        unit="unitless",
        difficulty="intermediate",
        parameters={
            "poles": [
                {"real": pole.real, "imaginary": pole.imag} for pole in poles
            ]
        },
    )


def dc_gain(rng: Random, seed: int) -> Task:
    numerator = rng.choice([1.0, 2.0, 4.0, 5.0, 8.0, 10.0])
    constant = rng.choice([1.0, 2.0, 4.0, 5.0, 8.0, 10.0, 20.0])
    damping_term = rng.choice([1.0, 2.0, 3.0, 4.0, 6.0])
    value = numerator / constant
    return make_task(
        pack="control",
        template="dc_gain",
        seed=seed,
        question=(
            f"A continuous-time transfer function is G(s) = {numerator:g} / "
            f"(s^2 + {damping_term:g}s + {constant:g}). What is the DC gain "
            "G(0)? Report a unitless number."
        ),
        value=value,
        unit="unitless",
        difficulty="introductory",
        parameters={
            "numerator": numerator,
            "s_coefficient": damping_term,
            "constant": constant,
        },
    )


GENERATORS = (
    first_order_time_constant,
    percent_overshoot,
    settling_time,
    discrete_pole_radius,
    dc_gain,
)
