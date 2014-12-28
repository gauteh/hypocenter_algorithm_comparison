# hypocenter algorithm comparison

for:

- HYPOSAT
- TauP
- HYPOCENTER ( not implemented )

## requirements

- numpy and scipy
- HYPOSAT
- HYPOMOD     (forward modelling for HYPOSAT)
- HYPOCENTER  (as provided by SEISAN)
- TTLAYER     (as provided by SEISAN) (forward modelling for HYPOCENTER)
- TauP

## usage

See test setup in tests/h_t_comp and run: `./hypomod_taup_comparison.py`. This
tests TauP vs HYPOMOD (HYPOSAT forward modeling) for a small array setup.


