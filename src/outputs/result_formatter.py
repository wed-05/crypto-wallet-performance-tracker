thonimport json
import logging
from pathlib import Path
from typing import Iterable, List

from models.wallet_stats import WalletStats

logger = logging.getLogger(__name__)

def serialize_wallet_stats(stats_iter: Iterable[WalletStats]) -> List[dict]:
    return [s.to_dict() for s in stats_iter]

def write_results(stats_iter: Iterable[WalletStats], output_path: Path) -> None:
    data = serialize_wallet_stats(stats_iter)
    logger.info("Writing %d wallet records to %s", len(data), output_path)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, sort_keys=False)
    logger.debug("Results written successfully.")