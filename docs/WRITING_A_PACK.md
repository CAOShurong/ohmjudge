# Writing a task pack

A good OhmJudge task is easy for code to verify and nontrivial for a language
model to solve reliably.

## Acceptance criteria

A new template must:

1. derive all variable values from the supplied `random.Random` instance;
2. return the same task for the same generator seed;
3. have a single unambiguous requested quantity and unit;
4. compute its expected answer independently of response parsing;
5. set tolerances that reflect numeric rounding, not desired outcomes;
6. avoid copyrighted question text and hidden external facts;
7. include at least one generation test and grading test.

## Generator shape

```python
from random import Random

from ..tasking import make_task


def example(rng: Random, seed: int):
    resistance = rng.uniform(100.0, 10_000.0)
    current = rng.uniform(0.001, 0.020)
    voltage = resistance * current
    return make_task(
        pack="example",
        template="ohms_law",
        seed=seed,
        question=(
            f"A {resistance:.6g} ohm resistor carries {current:.6g} A. "
            "What is the voltage in V?"
        ),
        value=voltage,
        unit="V",
        difficulty="introductory",
        parameters={"resistance_ohm": resistance, "current_a": current},
        rel_tol=1e-3,
        abs_tol=1e-6,
    )


GENERATORS = (example,)
```

Register the module in `src/ohmjudge/packs/__init__.py`.

## Avoid accidental ambiguity

- State whether a value is peak, peak-to-peak, RMS, magnitude, or signed.
- State log bases and impedance assumptions.
- Define one-sided versus two-sided bandwidth.
- Make units explicit for every input.
- Avoid component values that put a theoretical expression at a singularity.
- Round only for display; compute the expected answer from full-precision values.

## Tolerance policy

Use relative tolerance for scale-dependent floating-point answers and a small
absolute floor near zero. Exact integer results may use zero relative tolerance
and a sub-half-integer absolute tolerance. Do not widen a tolerance to accept a
different engineering convention; write that convention into the prompt or make
it a separate template.

## Review questions

- Could two competent engineers interpret the requested value differently?
- Can a unit-equivalent answer be normalized?
- Can the generator produce a physically impossible or degenerate case?
- Is the answer leaked by metadata in a public record?
- Does the template add a reasoning pattern rather than only new nouns?
- What real model failure would this template reveal?
