export type DaysOption = "7d" | "30d";

export type SupportedChain = "sol" | "eth" | "base" | "tron" | "blast";

export interface WalletStats {
    wallet: string;
    chain: SupportedChain;
    daysOption: DaysOption;
    totalPnlUsdAmount: number;
    totalPnlPct: number;
    unrealizedUsdProfit: number;
    totalUsdCost: number;
    tokenAvgUsdCost: number;
    tokenAvgRealizedUsdProfit: number;
    balance: number;
    usdBalance: number;
    pnlPct: number;
    winrate: number;
    error: string | null;
}