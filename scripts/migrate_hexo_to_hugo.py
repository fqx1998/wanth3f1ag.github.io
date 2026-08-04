from __future__ import annotations

import argparse
import os
import re
import stat
import shutil
import sys
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Iterable


MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\n]+)\)")
HTML_IMAGE_RE = re.compile(r"(<img\b[^>]*?\bsrc\s*=\s*)(['\"])(.*?)(\2)", re.IGNORECASE)
FENCE_RE = re.compile(r"^([`~]{3,})")
DATE_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)?)?$"
)
DATE_INPUT_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")
DEFAULT_TIMEZONE_OFFSET = "+08:00"
@dataclass
class MigrationStats:
    posts_total: int = 0
    posts_written: int = 0
    assets_copied: int = 0
    assets_reused: int = 0
    missing_assets: list[tuple[str, str]] = field(default_factory=list)
    cleaned_targets: list[Path] = field(default_factory=list)


class MigrationError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate Hexo markdown posts into Hugo page bundles, storing each article as "
            "content/posts/<post>/index.md and copying referenced images into the same "
            "bundle under image/ with flat filenames."
        )
    )
    parser.add_argument(
        "--src-posts",
        type=Path,
        default=Path(r"E:\Test\blog\source\_posts"),
        help="Hexo _posts directory",
    )
    parser.add_argument(
        "--dst-posts",
        type=Path,
        default=Path(r"E:\blog\content\posts"),
        help="Destination directory for Hugo page bundles",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing destination markdown files",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove destination page bundles and legacy flat-mode static post assets before writing",
    )
    return parser.parse_args()


def parse_front_matter(text: str) -> tuple[dict[str, object], str]:
    normalized = text.lstrip("\ufeff")
    if not normalized.startswith("---"):
        raise MigrationError("Missing YAML front matter delimiter")

    lines = normalized.splitlines()
    if not lines or lines[0].strip() != "---":
        raise MigrationError("Unsupported front matter opening delimiter")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise MigrationError("Missing front matter closing delimiter")

    front_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return parse_simple_yaml(front_lines), body


def parse_simple_yaml(lines: Iterable[str]) -> dict[str, object]:
    result: dict[str, object] = {}
    current_key: str | None = None

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if re.match(r"^\s*-\s+", line):
            if current_key is None:
                raise MigrationError(f"List item without parent key: {line}")
            value = re.sub(r"^\s*-\s+", "", line, count=1)
            current = result.setdefault(current_key, [])
            if not isinstance(current, list):
                raise MigrationError(f"Mixed scalar/list YAML for key: {current_key}")
            current.append(parse_scalar(value))
            continue

        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s*(.*))?$", line)
        if not match:
            raise MigrationError(f"Unsupported YAML line: {line}")

        key = match.group(1)
        raw_value = match.group(2)
        if raw_value in (None, ""):
            result[key] = []
            current_key = key
            continue

        result[key] = parse_scalar(raw_value)
        current_key = None

    return result


def parse_scalar(raw_value: str) -> object:
    value = raw_value.strip()
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        inner = value[1:-1]
        if value[0] == '"':
            inner = (
                inner.replace(r"\\", "\\")
                .replace(r"\"", '"')
                .replace(r"\n", "\n")
                .replace(r"\r", "\r")
                .replace(r"\t", "\t")
            )
        else:
            inner = inner.replace("''", "'")
        return inner
    return value


def convert_front_matter(hexo_front: dict[str, object], post_url: str) -> OrderedDict[str, object]:
    hugo_front: OrderedDict[str, object] = OrderedDict()

    if "title" in hexo_front:
        hugo_front["title"] = str(hexo_front["title"])
    if "date" in hexo_front:
        hugo_front["date"] = normalize_date_value(str(hexo_front["date"]))
    if "updated" in hexo_front:
        hugo_front["lastmod"] = normalize_date_value(str(hexo_front["updated"]))
    if "description" in hexo_front:
        hugo_front["description"] = str(hexo_front["description"])
    hugo_front["url"] = post_url

    for key in ("categories", "tags"):
        if key not in hexo_front:
            continue
        value = hexo_front[key]
        if isinstance(value, list):
            hugo_front[key] = [str(item) for item in value if str(item).strip()]
        elif str(value).strip():
            hugo_front[key] = [str(value)]
        else:
            hugo_front[key] = []

    published = hexo_front.get("published")
    hugo_front["draft"] = not bool(published) if isinstance(published, bool) else False

    for key, value in hexo_front.items():
        if key in {"title", "date", "updated", "description", "categories", "tags", "published"}:
            continue
        hugo_front[key] = value

    return hugo_front


def normalize_date_value(value: str) -> str:
    trimmed = value.strip()
    for input_format in DATE_INPUT_FORMATS:
        try:
            parsed = datetime.strptime(trimmed, input_format)
            return parsed.strftime(f"%Y-%m-%dT%H:%M:%S{DEFAULT_TIMEZONE_OFFSET}")
        except ValueError:
            continue
    return trimmed


def dump_front_matter(front_matter: OrderedDict[str, object]) -> str:
    lines = ["---"]
    for key, value in front_matter.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {yaml_scalar(item, key)}")
            continue
        lines.append(f"{key}: {yaml_scalar(value, key)}")
    lines.append("---")
    return "\n".join(lines)


def yaml_scalar(value: object, key: str | None = None) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return '""'
    if not isinstance(value, str):
        return f'"{escape_yaml_string(str(value))}"'
    if key in {"date", "lastmod"} and DATE_RE.match(value):
        return value
    return f'"{escape_yaml_string(value)}"'


def escape_yaml_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', r"\"")
        .replace("\n", r"\n")
        .replace("\r", r"\r")
        .replace("\t", r"\t")
    )


def split_fenced_segments(text: str) -> list[tuple[bool, str]]:
    segments: list[tuple[bool, str]] = []
    buffer: list[str] = []
    processable = True
    fence_char = ""
    fence_len = 0

    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        match = FENCE_RE.match(stripped)
        if match:
            token = match.group(1)
            token_char = token[0]
            token_len = len(token)
            if processable:
                if buffer:
                    segments.append((True, "".join(buffer)))
                    buffer = []
                processable = False
                fence_char = token_char
                fence_len = token_len
                buffer.append(line)
                continue
            if token_char == fence_char and token_len >= fence_len:
                buffer.append(line)
                segments.append((False, "".join(buffer)))
                buffer = []
                processable = True
                fence_char = ""
                fence_len = 0
                continue
        buffer.append(line)

    if buffer:
        segments.append((processable, "".join(buffer)))
    return segments


def split_target_and_suffix(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip()
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            return target[1:end], target[end + 1 :]
    parts = target.split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " " + parts[1]


def normalize_reference(reference: str) -> str:
    cleaned = reference.strip()
    cleaned = cleaned.split("#", 1)[0].split("?", 1)[0]
    return cleaned.replace("\\", "/")


def is_remote_reference(reference: str) -> bool:
    lowered = reference.lower()
    return lowered.startswith(("http://", "https://", "data:", "mailto:", "javascript:", "//"))


def safe_join(base: Path, reference: str) -> Path:
    parts = [part for part in PurePosixPath(reference).parts if part not in (".", "")]
    path = base
    for part in parts:
        path = path / part
    return path


def resolve_asset_path(post_path: Path, source_root: Path, reference: str) -> Path | None:
    normalized = normalize_reference(reference)
    if not normalized or is_remote_reference(normalized):
        return None

    candidates: list[Path] = []
    if normalized.startswith("/"):
        candidates.append(safe_join(source_root, normalized.lstrip("/")))
    else:
        candidates.append(safe_join(post_path.parent, normalized))
        if not normalized.startswith("../") and not normalized.startswith("./"):
            candidates.append(safe_join(post_path.parent / post_path.stem, normalized))

    source_root_resolved = source_root.resolve()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if not resolved.is_file():
            continue
        if not resolved.is_relative_to(source_root_resolved):
            continue
        return resolved
    return None


def posix_to_path(base: Path, relative_posix: str) -> Path:
    return base.joinpath(*PurePosixPath(relative_posix).parts)


class BundleAssetMigrator:
    def __init__(
        self,
        post_path: Path,
        source_root: Path,
        dst_bundle_dir: Path,
        overwrite: bool,
        stats: MigrationStats,
    ):
        self.post_path = post_path
        self.source_root = source_root
        self.dst_bundle_dir = dst_bundle_dir
        self.overwrite = overwrite
        self.stats = stats
        self.copied_by_source: dict[Path, str] = {}
        self.source_by_dest_rel: dict[str, Path] = {}

    def migrate_reference(self, reference: str) -> str | None:
        normalized = normalize_reference(reference)
        if not normalized or is_remote_reference(normalized):
            return None

        source_path = resolve_asset_path(self.post_path, self.source_root, normalized)
        if source_path is None:
            self.stats.missing_assets.append((self.post_path.name, reference))
            return None

        existing_rel = self.copied_by_source.get(source_path)
        if existing_rel is not None:
            self.stats.assets_reused += 1
            return existing_rel

        dest_rel = self.allocate_dest_rel(source_path, normalized)
        dest_path = posix_to_path(self.dst_bundle_dir, dest_rel)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if self.overwrite or not dest_path.exists():
            shutil.copy2(source_path, dest_path)
        self.copied_by_source[source_path] = dest_rel
        self.source_by_dest_rel[dest_rel] = source_path
        self.stats.assets_copied += 1
        return dest_rel

    def allocate_dest_rel(self, source_path: Path, normalized_reference: str) -> str:
        preferred_rel = build_preferred_asset_rel(source_path)
        occupied = self.source_by_dest_rel.get(preferred_rel)
        if occupied is None or occupied == source_path:
            return preferred_rel

        posix_path = PurePosixPath(preferred_rel)
        stem = posix_path.stem
        suffix = posix_path.suffix
        counter = 2
        while True:
            candidate = str(posix_path.parent / f"{stem}-{counter}{suffix}").replace("\\", "/")
            occupied = self.source_by_dest_rel.get(candidate)
            if occupied is None or occupied == source_path:
                return candidate
            counter += 1


def build_preferred_asset_rel(source_path: Path) -> str:
    return f"image/{source_path.name}"


def migrate_body(body: str, migrator: BundleAssetMigrator) -> str:
    output: list[str] = []
    for processable, segment in split_fenced_segments(body):
        if not processable:
            output.append(segment)
            continue
        updated = MARKDOWN_IMAGE_RE.sub(
            lambda match: replace_markdown_image(match, migrator),
            segment,
        )
        updated = HTML_IMAGE_RE.sub(
            lambda match: replace_html_image(match, migrator),
            updated,
        )
        output.append(updated)
    return "".join(output)


def replace_markdown_image(match: re.Match[str], migrator: BundleAssetMigrator) -> str:
    alt = match.group(1)
    raw_target = match.group(2)
    target, suffix = split_target_and_suffix(raw_target)
    migrated = migrator.migrate_reference(target)
    if migrated is None:
        return match.group(0)
    return f"![{alt}]({migrated}{suffix})"


def replace_html_image(match: re.Match[str], migrator: BundleAssetMigrator) -> str:
    prefix = match.group(1)
    quote = match.group(2)
    target = match.group(3)
    migrated = migrator.migrate_reference(target)
    if migrated is None:
        return match.group(0)
    return f"{prefix}{quote}{migrated}{quote}"


def write_post(
    src_post: Path,
    dst_posts_root: Path,
    source_root: Path,
    overwrite: bool,
    stats: MigrationStats,
) -> None:
    raw_text = src_post.read_text(encoding="utf-8-sig")
    hexo_front, body = parse_front_matter(raw_text)
    post_url = f"/posts/{src_post.stem}/"
    hugo_front = convert_front_matter(hexo_front, post_url)

    legacy_flat_post = dst_posts_root / f"{src_post.stem}.md"
    if legacy_flat_post.exists():
        raise MigrationError(
            f"Legacy flat post still exists: {legacy_flat_post}. Run with --clean before switching to page bundles."
        )

    bundle_dir = dst_posts_root / src_post.stem
    post_path = bundle_dir / "index.md"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    if post_path.exists() and not overwrite:
        raise MigrationError(f"Destination already exists: {post_path}")

    migrator = BundleAssetMigrator(
        post_path=src_post,
        source_root=source_root,
        dst_bundle_dir=bundle_dir,
        overwrite=overwrite,
        stats=stats,
    )
    migrated_body = migrate_body(body, migrator).rstrip() + "\n"
    output = dump_front_matter(hugo_front) + "\n\n" + migrated_body

    post_path.write_text(output, encoding="utf-8", newline="\n")
    stats.posts_written += 1


def clean_path(path: Path, stats: MigrationStats) -> None:
    if not path.exists():
        return
    if path.is_dir():
        for child in path.iterdir():
            remove_path(child)
    else:
        remove_path(path)
    stats.cleaned_targets.append(path)


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, onexc=retry_remove_readonly)
        return
    path.chmod(stat.S_IWRITE)
    path.unlink()


def retry_remove_readonly(function: object, failed_path: str, excinfo: object) -> None:
    os.chmod(failed_path, stat.S_IWRITE)
    function(failed_path)


def summarize(stats: MigrationStats, dst_posts: Path) -> str:
    lines = [
        f"Posts scanned: {stats.posts_total}",
        f"Posts written: {stats.posts_written}",
        f"Assets copied: {stats.assets_copied}",
        f"Assets reused within a post run: {stats.assets_reused}",
        f"Missing local assets: {len(stats.missing_assets)}",
        f"Page bundle destination: {dst_posts}",
    ]
    if stats.cleaned_targets:
        lines.append("Cleaned destinations:")
        for path in stats.cleaned_targets:
            lines.append(f"  - {path}")
    if stats.missing_assets:
        lines.append("Sample missing asset references:")
        for post_name, reference in stats.missing_assets[:20]:
            lines.append(f"  - {post_name}: {reference}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    src_posts = args.src_posts.resolve()
    source_root = src_posts.parent.resolve()
    dst_posts = args.dst_posts.resolve()
    legacy_static_posts = Path(r"E:\blog\static\posts").resolve()
    stats = MigrationStats()

    if not src_posts.is_dir():
        print(f"Source posts directory not found: {src_posts}", file=sys.stderr)
        return 1

    if args.clean:
        clean_path(dst_posts, stats)
        clean_path(legacy_static_posts, stats)

    dst_posts.mkdir(parents=True, exist_ok=True)

    posts = sorted(src_posts.glob("*.md"))
    stats.posts_total = len(posts)

    for post in posts:
        try:
            write_post(
                src_post=post,
                dst_posts_root=dst_posts,
                source_root=source_root,
                overwrite=args.overwrite,
                stats=stats,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] {post.name}: {exc}", file=sys.stderr)
            return 1

    print(summarize(stats, dst_posts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
