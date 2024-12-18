import argparse

from jade.app.app import JadeApp


def main():
    parser = argparse.ArgumentParser(description="JADE utilities", action="store_true")
    parser.add_argument("-f", "--fetch", help="Fetch the benchmark inputs", action="store_true")
    parser.add_argument("-r", "--restore", help="Restore default configurations", action="store_true")
    parser.add_argument("--runtpe", help="Remove MCNP runtpe files from sim folders", action="store_true")

    args = parser.parse_args()

    app = JadeApp()

    if args.fetch:
        app.update_inputs()
    if args.restore:
        app.restore_default_cfg()
    if args.runtpe:
        app.rmv_runtpe()


if __name__ == "__main__":
    main()
