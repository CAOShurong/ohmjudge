from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UnitSpec:
    canonical: str
    dimension: str
    factor: float


def _key(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("Ω", "ohm")
        .replace("ω", "ohm")
        .replace("μ", "u")
        .replace("µ", "u")
        .replace(" ", "")
        .replace("_", "")
    )


_UNITS: dict[str, UnitSpec] = {}


def _register(
    canonical: str, dimension: str, factor: float, *aliases: str
) -> None:
    spec = UnitSpec(canonical, dimension, factor)
    for alias in {canonical, *aliases}:
        _UNITS[_key(alias)] = spec


_register("V", "voltage", 1.0, "volt", "volts")
_register("mV", "voltage", 1e-3, "millivolt", "millivolts")
_register("A", "current", 1.0, "amp", "amps", "ampere", "amperes")
_register("mA", "current", 1e-3, "milliamp", "milliamps")
_register("uA", "current", 1e-6, "microamp", "microamps")
_register("ohm", "resistance", 1.0, "ohms")
_register("kohm", "resistance", 1e3, "kiloohm", "kiloohms", "kΩ")
_register("Mohm", "resistance", 1e6, "megaohm", "megaohms", "MΩ")
_register("Hz", "frequency", 1.0, "hertz")
_register("kHz", "frequency", 1e3, "kilohertz")
_register("MHz", "frequency", 1e6, "megahertz")
_register("GHz", "frequency", 1e9, "gigahertz")
_register("rad/s", "angular_frequency", 1.0, "rads", "radsec")
_register("s", "time", 1.0, "sec", "second", "seconds")
_register("ms", "time", 1e-3, "millisecond", "milliseconds")
_register("us", "time", 1e-6, "microsecond", "microseconds")
_register("W", "power", 1.0, "watt", "watts")
_register("mW", "power", 1e-3, "milliwatt", "milliwatts")
_register("dB", "decibel", 1.0, "decibels")
_register("dBm", "dbm", 1.0)
_register("bit/s", "data_rate", 1.0, "bps", "bits/s", "bitspersecond")
_register("kbit/s", "data_rate", 1e3, "kbps")
_register("Mbit/s", "data_rate", 1e6, "Mbps", "megabits/s")
_register("Gbit/s", "data_rate", 1e9, "Gbps")
_register("symbol/s", "symbol_rate", 1.0, "baud", "symbols/s")
_register("ksymbol/s", "symbol_rate", 1e3, "kbaud")
_register("Msymbol/s", "symbol_rate", 1e6, "Mbaud")
_register("%", "percent", 1.0, "percent", "percentage")
_register("samples", "count", 1.0, "sample")
_register("unitless", "unitless", 1.0, "", "1", "none", "dimensionless")


def lookup_unit(value: str | None) -> UnitSpec | None:
    if value is None:
        return None
    return _UNITS.get(_key(value))


def convert_value(value: float, from_unit: str, to_unit: str) -> float | None:
    source = lookup_unit(from_unit)
    target = lookup_unit(to_unit)
    if source is None or target is None or source.dimension != target.dimension:
        return None
    return value * source.factor / target.factor


_NUMBER = re.compile(
    r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",
    re.ASCII,
)


def finite_number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        match = _NUMBER.fullmatch(value.strip().replace(",", ""))
        if match:
            number = float(match.group(0))
            return number if math.isfinite(number) else None
    return None
