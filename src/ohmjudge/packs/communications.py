from __future__ import annotations

import math
from random import Random

from ..models import Task
from ..tasking import make_task


def shannon_capacity(rng: Random, seed: int) -> Task:
    bandwidth_mhz = rng.choice([1.0, 2.0, 5.0, 10.0, 20.0, 40.0])
    snr_db = rng.choice([-3.0, 0.0, 3.0, 6.0, 10.0, 15.0, 20.0])
    snr_linear = 10.0 ** (snr_db / 10.0)
    value = bandwidth_mhz * math.log2(1.0 + snr_linear)
    return make_task(
        pack="communications",
        template="shannon_capacity",
        seed=seed,
        question=(
            "An AWGN channel has bandwidth "
            f"{bandwidth_mhz:g} MHz and received SNR {snr_db:g} dB. Using "
            "C = B log2(1 + SNRlinear), what is its Shannon capacity in Mbit/s?"
        ),
        value=value,
        unit="Mbit/s",
        difficulty="intermediate",
        parameters={"bandwidth_mhz": bandwidth_mhz, "snr_db": snr_db},
    )


def free_space_path_loss(rng: Random, seed: int) -> Task:
    distance_km = rng.choice([0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    frequency_mhz = rng.choice([433.0, 868.0, 915.0, 1800.0, 2400.0, 5800.0])
    value = 32.44 + 20.0 * math.log10(distance_km) + 20.0 * math.log10(frequency_mhz)
    return make_task(
        pack="communications",
        template="free_space_path_loss",
        seed=seed,
        question=(
            "Use FSPL(dB) = 32.44 + 20 log10(d_km) + 20 log10(f_MHz). "
            f"For d = {distance_km:g} km and f = {frequency_mhz:g} MHz, "
            "what is the free-space path loss in dB?"
        ),
        value=value,
        unit="dB",
        difficulty="intermediate",
        parameters={"distance_km": distance_km, "frequency_mhz": frequency_mhz},
    )


def thermal_noise(rng: Random, seed: int) -> Task:
    bandwidth_hz = rng.choice([1e3, 10e3, 100e3, 1e6, 5e6, 10e6, 20e6])
    noise_figure_db = rng.choice([0.0, 1.0, 2.0, 3.0, 5.0, 8.0])
    value = -174.0 + 10.0 * math.log10(bandwidth_hz) + noise_figure_db
    return make_task(
        pack="communications",
        template="thermal_noise",
        seed=seed,
        question=(
            "At 290 K, use integrated receiver noise "
            "N(dBm) = -174 + 10 log10(B_Hz) + NF. "
            f"For B = {bandwidth_hz:g} Hz and noise figure {noise_figure_db:g} dB, "
            "what is N in dBm?"
        ),
        value=value,
        unit="dBm",
        difficulty="intermediate",
        parameters={
            "bandwidth_hz": bandwidth_hz,
            "noise_figure_db": noise_figure_db,
        },
    )


def qpsk_symbol_rate(rng: Random, seed: int) -> Task:
    bit_rate_mbps = rng.choice([1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    code_rate = rng.choice([0.5, 2.0 / 3.0, 0.75, 5.0 / 6.0, 1.0])
    value = bit_rate_mbps / (2.0 * code_rate)
    return make_task(
        pack="communications",
        template="qpsk_symbol_rate",
        seed=seed,
        question=(
            f"A QPSK link must carry {bit_rate_mbps:g} Mbit/s of user data. "
            f"The forward-error-correction code rate is {code_rate:.6g}. "
            "Ignoring all other overhead, what symbol rate is required in "
            "Msymbol/s?"
        ),
        value=value,
        unit="Msymbol/s",
        difficulty="intermediate",
        parameters={"user_rate_mbps": bit_rate_mbps, "code_rate": code_rate},
    )


def link_budget(rng: Random, seed: int) -> Task:
    transmit_dbm = rng.choice([0.0, 10.0, 20.0, 30.0])
    tx_gain = rng.choice([0.0, 2.0, 5.0, 8.0, 12.0])
    rx_gain = rng.choice([0.0, 2.0, 5.0, 8.0, 12.0])
    path_loss = rng.choice([60.0, 70.0, 80.0, 90.0, 100.0, 110.0])
    misc_loss = rng.choice([0.0, 1.0, 2.0, 3.0, 5.0])
    value = transmit_dbm + tx_gain + rx_gain - path_loss - misc_loss
    return make_task(
        pack="communications",
        template="link_budget",
        seed=seed,
        question=(
            f"A radio transmits {transmit_dbm:g} dBm. Transmit antenna gain is "
            f"{tx_gain:g} dBi, receive antenna gain is {rx_gain:g} dBi, path "
            f"loss is {path_loss:g} dB, and other losses total {misc_loss:g} dB. "
            "What received power does the scalar link budget predict in dBm?"
        ),
        value=value,
        unit="dBm",
        difficulty="introductory",
        parameters={
            "transmit_dbm": transmit_dbm,
            "tx_gain_dbi": tx_gain,
            "rx_gain_dbi": rx_gain,
            "path_loss_db": path_loss,
            "misc_loss_db": misc_loss,
        },
    )


GENERATORS = (
    shannon_capacity,
    free_space_path_loss,
    thermal_noise,
    qpsk_symbol_rate,
    link_budget,
)
