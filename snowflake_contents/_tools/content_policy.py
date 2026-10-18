"""Apply user-requested exclusions to imported content only."""
import json
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit


def load_policy(root):
    return json.loads((root / 'import_policy.json').read_text())


def excluded_source(path, identity, policy):
    path = Path(path)
    if set(path.parts) & set(policy['excluded_directory_names']):
        return True
    return any(path == Path(excluded) or Path(excluded) in path.parents
               for excluded in policy['excluded_repository_paths'].get(identity, []))


def excluded_entry(entry, policy):
    parsed = urlsplit(entry['url'])
    if parsed.hostname in policy['excluded_hosts']:
        return True
    if entry['url'] in policy['excluded_catalog_urls'] or '旧教材' in entry['title']:
        return True
    parts = unquote(parsed.path).strip('/').split('/')
    if parsed.hostname == 'github.com' and len(parts) > 4:
        return excluded_source(Path(*parts[4:]), '/'.join(parts[:2]), policy)
    return bool(set(parts) & set(policy['excluded_directory_names']))


def prune_source_tree(destination, identity, policy):
    candidates = [p for p in destination.rglob('*')
                  if p.name in policy['excluded_directory_names']]
    candidates += [destination / p for p in policy['excluded_repository_paths'].get(identity, [])]
    removed = []
    for path in sorted(set(candidates), key=lambda p: (len(p.parts), str(p))):
        # Never follow a link when removing an imported subtree.
        if path.is_symlink():
            path.unlink()
        elif path.exists():
            if not path.resolve().is_relative_to(destination.resolve()):
                raise ValueError(f'Exclusion escapes source directory: {path}')
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        else:
            continue
        removed.append(path.relative_to(destination).as_posix())
    return removed
