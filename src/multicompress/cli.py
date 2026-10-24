from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .engines.bzip2_engine import BZip2Engine
from .engines.lzma_engine import LZMAEngine
from .engines.sevenzip_engine import SevenZipEngine
from .exceptions import ArchiveError, CompressionError, DecompressionError, MissingDependencyError
from .statistics import OperationStats, format_stat_line


def _print_stats(stats: OperationStats, *, verbose: bool = False) -> None:
    print(format_stat_line(stats))
    if verbose:
        print(f"  gain_bytes={stats.gain_bytes}")


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source", help="source file or directory")
    parser.add_argument("--output", help="destination file or directory")
    parser.add_argument("--force", action="store_true", help="allow overwrite")
    parser.add_argument("--keep", action="store_true", help="keep the original source after a successful operation")
    parser.add_argument("--verbose", action="store_true", help="show extra diagnostics")


def _bzip2_compress(args: argparse.Namespace) -> int:
    engine = BZip2Engine()
    source = Path(args.source)
    output = Path(args.output) if args.output else None
    try:
        result = engine.compress_file(source, output, level=getattr(args, "level", 9))
        stats = OperationStats(
            source_name=str(source),
            output_name=str(result),
            source_size=source.stat().st_size,
            output_size=result.stat().st_size,
            elapsed_seconds=0.0,
            operation="compress",
        )
        _print_stats(stats, verbose=args.verbose)
        if not args.keep:
            source.unlink(missing_ok=True)
        return 0
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _bzip2_decompress(args: argparse.Namespace) -> int:
    engine = BZip2Engine()
    source = Path(args.source)
    output = Path(args.output) if args.output else None
    try:
        result = engine.decompress_file(source, output)
        print(f"Decompressed to {result}")
        if not args.keep:
            source.unlink(missing_ok=True)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _bzip2_test(args: argparse.Namespace) -> int:
    engine = BZip2Engine()
    try:
        valid = engine.test_file(args.source)
        print("valid" if valid else "invalid")
        return 0 if valid else 3
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


def _lzma_compress(args: argparse.Namespace) -> int:
    engine = LZMAEngine()
    output = Path(args.output) if args.output else None
    try:
        result = engine.compress_file(args.source, output, format_name=getattr(args, "format", "lzma"), preset=getattr(args, "preset", 6))
        print(f"Compressed to {result}")
        if not args.keep:
            Path(args.source).unlink(missing_ok=True)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _lzma_decompress(args: argparse.Namespace) -> int:
    engine = LZMAEngine()
    output = Path(args.output) if args.output else None
    try:
        result = engine.decompress_file(args.source, output)
        print(f"Decompressed to {result}")
        if not args.keep:
            Path(args.source).unlink(missing_ok=True)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _lzma_test(args: argparse.Namespace) -> int:
    engine = LZMAEngine()
    try:
        valid = engine.test_file(args.source)
        print("valid" if valid else "invalid")
        return 0 if valid else 3
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


def _sevenzip_create(args: argparse.Namespace) -> int:
    try:
        engine = SevenZipEngine()
        result = engine.create_archive(args.source, args.output, method=args.method)
        print(f"Archive created: {result}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _sevenzip_extract(args: argparse.Namespace) -> int:
    try:
        engine = SevenZipEngine()
        result = engine.extract_archive(args.source, args.output or ".")
        print(f"Extracted to {result}")
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _sevenzip_list(args: argparse.Namespace) -> int:
    try:
        engine = SevenZipEngine()
        print(engine.list_archive(args.source))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _sevenzip_test(args: argparse.Namespace) -> int:
    try:
        engine = SevenZipEngine()
        print("valid" if engine.test_archive(args.source) else "invalid")
        return 0 if engine.test_archive(args.source) else 3
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="multicompress", description="Compression and archive utilities for BZip2, LZMA and 7z files.")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="tool", required=True)

    bzip2_parser = subparsers.add_parser("bzip2", help="BZip2 utilities")
    bzip2_sub = bzip2_parser.add_subparsers(dest="action", required=True)

    compress_bz = bzip2_sub.add_parser("compress", help="Compress a file using BZip2")
    _add_common_options(compress_bz)
    compress_bz.add_argument("--level", type=int, default=9, help="BZip2 compression level (1-9)")
    compress_bz.set_defaults(func=_bzip2_compress)

    decompress_bz = bzip2_sub.add_parser("decompress", help="Decompress a BZip2 archive")
    _add_common_options(decompress_bz)
    decompress_bz.set_defaults(func=_bzip2_decompress)

    test_bz = bzip2_sub.add_parser("test", help="Validate a BZip2 archive")
    test_bz.add_argument("source", help="compressed file to test")
    test_bz.set_defaults(func=_bzip2_test)

    lzma_parser = subparsers.add_parser("lzma", help="LZMA utilities")
    lzma_sub = lzma_parser.add_subparsers(dest="action", required=True)

    compress_lz = lzma_sub.add_parser("compress", help="Compress a file using LZMA or XZ")
    _add_common_options(compress_lz)
    compress_lz.add_argument("--format", choices=["lzma", "xz", "lzma2"], default="lzma")
    compress_lz.add_argument("--preset", type=int, default=6)
    compress_lz.set_defaults(func=_lzma_compress)

    decompress_lz = lzma_sub.add_parser("decompress", help="Decompress an LZMA file")
    _add_common_options(decompress_lz)
    decompress_lz.set_defaults(func=_lzma_decompress)

    test_lz = lzma_sub.add_parser("test", help="Validate an LZMA stream")
    test_lz.add_argument("source", help="LZMA / XZ file to validate")
    test_lz.set_defaults(func=_lzma_test)

    seven_parser = subparsers.add_parser("7z", help="7-Zip utilities")
    seven_sub = seven_parser.add_subparsers(dest="action", required=True)

    create_7z = seven_sub.add_parser("create", help="Create a 7z archive")
    create_7z.add_argument("source", help="source file or directory")
    create_7z.add_argument("output", help="archive path to create")
    create_7z.add_argument("--method", default="LZMA2", choices=["LZMA", "LZMA2"], help="compression method")
    create_7z.set_defaults(func=_sevenzip_create)

    extract_7z = seven_sub.add_parser("extract", help="Extract a 7z archive")
    extract_7z.add_argument("source", help="archive file to extract")
    extract_7z.add_argument("--output", default=".", help="destination directory")
    extract_7z.set_defaults(func=_sevenzip_extract)

    list_7z = seven_sub.add_parser("list", help="List a 7z archive")
    list_7z.add_argument("source", help="archive to inspect")
    list_7z.set_defaults(func=_sevenzip_list)

    test_7z = seven_sub.add_parser("test", help="Test the integrity of a 7z archive")
    test_7z.add_argument("source", help="archive to verify")
    test_7z.set_defaults(func=_sevenzip_test)

    return parser
