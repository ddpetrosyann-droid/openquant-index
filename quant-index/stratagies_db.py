# strategies_db.py - Expanded Quantpedia Strategy Database

STRATEGIES_DB = {
    "Asset Class Trend-Following (Meb Faber GTAA 5)": {
        "id": "001",
        "type": "multi_asset_trend",
        "assets": ["SPY", "EFA", "BND", "VNQ", "GSG"],
        "asset_names": {
            "SPY": "US Equities (S&P 500)",
            "EFA": "Foreign Developed Equities",
            "BND": "US Total Bond Market",
            "VNQ": "US Real Estate (REITs)",
            "GSG": "Global Commodities"
        },
        "profile": {
            "Complexity": "Simple",
            "Rebalancing": "Monthly",
            "Confidence": "Strong",
            "Paper Backtest (1973-2008)": "11.27% CAGR | 6.87% Vol | -29.43% Max DD"
        },
        "simple_rule": "Equal-weight 5 major asset classes (20% each). Hold each ETF only when above its 200-day SMA; otherwise hold Cash.",
        "fundamental_reason": "Momentum filters identify market regimes where volatility is high, avoiding multi-year bear markets.",
        "source_paper": {
            "title": "A Quantitative Approach to Tactical Asset Allocation",
            "authors": "Mebane T. Faber",
            "year": "2007",
            "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461",
            "abstract": "Demonstrates that a simple 10-month moving average across 5 global asset classes achieves equity-like returns with bond-like volatility."
        },
        "related_papers": [
            {"title": "Risk Premia Harvesting Through Dual Momentum", "authors": "Gary Antonacci (2012)", "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750", "takeaway": "Combines relative and absolute momentum."}
        ]
    },
    "#0014: Momentum Factor Effect in Stocks": {
        "id": "014",
        "type": "single_momentum",
        "assets": ["SPY", "QQQ"],
        "asset_names": {"SPY": "S&P 500", "QQQ": "Nasdaq 100 Growth"},
        "profile": {
            "Complexity": "Simple",
            "Rebalancing": "Monthly",
            "Confidence": "Strong",
            "Paper Backtest": "Captured 12-month trailing price momentum in equities."
        },
        "simple_rule": "Compare 12-month trailing returns of SPY and QQQ. Invest 100% in the asset with higher 12-month momentum if its return is > 0%; otherwise hold Cash/Bonds.",
        "fundamental_reason": "Equities that have performed well over the past 3 to 12 months tend to continue outperforming due to investor underreaction and institutional herding.",
        "source_paper": {
            "title": "Momentum Factor Effect in Stocks",
            "authors": "Quantpedia Research Team",
            "year": "2026",
            "url": "https://quantpedia.com/strategies/momentum-factor-effect-in-stocks/",
            "abstract": "Exploits intermediate-term price momentum across equity indexes."
        },
        "related_papers": [
            {"title": "Relative Strength Strategies for Investing", "authors": "Jegadeesh & Titman (1993)", "url": "https://www.jstor.org/stable/2329002", "takeaway": "Foundational paper proving stock market momentum persists."}
        ]
    },
    "#0021: Momentum Effect in Commodities": {
        "id": "021",
        "type": "commodity_mom",
        "assets": ["GSG", "GLD"],
        "asset_names": {"GSG": "S&P GSCI Commodity-Indexed Trust", "GLD": "Gold Bullion"},
        "profile": {
            "Complexity": "Simple",
            "Rebalancing": "Monthly",
            "Confidence": "Strong",
            "Paper Backtest": "14.60% CAGR | Commodity trend exploitation"
        },
        "simple_rule": "Go long commodities (GSG/GLD) when their 200-day trend is positive. Commodities exhibit strong multi-year inflation and supply shock trends.",
        "fundamental_reason": "Commodity markets are driven by physical supply and demand imbalances that take months or years to clear, creating powerful price trends.",
        "source_paper": {
            "title": "Momentum Effect in Commodities",
            "authors": "Quantpedia Screener",
            "year": "2026",
            "url": "https://quantpedia.com/strategies/momentum-effect-in-commodities/",
            "abstract": "Examines rotational momentum systems across raw material and commodity futures ETFs."
        },
        "related_papers": [
            {"title": "Facts and Fantasies about Future Returns", "authors": "Gorton & Rouwenhorst (2006)", "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=298064", "takeaway": "Proves commodities provide equity-like returns with negative correlation to stocks."}
        ]
    },
    "#0028: Value and Momentum Factors Across Asset Classes": {
        "id": "028",
        "type": "multi_asset_trend",
        "assets": ["SPY", "BND", "VNQ", "GLD"],
        "asset_names": {"SPY": "Equities", "BND": "Bonds", "VNQ": "REITs", "GLD": "Gold"},
        "profile": {
            "Complexity": "Moderate",
            "Rebalancing": "Monthly",
            "Confidence": "Strong",
            "Paper Backtest": "11.90% CAGR | Cross-Asset Factor Allocation"
        },
        "simple_rule": "Rank asset classes by a composite of 12-month momentum and trend filters, overweighting top-performing asset classes while purging negative trend assets into cash.",
        "fundamental_reason": "Combining value and momentum across diverse asset classes captures both cyclical reversion and trending persistence.",
        "source_paper": {
            "title": "Value and Momentum Factors across Asset Classes",
            "authors": "Asness, Moskowitz, & Pedersen",
            "year": "2013",
            "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2218086",
            "abstract": "Value and momentum factor returns are robustly present across global equities, bonds, commodities, and currencies."
        },
        "related_papers": [
            {"title": "The Trinity Portfolio", "authors": "Mebane Faber (2016)", "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2801856", "takeaway": "Multi-asset factor and trend combination."}
        ]
    }
}