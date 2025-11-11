thonfrom dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Optional

class DaysOption(str, Enum):
    SEVEN_D = "7d"
    THIRTY_D = "30d"

class SupportedChain(str, Enum):
    SOL = "sol"
    ETH = "eth"
    BASE = "base"
    TRON = "tron"
    BLAST = "blast"

@dataclass
class WalletStats:
    wallet: str
    chain: SupportedChain
    daysOption: DaysOption
    totalPnlUsdAmount: float = 0.0
    totalPnlPct: float = 0.0
    unrealizedUsdProfit: float = 0.0
    totalUsdCost: float = 0.0
    tokenAvgUsdCost: float = 0.0
    tokenAvgRealizedUsdProfit: float = 0.0
    balance: float = 0.0
    usdBalance: float = 0.0
    pnlPct: float = 0.0
    winrate: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a JSON-serializable representation with enum values flattened.
        """
        raw = asdict(self)
        raw["chain"] = self.chain.value
        raw["daysOption"] = self.daysOption.value
        return raw

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletStats":
        chain_raw = data.get("chain", "sol")
        days_raw = data.get("daysOption", "30d")

        chain = SupportedChain(chain_raw)
        days = DaysOption(days_raw)

        kwargs = dict(data)
        kwargs["chain"] = chain
        kwargs["daysOption"] = days
        return cls(**kwargs)