from pathlib import Path


def latest_report(folder: Path) -> Path:
    return max(folder.glob('*.txt'), key=lambda path: path.name)
