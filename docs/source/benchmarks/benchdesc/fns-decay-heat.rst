FNS decay heat: iron, five-minute irradiation
---------------------------------------------

This initial subset contains the 1996 FNS iron experiment with a 300-second
irradiation and all 20 reported cooling-time measurements, distributed through
`IAEA CoNDERC <https://www-nds.iaea.org/conderc/>`_. It is a decay-heat
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

Input and measurement hosting is pending maintainer agreement and confirmation
of redistribution terms. This draft supplies the adapter and post-processing
configuration; these data are not installed by JADE's normal input download yet.
For a local installation, the required layout is:

.. code-block:: text

   benchmark_templates/FNS-DecayHeat/
     benchmark_metadata.json
     Fe-1996-5min/actinv/spec.json
   raw_data/_exp_-_exp_/FNS-DecayHeat/
     Fe-1996-5min Decay heat.csv

The input folder contains exactly one scalar spec JSON. Metadata uses
``{"name": "FNS-DecayHeat", "version": {"actinv": "1.0.0"}}``.
The experimental CSV columns are ``time,Value,Error`` in seconds after shutdown,
microW/g and relative reported error, respectively. Benchmark case names must
not contain spaces because JADE separates case and result names with a space.

The source archive is ``https://www-nds.iaea.org/conderc/fusion/files/fns.zip``
(SHA-256 ``ba1dd6cb150a4aa3e0d81461054aec7d415ef19d946aba8b9886b31de218252d``).
The relevant members under ``fns/Fe/`` are ``1996exp_5min.exp``,
``1996exp_5min_fluxes``, ``TENDL-2017_1996exp_5min.i`` and
``total_1996exp_5min.pdf``. Obtain the source data separately under their
applicable terms. See :ref:`actinv_libraries` for data configuration and
:ref:`actinv_run` for input and execution requirements.
