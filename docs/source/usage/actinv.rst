ACTINV inventory calculations
=============================

The initial ACTINV adapter supports local, deterministic neutron activation of
one material per ``actinv-spec-1`` JSON input. Install the ACTINV CLI separately.
It runs ``actinv run <input>.json <output>.json`` as a subprocess. No ACTINV
Python dependency is required.

In ``cfg/libs_cfg.yml``, each library name selects an explicit activation and
decay combination. Paths should be absolute; relative paths resolve from the
directory where JADE starts. The activation NPZ requires its companion
``<stem>_index.json`` with schema ``actinv-library-index-2``, neutron projectile
and ``fispact-709`` groups.

.. code-block:: yaml

   TENDL2025-patched-ENDF8-JEFF33:
     actinv:
       path: /data/activation/tendl-2025-patched-neutron-709g.npz
       decay_primary: /data/decay/endf-b-viii-0_decay.dat
       decay_fallback: /data/decay/jeff-3-3_decay.dat

Library names label JADE's tables and plots, so name the data actually used:
the example activation file is ACTINV's patched derivative of TENDL-2025, not
an official TENDL release. ``decay_fallback`` is optional. The selected configuration replaces all template
library and decay references, including catalog references. A missing file is an
error. There is no automatic choice of a different file or retention of a
template fallback when none is configured.

Use these settings in ``cfg/env_vars_cfg.yml``:

.. code-block:: yaml

   mpi_tasks: 0
   openmp_threads: 1
   executables:
     actinv: /path/to/actinv
   run_mode: local
   code_job_template: {}
   exe_prefix: null

MPI, executable prefixes and scheduler modes are rejected by this first adapter.
These settings apply to the whole JADE session and are checked before any
benchmark starts when ACTINV will execute; JADE's default configuration sets
``exe_prefix: srun``. With ``only_input: true``, input generation needs no ACTINV
executable and does not impose these execution settings. ``continue`` executes
previously generated inputs and checks the settings even if ``only_input`` is
still true.
JADE's ``openmp_threads`` setting does not configure ACTINV. Each scalar process
has a 180-second timeout. Successful runs require valid finite output at every
requested schedule endpoint before JADE writes ``actinv.complete``. A failed,
timed-out or interrupted attempt removes any old completion marker. ``continue``
restarts an incomplete scalar case from its persisted input; it does not resume
an internal solver checkpoint. Changing the selected data requires regenerating
the input.

Select the benchmark and library in ``cfg/run_cfg.yml``:

.. code-block:: yaml

   FNS-DecayHeat:
     codes:
       actinv: [TENDL2025-patched-ENDF8-JEFF33]
     description: FNS iron five-minute irradiation
     nps: 1
     only_input: false
     custom_input: null

``nps`` is an unused compatibility field. ACTINV is deterministic, so increasing
it does not improve the solution. The input must supply an inline 709-group
spectrum and a positive-duration schedule. Mesh inputs, non-neutron projectiles,
uncertainty sampling and other optional response calculations are outside this
initial adapter.

The output reader exposes total heat as tally 1 in W/g and total activity as
tally 2 in Bq/g, with elapsed time in seconds. ``Error=0`` means no Monte Carlo
sampling error is supplied; it does not mean zero uncertainty in nuclear data,
the irradiation history or the model. The FNS benchmark separately retains
reported experimental errors.

For comparisons, list the experiment and the ACTINV library in
``cfg/pp_cfg.yml``. JADE always uses ``_exp_-_exp_`` as the reference, so the
ratio is calculated/measured:

.. code-block:: yaml

   benchmarks: [FNS-DecayHeat]
   code_libs: [_exp_-_exp_, _actinv_-_TENDL2025-patched-ENDF8-JEFF33_]

See :ref:`fnsdecayheat` for the initial case, data layout and availability.
