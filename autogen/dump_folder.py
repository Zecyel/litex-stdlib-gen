import os
import argparse
from typing import List, Optional


def collect_file_paths(root_directory: str) -> List[str]:
    paths: List[str] = []
    for current_dir, _subdirs, filenames in os.walk(root_directory):
        for filename in filenames:
            full_path = os.path.normpath(os.path.join(current_dir, filename))
            paths.append(full_path)
    paths.sort()
    return paths


def ensure_parent_dir_exists(file_path: str) -> None:
    parent = os.path.dirname(file_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Dump all files under a directory into a single stream. "
            "Each entry is formatted as '<path>:\ncontent\n\n'."
        )
    )
    parser.add_argument(
        "--path",
        "-p",
        dest="path",
        required=True,
        help="Directory to scan recursively",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default="-",
        help="Output file path. Use '-' (default) to write to stdout.",
    )

    args = parser.parse_args(argv)

    # Preserve how the user typed the base path for display purposes
    raw_base_for_display = args.path.rstrip("/\\") or "."

    root_directory_norm = os.path.normpath(args.path)
    if not os.path.isdir(root_directory_norm):
        parser.error(f"Path is not a directory: {args.path}")

    root_abs = os.path.abspath(root_directory_norm)

    write_to_stdout = args.output in ("-", "")
    output_abs = None if write_to_stdout else os.path.abspath(args.output)

    file_paths = collect_file_paths(root_abs)

    # If output file is inside the scanned directory, skip it to avoid self-inclusion
    if output_abs is not None:
        normalized_output_abs = os.path.normcase(output_abs)
        file_paths = [
            p for p in file_paths if os.path.normcase(os.path.abspath(p)) != normalized_output_abs
        ]

    if write_to_stdout:
        output_stream = None
    else:
        ensure_parent_dir_exists(output_abs)  # type: ignore[arg-type]

    try:
        if write_to_stdout:
            for file_path in file_paths:
                rel_path = os.path.relpath(file_path, root_abs)
                display_path = os.path.normpath(os.path.join(raw_base_for_display, rel_path))
                print(f"<{display_path}>:")
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    print(f.read(), end="")
                print("\n")
        else:
            with open(output_abs, "w", encoding="utf-8", errors="replace") as out_f:
                for file_path in file_paths:
                    rel_path = os.path.relpath(file_path, root_abs)
                    display_path = os.path.normpath(os.path.join(raw_base_for_display, rel_path))
                    out_f.write(f"<{display_path}>:\n")
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        out_f.write(f.read())
                    out_f.write("\n\n")
    except KeyboardInterrupt:
        # Allow graceful interruption
        pass


if __name__ == "__main__":
    main()

