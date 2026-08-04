from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def three_phase_real_power(rng: Random, seed: int) -> Task:
    line_voltage_v = rng.choice([208.0, 380.0, 400.0, 415.0, 480.0])
    line_current_a = rng.choice([5.0, 10.0, 16.0, 25.0, 40.0, 63.0])
    power_factor = rng.choice([0.70, 0.80, 0.85, 0.90, 0.95, 1.0])
    value = math.sqrt(3.0) * line_voltage_v * line_current_a * power_factor / 1e3
    return make_task(
        pack="power",
        template="three_phase_real_power",
        seed=seed,
        question=(
            f"A balanced three-phase load draws {line_current_a:g} A from a "
            f"{line_voltage_v:g} V line-to-line supply at power factor "
            f"{power_factor:g}. Using P = sqrt(3) V_L I_L PF, what is the "
            "total real power in kW?"
        ),
        value=value,
        unit="kW",
        difficulty="intermediate",
        parameters={
            "line_voltage_v": line_voltage_v,
            "line_current_a": line_current_a,
            "power_factor": power_factor,
        },
    )


def ideal_transformer_voltage(rng: Random, seed: int) -> Task:
    primary_v = rng.choice([24.0, 48.0, 120.0, 230.0, 400.0])
    primary_turns = rng.choice([100, 200, 400, 500, 800])
    secondary_turns = rng.choice([20, 50, 80, 100, 160, 250])
    value = primary_v * secondary_turns / primary_turns
    return make_task(
        pack="power",
        template="ideal_transformer_voltage",
        seed=seed,
        question=(
            f"An ideal transformer has {primary_turns} primary turns, "
            f"{secondary_turns} secondary turns, and {primary_v:g} V RMS on "
            "the primary. What is the secondary RMS voltage in V?"
        ),
        value=value,
        unit="V",
        difficulty="introductory",
        parameters={
            "primary_v": primary_v,
            "primary_turns": primary_turns,
            "secondary_turns": secondary_turns,
        },
    )


def capacitor_energy(rng: Random, seed: int) -> Task:
    capacitance_uf = rng.choice([10.0, 22.0, 47.0, 100.0, 220.0, 470.0, 1000.0])
    voltage_v = rng.choice([3.3, 5.0, 12.0, 24.0, 48.0])
    value = 0.5 * capacitance_uf * 1e-6 * voltage_v * voltage_v * 1e3
    return make_task(
        pack="power",
        template="capacitor_energy",
        seed=seed,
        question=(
            f"An ideal {capacitance_uf:g} uF capacitor is charged to "
            f"{voltage_v:g} V. Using E = 0.5 C V^2, how much energy is stored "
            "in mJ?"
        ),
        value=value,
        unit="mJ",
        difficulty="introductory",
        parameters={"capacitance_uf": capacitance_uf, "voltage_v": voltage_v},
    )


def power_factor_correction(rng: Random, seed: int) -> Task:
    real_power_kw = rng.choice([1.0, 2.0, 5.0, 7.5, 10.0, 15.0])
    voltage_v = rng.choice([120.0, 230.0, 240.0])
    frequency_hz = rng.choice([50.0, 60.0])
    initial_pf, target_pf = rng.choice(
        [(0.65, 0.90), (0.70, 0.95), (0.75, 0.90), (0.80, 0.95)]
    )
    reactive_var = (
        real_power_kw
        * 1e3
        * (math.tan(math.acos(initial_pf)) - math.tan(math.acos(target_pf)))
    )
    value = reactive_var / (2.0 * math.pi * frequency_hz * voltage_v * voltage_v) * 1e6
    return make_task(
        pack="power",
        template="power_factor_correction",
        seed=seed,
        question=(
            f"A single-phase {real_power_kw:g} kW load at {voltage_v:g} V RMS "
            f"and {frequency_hz:g} Hz improves from PF {initial_pf:g} to "
            f"{target_pf:g}. Use Qc = P[tan(acos(PF1))-tan(acos(PF2))] and "
            "C = Qc/(2πfV^2). What shunt capacitance is required in uF?"
        ),
        value=value,
        unit="uF",
        difficulty="advanced",
        parameters={
            "real_power_kw": real_power_kw,
            "voltage_v": voltage_v,
            "frequency_hz": frequency_hz,
            "initial_pf": initial_pf,
            "target_pf": target_pf,
        },
    )


def battery_runtime(rng: Random, seed: int) -> Task:
    capacity_ah = rng.choice([1.5, 2.0, 3.0, 5.0, 10.0, 20.0])
    nominal_v = rng.choice([3.7, 7.4, 12.0, 24.0, 48.0])
    efficiency = rng.choice([0.70, 0.80, 0.85, 0.90, 0.95])
    load_w = rng.choice([2.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    value = capacity_ah * nominal_v * efficiency / load_w
    return make_task(
        pack="power",
        template="battery_runtime",
        seed=seed,
        question=(
            f"Use the ideal energy approximation for a {capacity_ah:g} Ah, "
            f"{nominal_v:g} V battery feeding a constant {load_w:g} W load "
            f"through a converter of efficiency {efficiency:g}. Ignoring rate, "
            "temperature, and cutoff effects, what runtime is predicted in hours?"
        ),
        value=value,
        unit="hours",
        difficulty="introductory",
        parameters={
            "capacity_ah": capacity_ah,
            "nominal_v": nominal_v,
            "efficiency": efficiency,
            "load_w": load_w,
        },
    )


GENERATORS = (
    three_phase_real_power,
    ideal_transformer_voltage,
    capacitor_energy,
    power_factor_correction,
    battery_runtime,
)
