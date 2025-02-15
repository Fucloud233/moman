import argparse
# import sys

from pathlib import Path

from handler import MomanCmdHandler


def test(args):
    print(args)


def main():
    parser = argparse.ArgumentParser()

    sub_parsers = parser.add_subparsers()

    parser_modular = sub_parsers.add_parser("modular")
    parser_modular.set_defaults(func=test)

    MomanCmdHandler.modular(Path("/Users/fucloud/Code/moman-demo"))

    # args = parser.parse_args(sys.argv[1:])
    # args.func(args)


if __name__ == "__main__":
    main()
