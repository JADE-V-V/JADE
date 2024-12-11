import argparse

from jade.app.app import JadeApp


def main():
    parser = argparse.ArgumentParser(description="JADE V&V")
    parser.add_argument("--run", help="run benchmarks")
    parser.add_argument("--raw", help="process raw results")
    parser.add_argument("--pp", help="perform complete post-process of the results")
    parser.add_argument("--gui", help="open the run configuration GUI")

    args = parser.parse_args()

    app = JadeApp()
    app.initialize_log()

    if args.gui:
        app.start_config_gui()
    if args.run:
        app.run_benchmarks()
    if args.raw:
        app.raw_process()
    if args.pp:
        raise NotImplementedError("JADE Post-processing not re-implemented yet")


if __name__ == "__main__":
    main()
