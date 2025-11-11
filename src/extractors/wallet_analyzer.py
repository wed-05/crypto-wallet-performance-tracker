thonimport logging
from typing import Any, Dict, Iterable, List

from models.wallet_stats import DaysOption, SupportedChain, WalletStats
from . import blockchain_utils

class WalletAnalyzer:
    """
    High-level orchestration component that converts raw wallet inputs into
    structured WalletStats objects using blockchain_utils.
    """

    def __init__(self, settings: Dict[str, Any]) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = settings or {}
        self.default_days = self._parse_default_days_option()
        self.supported_chains = self._parse_supported_chains()
        self.max_wallets = int(
            self.settings.get("analysis", {}).get("max_wallets_per_run", 500)
        )

    def _parse_default_days_option(self) -> DaysOption:
        raw = (
            self.settings.get("analysis", {}).get("default_days_option")
            or self.settings.get("default_days_option")
            or "30d"
        )
        try:
            return blockchain_utils.parse_days_option(str(raw))
        except ValueError as exc:
            self.logger.warning(
                "Invalid default_days_option '%s' in settings: %s. Falling back to 30d.",
                raw,
                exc,
            )
            return DaysOption.THIRTY_D

    def _parse_supported_chains(self) -> List[SupportedChain]:
        raw_chains = self.settings.get("supported_chains") or [
            c.value for c in SupportedChain
        ]
        chains: List[SupportedChain] = []
        for raw in raw_chains:
            try:
                chains.append(blockchain_utils.normalize_chain(str(raw)))
            except ValueError as exc:
                self.logger.warning("Ignoring unsupported chain in settings: %s", exc)
        if not chains:
            chains = list(SupportedChain)
        return chains

    def _normalize_wallet_item(self, item: Any) -> Dict[str, Any]:
        """
        Normalize a wallet item from the wallets JSON.

        Supported shapes:
          - "wallet_address"
          - {"wallet": "...", "chain": "sol", "daysOption": "7d"}
        """
        if isinstance(item, str):
            return {"wallet": item, "chain": None, "daysOption": None}
        if not isinstance(item, dict):
            raise ValueError(f"Wallet item must be a string or object, got: {type(item)}")
        return {
            "wallet": item.get("wallet") or item.get("address"),
            "chain": item.get("chain"),
            "daysOption": item.get("daysOption") or item.get("days") or item.get("period"),
        }

    def analyze_wallets(self, wallet_items: Iterable[Any]) -> List[WalletStats]:
        results: List[WalletStats] = []
        count = 0

        for raw_item in wallet_items:
            if count >= self.max_wallets:
                self.logger.warning(
                    "Reached max_wallets_per_run limit (%d). Remaining wallets will be skipped.",
                    self.max_wallets,
                )
                break
            count += 1

            try:
                normalized = self._normalize_wallet_item(raw_item)
                wallet_addr = normalized["wallet"]
                chain_raw = normalized["chain"]
                days_raw = normalized["daysOption"]

                if not wallet_addr:
                    raise ValueError("Missing wallet address.")

                chain = (
                    blockchain_utils.normalize_chain(chain_raw)
                    if chain_raw is not None
                    else self.supported_chains[0]
                )
                if chain not in self.supported_chains:
                    raise ValueError(f"Chain '{chain.value}' is not enabled in settings.")

                days = (
                    blockchain_utils.parse_days_option(days_raw)
                    if days_raw is not None
                    else self.default_days
                )

                blockchain_utils.validate_wallet_address(wallet_addr, chain)

                stats = blockchain_utils.simulate_wallet_performance(
                    wallet=wallet_addr,
                    chain=chain,
                    days=days,
                )
                results.append(stats)
            except Exception as exc:
                self.logger.error(
                    "Error analyzing wallet item %r: %s", raw_item, exc, exc_info=False
                )
                # Create a WalletStats object with error information
                try:
                    wallet_unsafe = getattr(raw_item, "wallet", None)
                except Exception:
                    wallet_unsafe = None

                wallet_for_error = None
                if isinstance(raw_item, dict):
                    wallet_for_error = raw_item.get("wallet") or raw_item.get("address")
                elif isinstance(raw_item, str):
                    wallet_for_error = raw_item

                stats_with_error = WalletStats(
                    wallet=wallet_for_error or "unknown",
                    chain=SupportedChain.SOL,
                    daysOption=self.default_days,
                    error=str(exc),
                )
                results.append(stats_with_error)

        return results