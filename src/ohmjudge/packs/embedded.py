from __future__ import annotations

from random import Random

from ..models import Task
from ..tasking import make_task


def uart_frame_time(rng: Random, seed: int) -> Task:
    baud = rng.choice([9600, 19200, 38400, 57600, 115200, 230400, 460800])
    bytes_sent = rng.choice([1, 8, 16, 32, 64, 128, 256])
    value = bytes_sent * 10.0 / baud * 1e3
    return make_task(
        pack="embedded",
        template="uart_frame_time",
        seed=seed,
        question=(
            f"An 8N1 UART sends {bytes_sent} bytes at {baud} baud. Count one "
            "start bit, eight data bits, and one stop bit per byte, with no "
            "gaps. What is the transmission time in ms?"
        ),
        value=value,
        unit="ms",
        difficulty="introductory",
        parameters={"baud": baud, "bytes": bytes_sent, "bits_per_frame": 10},
    )


def pwm_duty_cycle(rng: Random, seed: int) -> Task:
    period_counts = rng.choice([100, 256, 500, 1000, 4096, 65536])
    compare_counts = rng.randint(1, period_counts - 1)
    value = compare_counts / period_counts * 100.0
    return make_task(
        pack="embedded",
        template="pwm_duty_cycle",
        seed=seed,
        question=(
            f"A PWM output is high for {compare_counts} timer counts in every "
            f"{period_counts} counts. Using duty = high_counts/period_counts, "
            "what is the duty cycle in %?"
        ),
        value=value,
        unit="%",
        difficulty="introductory",
        parameters={
            "compare_counts": compare_counts,
            "period_counts": period_counts,
        },
    )


def timer_update_frequency(rng: Random, seed: int) -> Task:
    timer_clock_mhz = rng.choice([8.0, 16.0, 48.0, 72.0, 80.0, 120.0, 168.0])
    prescaler = rng.choice([0, 7, 15, 71, 79, 119, 167])
    auto_reload = rng.choice([99, 999, 1999, 9999, 65535])
    value = timer_clock_mhz * 1e6 / (prescaler + 1) / (auto_reload + 1)
    return make_task(
        pack="embedded",
        template="timer_update_frequency",
        seed=seed,
        question=(
            f"A microcontroller timer clock is {timer_clock_mhz:g} MHz. Its "
            f"prescaler register is {prescaler} and auto-reload register is "
            f"{auto_reload}; both divide by register+1. What update-event "
            "frequency results in Hz?"
        ),
        value=value,
        unit="Hz",
        difficulty="intermediate",
        parameters={
            "timer_clock_mhz": timer_clock_mhz,
            "prescaler_register": prescaler,
            "auto_reload_register": auto_reload,
        },
    )


def adc_buffer_size(rng: Random, seed: int) -> Task:
    channels = rng.choice([1, 2, 4, 8, 12, 16])
    samples_per_channel = rng.choice([128, 256, 512, 1000, 2048, 4096])
    bytes_per_sample = rng.choice([1, 2, 4])
    value = channels * samples_per_channel * bytes_per_sample / 1024.0
    return make_task(
        pack="embedded",
        template="adc_buffer_size",
        seed=seed,
        question=(
            f"An acquisition buffer stores {samples_per_channel} samples for "
            f"each of {channels} channels using {bytes_per_sample} bytes per "
            "sample. What buffer capacity is required in KiB, where 1 KiB is "
            "1024 bytes?"
        ),
        value=value,
        unit="KiB",
        difficulty="introductory",
        parameters={
            "channels": channels,
            "samples_per_channel": samples_per_channel,
            "bytes_per_sample": bytes_per_sample,
        },
    )


def i2c_transfer_time(rng: Random, seed: int) -> Task:
    clock_khz = rng.choice([100.0, 400.0, 1000.0, 3400.0])
    payload_bytes = rng.choice([1, 2, 4, 8, 16, 32, 64])
    clock_pulses = 9 * (payload_bytes + 1)
    value = clock_pulses / (clock_khz * 1e3) * 1e6
    return make_task(
        pack="embedded",
        template="i2c_transfer_time",
        seed=seed,
        question=(
            f"An I2C write sends one address byte and {payload_bytes} payload "
            f"bytes at {clock_khz:g} kHz. Count 9 clock pulses for every byte "
            "(eight data bits plus ACK), and ignore start/stop duration and "
            "clock stretching. What is the transfer time in us?"
        ),
        value=value,
        unit="us",
        difficulty="intermediate",
        parameters={
            "clock_khz": clock_khz,
            "payload_bytes": payload_bytes,
            "clock_pulses": clock_pulses,
        },
    )


GENERATORS = (
    uart_frame_time,
    pwm_duty_cycle,
    timer_update_frequency,
    adc_buffer_size,
    i2c_transfer_time,
)
