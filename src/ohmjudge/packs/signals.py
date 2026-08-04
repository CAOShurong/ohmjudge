from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def sine_rms(rng: Random, seed: int) -> Task:
    amplitude = rng.choice([0.5, 1.0, 1.5, 2.0, 3.3, 5.0, 10.0])
    dc = rng.choice([0.0, 0.2, 0.5, 1.0, 2.0])
    value = math.sqrt(dc * dc + amplitude * amplitude / 2.0)
    return make_task(
        pack="signals",
        template="sine_rms",
        seed=seed,
        question=(
            f"A waveform is x(t) = {dc:g} + {amplitude:g} sin(2πft) V. "
            "What is its total RMS value in V, including the DC component?"
        ),
        value=value,
        unit="V",
        difficulty="introductory",
        parameters={"dc_v": dc, "peak_amplitude_v": amplitude},
    )


def nyquist_rate(rng: Random, seed: int) -> Task:
    tones_khz = sorted(
        rng.sample([0.8, 1.0, 1.2, 1.5, 2.0, 2.4, 3.0, 3.6, 4.0, 5.0], 3)
    )
    value = 2.0 * max(tones_khz)
    return make_task(
        pack="signals",
        template="nyquist_rate",
        seed=seed,
        question=(
            "A continuous-time signal contains only sinusoidal components at "
            f"{tones_khz[0]:g}, {tones_khz[1]:g}, and {tones_khz[2]:g} kHz. "
            "Under the ordinary Nyquist criterion, what is the minimum sampling "
            "rate in kHz?"
        ),
        value=value,
        unit="kHz",
        difficulty="introductory",
        parameters={"tones_khz": tones_khz},
    )


def alias_frequency(rng: Random, seed: int) -> Task:
    sample_rate = rng.choice([8.0, 10.0, 12.0, 16.0, 20.0])
    input_frequency = rng.choice(
        [value for value in [6.0, 7.0, 9.0, 11.0, 13.0, 15.0, 18.0, 23.0]
         if value != sample_rate]
    )
    remainder = input_frequency % sample_rate
    value = min(remainder, sample_rate - remainder)
    return make_task(
        pack="signals",
        template="alias_frequency",
        seed=seed,
        question=(
            f"A real sinusoid at {input_frequency:g} kHz is sampled at "
            f"{sample_rate:g} kHz. Give the aliased frequency observed in the "
            "first Nyquist zone [0, fs/2], in kHz."
        ),
        value=value,
        unit="kHz",
        difficulty="intermediate",
        parameters={
            "sample_rate_khz": sample_rate,
            "input_frequency_khz": input_frequency,
        },
    )


def sequence_energy(rng: Random, seed: int) -> Task:
    sequence = [rng.randint(-4, 5) for _ in range(rng.choice([4, 5, 6]))]
    value = sum(item * item for item in sequence)
    return make_task(
        pack="signals",
        template="sequence_energy",
        seed=seed,
        question=(
            f"For the finite discrete-time sequence x[n] = {sequence}, compute "
            "its energy E = sum |x[n]|^2. Report a unitless number."
        ),
        value=value,
        unit="unitless",
        difficulty="introductory",
        parameters={"sequence": sequence},
        rel_tol=0.0,
        abs_tol=0.0,
    )


def convolution_length(rng: Random, seed: int) -> Task:
    first = rng.randint(3, 20)
    second = rng.randint(3, 20)
    value = first + second - 1
    return make_task(
        pack="signals",
        template="convolution_length",
        seed=seed,
        question=(
            f"Two finite sequences have lengths {first} and {second}. Assuming "
            "their first and last samples are nonzero, how many samples are in "
            "their linear convolution?"
        ),
        value=value,
        unit="samples",
        difficulty="introductory",
        parameters={"first_length": first, "second_length": second},
        rel_tol=0.0,
        abs_tol=0.0,
    )


GENERATORS = (
    sine_rms,
    nyquist_rate,
    alias_frequency,
    sequence_energy,
    convolution_length,
)
