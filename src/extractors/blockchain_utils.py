thonimport hashlib
import logging
import random
from typing import Dict

from models.wallet_stats import DaysOption, SupportedChain, WalletStats

logger = logging.getLogger(__name__)

def normalize_chain(chain: str) -> SupportedChain:
    if not isinstance(chain, str):
        raise ValueError(f"Chain must be a string, got {type(chain)}")
    chain_lower = chain.strip().lower()
    mapping = {
        "sol": SupportedChain.SOL,
        "solana": SupportedChain.SOL,
        "eth": SupportedChain.ETH,
        "ethereum": SupportedChain.ETH,
        "base": SupportedChain.BASE,
        "tron": SupportedChain.TRON,
        "trx": SupportedChain.TRON,
        "blast": SupportedChain.BLAST,
    }
    if chain_lower not in mapping:
        raise ValueError(f"Unsupported chain: {chain}")
    return mapping[chain_lower]

def parse_days_option(days: str) -> DaysOption:
    if not isinstance(days, str):
        raise ValueError(f"daysOption must be a string, got {type(days)}")
    normalized = days.strip().lower()
    if normalized in {"7", "7d", "week"}:
        return DaysOption.SEVEN_D
    if normalized in {"30", "30d", "month"}:
        return DaysOption.THIRTY_D
    raise ValueError(f"Unsupported daysOption: {days}")

def validate_wallet_address(wallet: str, chain: SupportedChain) -> None:
    """
    Lightweight validation based on basic heuristics for demo purposes.
    """
    if not isinstance(wallet, str) or not wallet.strip():
        raise ValueError("Wallet address must be a non-empty string.")

    wallet = wallet.strip()
    if chain in {SupportedChain.ETH, SupportedChain.BASE, SupportedChain.BLAST}:
        if not wallet.startswith("0x") or len(wallet) < 10:
            raise ValueError(f"Invalid EVM wallet address for chain {chain.value}: {wallet}")
    elif chain is SupportedChain.SOL:
        if len(wallet) < 20:
            raise ValueError(f"Invalid Solana wallet address (too short): {wallet}")
    elif chain is SupportedChain.TRON:
        if not (wallet.startswith("T") or wallet.startswith("t")) or len(wallet) < 20:
            raise ValueError(f"Invalid Tron wallet address: {wallet}")

def _deterministic_rng(wallet: str, chain: SupportedChain, days: DaysOption) -> random.Random:
    seed_material = f"{wallet}|{chain.value}|{days.value}".encode("utf-8")
    digest = hashlib.sha256(seed_material).hexdigest()
    # Use lower bits for a deterministic seed
    seed = int(digest[:16], 16)
    return random.Random(seed)

def simulate_wallet_performance(wallet: str, chain: SupportedChain, days: DaysOption) -> WalletStats:
    """
    Simulate realistic-ish wallet performance metrics deterministically.
    This function does NOT perform real on-chain queries; it is a pure simulation
    suitable for running this repository offline.
    """
    rng = _deterministic_rng(wallet, chain, days)
    logger.debug(
        "Simulating performance for wallet=%s chain=%s days=%s",
        wallet,
        chain.value,
        days.value,
    )

    # Total cost invested in USD
    total_usd_cost = round(rng.uniform(1_000.0, 100_000.0), 2)

    # PnL percentage between -50% and +200%
    pnl_pct = round(rng.uniform(-50.0, 200.0), 2)
    total_pnl_usd = round(total_usd_cost * pnl_pct / 100.0, 2)

    # Unrealized profit is some fraction (0-80%) of total PnL, can be negative too
    unrealized_fraction = rng.uniform(0.0, 0.8)
    unrealized_usd_profit = round(total_pnl_usd * unrealized_fraction, 2)

    # Balance in native tokens
    balance_native = round(rng.uniform(0.0, 10_000.0), 6)

    # Current USD wallet balance cost + PnL
    usd_balance = round(total_usd_cost + total_pnl_usd, 2)

    token_avg_usd_cost = round(rng.uniform(0.5, 500.0), 2)
    token_avg_realized_usd_profit = round(rng.uniform(10.0, 2_000.0), 2)

    # Winrate between 20% and 95%
    winrate = round(rng.uniform(20.0, 95.0), 2)

    stats_kwargs: Dict[str, object] = {
        "wallet": wallet,
        "chain": chain,
        "daysOption": days,
        "totalPnlUsdAmount": float(total_pnl_usd),
        "totalPnlPct": float(pnl_pct),
        "unrealizedUsdProfit": float(unrealized_usd_profit),
        "totalUsdCost": float(total_usd_cost),
        "tokenAvgUsdCost": float(token_avg_usd_cost),
        "tokenAvgRealizedUsdProfit": float(token_avg_realized_usd_profit),
        "balance": float(balance_native),
        "usdBalance": float(usd_balance),
        "pnlPct": float(pnl_pct),
        "winrate": float(winrate),
        "error": None,
    }

    return WalletStats(**stats_kwargs)