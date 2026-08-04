from __future__ import annotations

from random import Random

from ..models import Task
from ..tasking import make_task


def diode_resistor_current(rng: Random, seed: int) -> Task:
    source_v = rng.choice([3.3, 5.0, 9.0, 12.0])
    diode_v = rng.choice([0.60, 0.65, 0.70, 0.75])
    resistance_ohm = rng.choice([220.0, 330.0, 470.0, 680.0, 1000.0, 2200.0])
    value = (source_v - diode_v) / resistance_ohm * 1e3
    return make_task(
        pack="electronics",
        template="diode_resistor_current",
        seed=seed,
        question=(
            f"A {source_v:g} V ideal source drives a diode and "
            f"{resistance_ohm:g} ohm resistor in series. Use a constant diode "
            f"drop of {diode_v:g} V. What current flows in mA?"
        ),
        value=value,
        unit="mA",
        difficulty="introductory",
        parameters={
            "source_v": source_v,
            "diode_drop_v": diode_v,
            "resistance_ohm": resistance_ohm,
        },
    )


def bjt_base_resistor(rng: Random, seed: int) -> Task:
    drive_v = rng.choice([3.3, 5.0, 9.0, 12.0])
    collector_current_ma = rng.choice([10.0, 20.0, 40.0, 60.0, 100.0])
    forced_beta = rng.choice([10.0, 15.0, 20.0])
    vbe = 0.7
    base_current_a = collector_current_ma * 1e-3 / forced_beta
    value = (drive_v - vbe) / base_current_a / 1e3
    return make_task(
        pack="electronics",
        template="bjt_base_resistor",
        seed=seed,
        question=(
            f"An NPN low-side switch is driven from {drive_v:g} V. Use "
            f"VBE = {vbe:g} V and a forced beta of {forced_beta:g} for a "
            f"{collector_current_ma:g} mA collector current. What base "
            "resistor gives that base current, in kohm?"
        ),
        value=value,
        unit="kohm",
        difficulty="intermediate",
        parameters={
            "drive_v": drive_v,
            "vbe_v": vbe,
            "collector_current_ma": collector_current_ma,
            "forced_beta": forced_beta,
        },
    )


def mosfet_conduction_loss(rng: Random, seed: int) -> Task:
    current_a = rng.choice([1.0, 2.0, 3.0, 5.0, 8.0, 12.0])
    rds_mohm = rng.choice([5.0, 8.0, 12.0, 20.0, 35.0, 50.0])
    duty = rng.choice([0.25, 0.4, 0.5, 0.7, 0.85, 1.0])
    value = current_a * current_a * rds_mohm * 1e-3 * duty
    return make_task(
        pack="electronics",
        template="mosfet_conduction_loss",
        seed=seed,
        question=(
            f"A MOSFET carries {current_a:g} A while on, has "
            f"RDS(on) = {rds_mohm:g} milliohm, and conducts for a duty ratio "
            f"of {duty:g}. Ignoring switching loss and temperature rise, what "
            "is its average conduction loss in W?"
        ),
        value=value,
        unit="W",
        difficulty="intermediate",
        parameters={
            "current_a": current_a,
            "rds_mohm": rds_mohm,
            "duty_ratio": duty,
        },
    )


def adc_lsb_size(rng: Random, seed: int) -> Task:
    reference_v = rng.choice([1.8, 2.5, 3.0, 3.3, 4.096, 5.0])
    bits = rng.choice([8, 10, 12, 14, 16])
    value = reference_v / (2**bits) * 1e3
    return make_task(
        pack="electronics",
        template="adc_lsb_size",
        seed=seed,
        question=(
            f"An ideal {bits}-bit unipolar ADC spans 0 to {reference_v:g} V. "
            "Define one LSB as Vref/2^N. What is one LSB in mV?"
        ),
        value=value,
        unit="mV",
        difficulty="introductory",
        parameters={"reference_v": reference_v, "bits": bits},
    )


def opamp_slew_time(rng: Random, seed: int) -> Task:
    step_v = rng.choice([1.0, 2.0, 3.3, 5.0, 8.0, 10.0])
    slew_rate = rng.choice([0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    value = step_v / slew_rate
    return make_task(
        pack="electronics",
        template="opamp_slew_time",
        seed=seed,
        question=(
            f"An op-amp output must change by {step_v:g} V and is limited by "
            f"a constant slew rate of {slew_rate:g} V/us. Ignoring settling "
            "and bandwidth limits, what minimum transition time is required "
            "in us?"
        ),
        value=value,
        unit="us",
        difficulty="introductory",
        parameters={"step_v": step_v, "slew_rate_v_per_us": slew_rate},
    )


GENERATORS = (
    diode_resistor_current,
    bjt_base_resistor,
    mosfet_conduction_loss,
    adc_lsb_size,
    opamp_slew_time,
)
