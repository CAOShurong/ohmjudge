from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def voltage_divider(rng: Random, seed: int) -> Task:
    vin = rng.choice([3.3, 5.0, 9.0, 12.0, 15.0])
    r_top = rng.choice([1.0, 2.2, 3.3, 4.7, 6.8, 10.0, 22.0])
    r_bottom = rng.choice([1.0, 2.2, 3.3, 4.7, 6.8, 10.0, 22.0])
    value = vin * r_bottom / (r_top + r_bottom)
    return make_task(
        pack="circuits",
        template="voltage_divider",
        seed=seed,
        question=(
            f"An unloaded voltage divider has {r_top:g} kohm from a "
            f"{vin:g} V ideal source to the output node and {r_bottom:g} kohm "
            "from the output node to ground. What is the output voltage in V?"
        ),
        value=value,
        unit="V",
        difficulty="introductory",
        parameters={"vin_v": vin, "r_top_kohm": r_top, "r_bottom_kohm": r_bottom},
    )


def rc_cutoff(rng: Random, seed: int) -> Task:
    resistance_kohm = rng.choice([1.0, 2.2, 4.7, 10.0, 22.0, 47.0])
    capacitance_nf = rng.choice([1.0, 2.2, 4.7, 10.0, 22.0, 47.0, 100.0])
    value = 1.0 / (
        2.0 * math.pi * resistance_kohm * 1e3 * capacitance_nf * 1e-9
    )
    return make_task(
        pack="circuits",
        template="rc_cutoff",
        seed=seed,
        question=(
            "A first-order RC low-pass filter uses "
            f"R = {resistance_kohm:g} kohm and C = {capacitance_nf:g} nF. "
            "What is its -3 dB cutoff frequency in Hz?"
        ),
        value=value,
        unit="Hz",
        difficulty="introductory",
        parameters={
            "resistance_kohm": resistance_kohm,
            "capacitance_nf": capacitance_nf,
        },
    )


def inverting_amplifier(rng: Random, seed: int) -> Task:
    r_in = rng.choice([1.0, 2.0, 5.0, 10.0])
    gain_magnitude = rng.choice([2.0, 3.0, 4.0, 5.0, 8.0])
    r_feedback = r_in * gain_magnitude
    vin = rng.choice([-1.2, -0.8, -0.5, 0.4, 0.7, 1.0])
    rail = rng.choice([3.3, 5.0, 9.0, 12.0])
    ideal = -gain_magnitude * vin
    value = max(-rail, min(rail, ideal))
    return make_task(
        pack="circuits",
        template="inverting_amplifier",
        seed=seed,
        question=(
            "An ideal inverting op-amp has "
            f"Rin = {r_in:g} kohm, Rf = {r_feedback:g} kohm, "
            f"Vin = {vin:g} V, and symmetric output limits of ±{rail:g} V. "
            "Assume the non-inverting input is grounded. What output voltage "
            "does the limited ideal model produce, in V?"
        ),
        value=value,
        unit="V",
        difficulty="intermediate",
        parameters={
            "r_in_kohm": r_in,
            "r_feedback_kohm": r_feedback,
            "vin_v": vin,
            "rail_v": rail,
        },
    )


def thevenin_resistance(rng: Random, seed: int) -> Task:
    r_top = rng.choice([1.0, 2.2, 3.3, 4.7, 6.8, 10.0, 22.0])
    r_bottom = rng.choice([1.0, 2.2, 3.3, 4.7, 6.8, 10.0, 22.0])
    value = r_top * r_bottom / (r_top + r_bottom)
    return make_task(
        pack="circuits",
        template="thevenin_resistance",
        seed=seed,
        question=(
            "A divider is made from "
            f"{r_top:g} kohm connected to an ideal voltage source and "
            f"{r_bottom:g} kohm connected to ground. Looking into the midpoint "
            "with the ideal voltage source set to zero, what is the Thevenin "
            "resistance in kohm?"
        ),
        value=value,
        unit="kohm",
        difficulty="introductory",
        parameters={"r_top_kohm": r_top, "r_bottom_kohm": r_bottom},
    )


def series_current(rng: Random, seed: int) -> Task:
    voltage = rng.choice([3.3, 5.0, 9.0, 12.0, 24.0])
    resistors = [
        rng.choice([100.0, 220.0, 330.0, 470.0, 680.0, 1000.0])
        for _ in range(rng.choice([2, 3, 4]))
    ]
    value = voltage / sum(resistors) * 1e3
    resistor_text = ", ".join(f"{value:g}" for value in resistors)
    return make_task(
        pack="circuits",
        template="series_current",
        seed=seed,
        question=(
            f"An ideal {voltage:g} V source drives series resistors of "
            f"{resistor_text} ohm. What is the loop current in mA?"
        ),
        value=value,
        unit="mA",
        difficulty="introductory",
        parameters={"voltage_v": voltage, "resistors_ohm": resistors},
    )


GENERATORS = (
    voltage_divider,
    rc_cutoff,
    inverting_amplifier,
    thevenin_resistance,
    series_current,
)
