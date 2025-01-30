import argparse

from jade.app.app import JadeApp


def main():
    parser = argparse.ArgumentParser(description="JADE V&V")
    parser.add_argument("--run", help="run benchmarks", action="store_true")
    parser.add_argument("--raw", help="process raw results", action="store_true")
    parser.add_argument(
        "--pp", help="perform complete post-process of the results", action="store_true"
    )
    parser.add_argument(
        "--rungui", help="open the run configuration GUI", action="store_true"
    )
    parser.add_argument(
        "--ppgui", help="open the post-process configuration GUI", action="store_true"
    )

    args = parser.parse_args()

    app = JadeApp()
    app.initialize_log()

    if args.rungui:
        app.start_run_config_gui()
    if args.ppgui:
        app.start_pp_config_gui()
    if args.run:
        app.run_benchmarks()
    if args.raw:
        app.raw_process()
    if args.pp:
        app.post_process()


if __name__ == "__main__":
    main()
