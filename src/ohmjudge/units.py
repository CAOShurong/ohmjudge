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
    stripped = value.strip()
    resistance_prefixes = {
        "mΩ": "milliohm",
        "mohm": "milliohm",
        "MΩ": "megaohm",
        "Mohm": "megaohm",
        "kΩ": "kohm",
    }
    stripped = resistance_prefixes.get(stripped, stripped)
    return (
        stripped.lower()
        .replace("Ω", "ohm")
        .replace("ω", "ohm")
        .replace("μ", "u")
        .replace("µ", "u")
        .replace(" ", "")
        .replace("_", "")
    )


_UNITS: dict[str, UnitSpec] = {}


def _register(canonical: str, dimension: str, factor: float, *aliases: str) -> None:
    spec = UnitSpec(canonical, dimension, factor)
    for alias in {canonical, *aliases}:
        _UNITS[_key(alias)] = spec


_register("V", "voltage", 1.0, "volt", "volts")
_register("mV", "voltage", 1e-3, "millivolt", "millivolts")
_register("A", "current", 1.0, "amp", "amps", "ampere", "amperes")
_register("mA", "current", 1e-3, "milliamp", "milliamps")
_register("uA", "current", 1e-6, "microamp", "microamps")
_register("A/m", "magnetic_field", 1.0, "amp/m", "amps/m")
_register("mA/m", "magnetic_field", 1e-3, "milliamp/m", "milliamps/m")
_register("ohm", "resistance", 1.0, "ohms")
_register("mohm", "resistance", 1e-3, "milliohm", "milliohms", "mΩ")
_register("kohm", "resistance", 1e3, "kiloohm", "kiloohms", "kΩ")
_register("Mohm", "resistance", 1e6, "megaohm", "megaohms", "MΩ")
_register("Hz", "frequency", 1.0, "hertz")
_register("kHz", "frequency", 1e3, "kilohertz")
_register("MHz", "frequency", 1e6, "megahertz")
_register("GHz", "frequency", 1e9, "gigahertz")
_register("rad/s", "angular_frequency", 1.0, "rads", "radsec")
_register("s", "time", 1.0, "sec", "second", "seconds")
_register("hour", "time", 3600.0, "hr", "hrs", "hours")
_register("ms", "time", 1e-3, "millisecond", "milliseconds")
_register("us", "time", 1e-6, "microsecond", "microseconds")
_register("ns", "time", 1e-9, "nanosecond", "nanoseconds")
_register("W", "power", 1.0, "watt", "watts")
_register("mW", "power", 1e-3, "milliwatt", "milliwatts")
_register("kW", "power", 1e3, "kilowatt", "kilowatts")
_register("J", "energy", 1.0, "joule", "joules")
_register("mJ", "energy", 1e-3, "millijoule", "millijoules")
_register("F", "capacitance", 1.0, "farad", "farads")
_register("uF", "capacitance", 1e-6, "microfarad", "microfarads")
_register("nF", "capacitance", 1e-9, "nanofarad", "nanofarads")
_register("pF", "capacitance", 1e-12, "picofarad", "picofarads")
_register("H", "inductance", 1.0, "henry", "henries")
_register("mH", "inductance", 1e-3, "millihenry", "millihenries")
_register("uH", "inductance", 1e-6, "microhenry", "microhenries")
_register("T", "magnetic_flux_density", 1.0, "tesla")
_register("uT", "magnetic_flux_density", 1e-6, "microtesla")
_register("m", "length", 1.0, "meter", "meters", "metre", "metres")
_register("cm", "length", 1e-2, "centimeter", "centimeters")
_register("mm", "length", 1e-3, "millimeter", "millimeters")
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
_register("bits", "bit_count", 1.0, "bit")
_register("KiB", "data_size", 1024.0, "kibibyte", "kibibytes")
_register("degC", "temperature", 1.0, "celsius", "°C")
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
