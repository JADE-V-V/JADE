import argparse

from jade.app.app import JadeApp


def main():
    parser = argparse.ArgumentParser(description="JADE V&V")
    parser.add_argument("--run", help="run benchmarks", action="store_true")
    parser.add_argument(
        "--raw",
        help="process raw results (optionally specify 'force')",
        nargs="?",
        const=True,
        default=False,
    )
    parser.add_argument(
        "--pp", help="perform complete post-process of the results", action="store_true"
    )
    parser.add_argument(
        "--rungui", help="open the run configuration GUI", action="store_true"
    )
    parser.add_argument(
        "--ppgui", help="open the post-process configuration GUI", action="store_true"
    )
    parser.add_argument(
        "--cnt",
        help="Continue the run for not simulated inputs",
        action="store_true",
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
        if args.raw == "force":
            force = True
        elif isinstance(args.raw, str) and args.raw != "force":
            raise ValueError("Invalid argument for --raw. Use 'force' or leave empty.")
        else:
            force = False
        app.raw_process(force=force)
    if args.pp:
        app.post_process()
    if args.cnt:
        app.continue_run()


if __name__ == "__main__":
    main()
