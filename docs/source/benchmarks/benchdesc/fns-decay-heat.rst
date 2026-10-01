FNS decay heat: iron, five-minute irradiation
---------------------------------------------

This initial subset contains the 1996 FNS iron experiment with a 300-second
irradiation and all 20 reported cooling-time measurements, distributed through
`IAEA CoNDERC <https://www-nds.iaea.org/conderc/>`_ in the
`FNS source archive <https://www-nds.iaea.org/conderc/fusion/files/fns.zip>`_. It is a decay-heat
experiment, distinct from the FNS time-of-flight benchmark. The supplied
709-group neutron spectrum and irradiation history are used directly; no
transport calculation is needed.

The source deck specifies elemental iron and a total flux of
1.116 x 10^10 neutrons/cm^2/s. The calculation uses heat per gram. Experimental
times are converted from minutes to seconds using the published decimal values,
and each measurement is a schedule endpoint. No interpolation is used. The raw
configuration removes the irradiation endpoint, subtracts the 300-second
shutdown time and converts W/g to microW/g. This shutdown setting applies only
to the initial five-minute case; raw processing fails for a case whose output
has no endpoint at 300 seconds, instead of shifting its cooling times. Other
irradiation histories need their own setting. Cooling-time labels are rounded
to nine decimal places to remove floating-point subtraction noise before JADE
matches table indices; no heat values are interpolated or rounded.

The comparison is calculated/measured decay heat. Experimental ``Error`` is the
reported absolute error divided by measured heat. Its published magnitude is
retained without assuming a confidence level or covariance. With ACTINV's zero
sampling-error field, JADE propagates that relative experimental error to C/E.
The table and plot do not represent total predictive uncertainty.

JADE-ready inputs and measurements are supplied through
`IAEA Open Benchmarks <https://github.com/IAEA-NDS/open-benchmarks/tree/main/jade_open_benchmarks>`_.
JADE's standard IAEA input download installs the benchmark templates and
experimental results.

Activation and decay libraries are installed separately. See
:ref:`actinv_libraries` for data configuration and :ref:`actinv_run` for input
and execution requirements.
