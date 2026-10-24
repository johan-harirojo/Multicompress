from __future__ import annotations

import sys
from typing import Sequence

from .cli import build_parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)

    if "--gui" in arguments or "gui" in arguments:
        from .gui import main as gui_main
        return gui_main()

    parser = build_parser()
    args = parser.parse_args(arguments)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
