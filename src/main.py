thonimport argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is on sys.path so we can import top-level modules like "models"
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# These imports work because the script directory (src) is on sys.path
from extractors.wallet_analyzer import WalletAnalyzer  # type: ignore
from outputs.result_formatter import write_results  # type: ignore
from models.wallet_stats import WalletStats  # type: ignore

def configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

def load_json(path: Path, description: str) -> Any:
    logger = logging.getLogger("main.load_json")
    logger.debug("Loading %s from %s", description, path)
    if not path.exists():
        raise FileNotFoundError(f"{description} file not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def resolve_default_paths() -> Dict[str, Path]:
    """
    Resolve default paths relative to the project root.
    """
    return {
        "config": ROOT_DIR / "src" / "config" / "settings.example.json",
        "wallets": ROOT_DIR / "data" / "wallets.sample.json",
        "output": ROOT_DIR / "data" / "sample_output.json",
    }

def parse_args(default_paths: Dict[str, Path]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Crypto Wallet Performance Tracker - simulate wallet performance analytics."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=default_paths["config"],
        help="Path to settings JSON (default: src/config/settings.example.json)",
    )
    parser.add_argument(
        "--wallets",
        type=Path,
        default=default_paths["wallets"],
        help="Path to wallets JSON (default: data/wallets.sample.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_paths["output"],
        help="Path to write analysis output JSON (default: data/sample_output.json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase logging verbosity (-v, -vv).",
    )
    return parser.parse_args()

def main() -> None:
    default_paths = resolve_default_paths()
    args = parse_args(default_paths)
    configure_logging(args.verbose)

    logger = logging.getLogger("main")
    logger.info("Starting Crypto Wallet Performance Tracker")

    try:
        settings = load_json(args.config, "settings")
    except Exception as exc:
        logger.error("Failed to load settings: %s", exc, exc_info=args.verbose >= 2)
        sys.exit(1)

    try:
        wallets = load_json(args.wallets, "wallet list")
    except Exception as exc:
        logger.error("Failed to load wallets: %s", exc, exc_info=args.verbose >= 2)
        sys.exit(1)

    if not isinstance(wallets, list):
        logger.error("Wallets JSON must be a list of wallet objects.")
        sys.exit(1)

    analyzer = WalletAnalyzer(settings=settings)

    try:
        results: List[WalletStats] = analyzer.analyze_wallets(wallets)
    except Exception as exc:
        logger.error(
            "Unexpected error during wallet analysis: %s", exc, exc_info=args.verbose >= 2
        )
        sys.exit(1)

    try:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_results(results, output_path)
    except Exception as exc:
        logger.error("Failed to write results: %s", exc, exc_info=args.verbose >= 2)
        sys.exit(1)

    logger.info("Analysis completed successfully. Output written to %s", output_path)

if __name__ == "__main__":
    main()