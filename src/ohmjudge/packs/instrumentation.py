from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def shunt_voltage(rng: Random, seed: int) -> Task:
    current_a = rng.choice([0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    resistance_mohm = rng.choice([1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    value = current_a * resistance_mohm
    return make_task(
        pack="instrumentation",
        template="shunt_voltage",
        seed=seed,
        question=(
            f"A current shunt has resistance {resistance_mohm:g} milliohm and "
            f"carries {current_a:g} A. What voltage appears across it in mV?"
        ),
        value=value,
        unit="mV",
        difficulty="introductory",
        parameters={"current_a": current_a, "resistance_mohm": resistance_mohm},
    )


def linear_sensor_temperature(rng: Random, seed: int) -> Task:
    offset_mv = rng.choice([0.0, 100.0, 400.0, 500.0, 750.0])
    sensitivity_mv_per_c = rng.choice([5.0, 10.0, 12.5, 20.0])
    temperature_c = rng.choice([-20.0, 0.0, 25.0, 40.0, 75.0, 100.0])
    measured_mv = offset_mv + sensitivity_mv_per_c * temperature_c
    return make_task(
        pack="instrumentation",
        template="linear_sensor_temperature",
        seed=seed,
        question=(
            "A linear temperature sensor follows "
            f"Vout(mV) = {offset_mv:g} + {sensitivity_mv_per_c:g} T(°C). "
            f"Its measured output is {measured_mv:g} mV. What temperature does "
            "this model imply in degC?"
        ),
        value=temperature_c,
        unit="degC",
        difficulty="introductory",
        parameters={
            "offset_mv": offset_mv,
            "sensitivity_mv_per_c": sensitivity_mv_per_c,
            "measured_mv": measured_mv,
        },
    )


def rss_voltage_uncertainty(rng: Random, seed: int) -> Task:
    components_mv = [
        rng.choice([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0])
        for _ in range(rng.choice([3, 4, 5]))
    ]
    value = math.sqrt(sum(component * component for component in components_mv))
    rendered = ", ".join(f"{component:g}" for component in components_mv)
    return make_task(
        pack="instrumentation",
        template="rss_voltage_uncertainty",
        seed=seed,
        question=(
            f"Independent standard voltage uncertainties are {rendered} mV. "
            "Combine them by root-sum-square. What is the combined standard "
            "uncertainty in mV?"
        ),
        value=value,
        unit="mV",
        difficulty="intermediate",
        parameters={"components_mv": components_mv},
    )


def voltage_gain_db(rng: Random, seed: int) -> Task:
    input_mv = rng.choice([1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    gain = rng.choice([0.25, 0.5, 2.0, 5.0, 10.0, 20.0, 100.0])
    output_mv = input_mv * gain
    value = 20.0 * math.log10(output_mv / input_mv)
    return make_task(
        pack="instrumentation",
        template="voltage_gain_db",
        seed=seed,
        question=(
            f"A voltage amplifier produces {output_mv:g} mV from "
            f"{input_mv:g} mV. Using Av(dB) = 20 log10(|Vout/Vin|), what is "
            "the voltage gain in dB?"
        ),
        value=value,
        unit="dB",
        difficulty="introductory",
        parameters={"input_mv": input_mv, "output_mv": output_mv},
    )


def wheatstone_bridge_output(rng: Random, seed: int) -> Task:
    supply_v = rng.choice([2.5, 3.3, 5.0, 10.0])
    nominal = rng.choice([100.0, 120.0, 350.0, 1000.0])
    fractional_change = rng.choice([-0.05, -0.02, -0.01, 0.01, 0.02, 0.05])
    r1 = nominal
    r2 = nominal
    r3 = nominal
    r4 = nominal * (1.0 + fractional_change)
    value = supply_v * (r4 / (r3 + r4) - r2 / (r1 + r2)) * 1e3
    return make_task(
        pack="instrumentation",
        template="wheatstone_bridge_output",
        seed=seed,
        question=(
            f"A Wheatstone bridge is excited by {supply_v:g} V from top to "
            f"bottom. The left branch is R1={r1:g} ohm over R2={r2:g} ohm; "
            f"the right branch is R3={r3:g} ohm over R4={r4:g} ohm. Define "
            "Vout = Vright - Vleft and use "
            "Vout = Vs[R4/(R3+R4)-R2/(R1+R2)]. What is Vout in mV?"
        ),
        value=value,
        unit="mV",
        difficulty="intermediate",
        parameters={
            "supply_v": supply_v,
            "r1_ohm": r1,
            "r2_ohm": r2,
            "r3_ohm": r3,
            "r4_ohm": r4,
            "fractional_change": fractional_change,
        },
    )


GENERATORS = (
    shunt_voltage,
    linear_sensor_temperature,
    rss_voltage_uncertainty,
    voltage_gain_db,
    wheatstone_bridge_output,
)
