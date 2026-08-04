from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task

_C = 299_792_458.0
_MU_0 = 4.0 * math.pi * 1e-7
_EPSILON_0 = 8.854_187_812_8e-12


def free_space_wavelength(rng: Random, seed: int) -> Task:
    frequency_mhz = rng.choice([100.0, 433.0, 868.0, 915.0, 1800.0, 2400.0, 5800.0])
    value = _C / (frequency_mhz * 1e6)
    return make_task(
        pack="electromagnetics",
        template="free_space_wavelength",
        seed=seed,
        question=(
            f"Using c = 299792458 m/s, what is the free-space wavelength of a "
            f"{frequency_mhz:g} MHz wave in m?"
        ),
        value=value,
        unit="m",
        difficulty="introductory",
        parameters={"frequency_mhz": frequency_mhz},
    )


def plane_wave_magnetic_field(rng: Random, seed: int) -> Task:
    electric_v_per_m = rng.choice([0.1, 0.5, 1.0, 3.0, 10.0, 30.0, 100.0])
    impedance_ohm = 376.730313668
    value = electric_v_per_m / impedance_ohm * 1e3
    return make_task(
        pack="electromagnetics",
        template="plane_wave_magnetic_field",
        seed=seed,
        question=(
            f"A uniform plane wave in free space has |E| = "
            f"{electric_v_per_m:g} V/m. Using |E|/|H| = 376.730313668 ohm, "
            "what is |H| in mA/m?"
        ),
        value=value,
        unit="mA/m",
        difficulty="intermediate",
        parameters={
            "electric_field_v_per_m": electric_v_per_m,
            "free_space_impedance_ohm": impedance_ohm,
        },
    )


def straight_wire_flux_density(rng: Random, seed: int) -> Task:
    current_a = rng.choice([0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    radius_cm = rng.choice([0.5, 1.0, 2.0, 5.0, 10.0])
    value = _MU_0 * current_a / (2.0 * math.pi * radius_cm * 1e-2) * 1e6
    return make_task(
        pack="electromagnetics",
        template="straight_wire_flux_density",
        seed=seed,
        question=(
            f"An infinitely long straight wire carries {current_a:g} A. Using "
            f"B = μ0 I/(2πr), what magnetic flux density occurs {radius_cm:g} "
            "cm from the wire, in uT?"
        ),
        value=value,
        unit="uT",
        difficulty="intermediate",
        parameters={"current_a": current_a, "radius_cm": radius_cm},
    )


def parallel_plate_capacitance(rng: Random, seed: int) -> Task:
    area_cm2 = rng.choice([1.0, 2.0, 5.0, 10.0, 20.0, 50.0])
    separation_mm = rng.choice([0.1, 0.2, 0.5, 1.0, 2.0])
    relative_permittivity = rng.choice([1.0, 2.1, 3.2, 4.0, 4.5])
    value = (
        relative_permittivity
        * _EPSILON_0
        * area_cm2
        * 1e-4
        / (separation_mm * 1e-3)
        * 1e12
    )
    return make_task(
        pack="electromagnetics",
        template="parallel_plate_capacitance",
        seed=seed,
        question=(
            f"An ideal parallel-plate capacitor has plate area {area_cm2:g} "
            f"cm^2, separation {separation_mm:g} mm, and dielectric relative "
            f"permittivity {relative_permittivity:g}. Neglect fringing and use "
            "epsilon0 = 8.8541878128e-12 F/m. What is C in pF?"
        ),
        value=value,
        unit="pF",
        difficulty="intermediate",
        parameters={
            "area_cm2": area_cm2,
            "separation_mm": separation_mm,
            "relative_permittivity": relative_permittivity,
        },
    )


def air_core_solenoid_inductance(rng: Random, seed: int) -> Task:
    turns = rng.choice([50, 100, 150, 200, 300, 500])
    area_cm2 = rng.choice([0.5, 1.0, 2.0, 5.0, 10.0])
    length_cm = rng.choice([2.0, 5.0, 8.0, 10.0, 20.0])
    value = _MU_0 * turns * turns * area_cm2 * 1e-4 / (length_cm * 1e-2) * 1e3
    return make_task(
        pack="electromagnetics",
        template="air_core_solenoid_inductance",
        seed=seed,
        question=(
            f"Use the long-solenoid approximation L = μ0 N^2 A/l for an "
            f"air-core coil with {turns} turns, area {area_cm2:g} cm^2, and "
            f"length {length_cm:g} cm. What is its inductance in mH?"
        ),
        value=value,
        unit="mH",
        difficulty="intermediate",
        parameters={"turns": turns, "area_cm2": area_cm2, "length_cm": length_cm},
    )


GENERATORS = (
    free_space_wavelength,
    plane_wave_magnetic_field,
    straight_wire_flux_density,
    parallel_plate_capacitance,
    air_core_solenoid_inductance,
)
