import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="OpenQuant Institutional Terminal", layout="wide")

CSV_FILE = "strategies_master.csv"
RAW_TXT_FILE = "Untitled document.txt"

# Curated Metadata for the First 37 Foundational Strategies
MASTER_STRATEGIES = [
    {
        "ID": "#0001",
        "Title": "Asset Class Trend-Following",
        "Reb": "Monthly",
        "Markets": "Equities, Bonds, Commodities, REITs",
        "Paper_Ret": 11.27,
        "Paper_Vol": 6.87,
        "Keywords": "momentum, asset class picking, trend-following",
        "Type": "trend",
        "Assets": "SPY,EFA,BND,VNQ,GSG",
        "Paper": (
            "Mebane Faber (2007) - A Quantitative Approach to Tactical Asset"
            " Allocation"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461",
        "QP_URL": (
            "https://quantpedia.com/strategies/asset-class-trend-following"
        ),
    },
    {
        "ID": "#0002",
        "Title": "Momentum Asset Allocation Strategy",
        "Reb": "Monthly",
        "Markets": "Equities, Bonds, Commodities, REITs",
        "Paper_Ret": 14.49,
        "Paper_Vol": 11.00,
        "Keywords": "momentum, asset class picking, rotational system",
        "Type": "top2",
        "Assets": "SPY,EFA,BND,VNQ,GSG",
        "Paper": (
            "Gary Antonacci (2012) - Risk Premia Harvesting Through Dual"
            " Momentum"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750",
        "QP_URL": "https://quantpedia.com/strategies/asset-class-momentum-rotational-system",
    },
    {
        "ID": "#0003",
        "Title": "Sector Momentum - Rotational System",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 13.94,
        "Paper_Vol": 18.38,
        "Keywords": "momentum, rotational system, sector picking",
        "Type": "top2",
        "Assets": "XLK,XLF,XLE,XLV,XLI,XLP,XLY",
        "Paper": (
            "Moskowitz & Grinblatt (1999) - Do Industries Explain Momentum?"
        ),
        "Paper_URL": "https://www.jstor.org/stable/222491",
        "QP_URL": (
            "https://quantpedia.com/strategies/sector-momentum-rotational-system"
        ),
    },
    {
        "ID": "#0004",
        "Title": "Overnight Anomaly",
        "Reb": "Intraday",
        "Markets": "Equities",
        "Paper_Ret": 14.00,
        "Paper_Vol": 12.50,
        "Keywords": "market timing, seasonality",
        "Type": "trend",
        "Assets": "SPY,QQQ",
        "Paper": (
            "Cooper, Cliff, & Gulen (2008) - Return Differences Between Trading"
            " and Non-Trading Hours"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1004081",
        "QP_URL": "https://quantpedia.com/strategies/overnight-anomaly",
    },
    {
        "ID": "#0005",
        "Title": "FX Carry Trade",
        "Reb": "Monthly",
        "Markets": "Currencies",
        "Paper_Ret": 7.27,
        "Paper_Vol": 9.60,
        "Keywords": (
            "carry trade, FX anomaly, forex system, factor investing, smart"
            " beta"
        ),
        "Type": "top2",
        "Assets": "UUP,FXA,FXE,FXY,FXB",
        "Paper": (
            "Lustig, Roussanov, & Verdelhan (2011) - Common Risk Factors in"
            " Currency Markets"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1269446",
        "QP_URL": "https://quantpedia.com/strategies/fx-carry-trade",
    },
    {
        "ID": "#0006",
        "Title": "Bond Carry Strategy",
        "Reb": "Monthly",
        "Markets": "Bonds",
        "Paper_Ret": 9.91,
        "Paper_Vol": 8.63,
        "Keywords": "carry trade, factor investing, smart beta",
        "Type": "top2",
        "Assets": "TLT,IEF,HYG,LQD,EMB",
        "Paper": "Koijen, Moskowitz, Pedersen, & Vrugt (2018) - Carry",
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2298565",
        "QP_URL": "https://quantpedia.com/strategies/bond-carry-strategy",
    },
    {
        "ID": "#0007",
        "Title": "Low Volatility Factor Effect in Stocks",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 11.30,
        "Paper_Vol": 10.10,
        "Keywords": (
            "stock picking, volatility effect, factor investing, smart beta"
        ),
        "Type": "trend",
        "Assets": "USMV,SPLV,SPY",
        "Paper": (
            "Blitz & van Vliet (2007) - The Volatility Effect: Lower Risk"
            " Without Lower Return"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=980865",
        "QP_URL": "https://quantpedia.com/strategies/low-volatility-factor-effect-in-stocks",
    },
    {
        "ID": "#0008",
        "Title": "Currency Momentum Factor",
        "Reb": "Monthly",
        "Markets": "Currencies",
        "Paper_Ret": 7.61,
        "Paper_Vol": 10.22,
        "Keywords": (
            "momentum, FX anomaly, forex system, factor investing, smart beta"
        ),
        "Type": "top2",
        "Assets": "UUP,FXE,FXY,FXA,FXC",
        "Paper": (
            "Menkhoff, Sarno, Schmeling, & Schrimpf (2012) - Currency Momentum"
            " Strategies"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1409822",
        "QP_URL": "https://quantpedia.com/strategies/currency-momentum-factor",
    },
    {
        "ID": "#0009",
        "Title": "Currency Value Factor - PPP Strategy",
        "Reb": "Quarterly",
        "Markets": "Currencies",
        "Paper_Ret": 7.82,
        "Paper_Vol": 9.33,
        "Keywords": (
            "FX anomaly, forex system, value, factor investing, smart beta"
        ),
        "Type": "valmom",
        "Assets": "UUP,FXE,FXY,FXB,FXA",
        "Paper": (
            "Asness, Moskowitz, & Pedersen (2013) - Value and Momentum"
            " Everywhere (FX Value)"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2174501",
        "QP_URL": "https://quantpedia.com/strategies/currency-value-factor-ppp-strategy",
    },
    {
        "ID": "#0010",
        "Title": "Sector Rotation based on Monetary Policy",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 15.82,
        "Paper_Vol": 15.50,
        "Keywords": "sector picking, monetary policy",
        "Type": "top2",
        "Assets": "XLF,XLK,XLV,XLP,XLU",
        "Paper": (
            "Conover, Jensen, Johnson, & Mercer (2008) - Sector Rotation and"
            " Monetary Conditions"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=936946",
        "QP_URL": "https://quantpedia.com/strategies/sector-rotation-based-on-monetary-policy",
    },
    {
        "ID": "#0011",
        "Title": "Stock Return Reversal within Industries",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 16.78,
        "Paper_Vol": 12.91,
        "Keywords": "stock picking, reversal, equity long short",
        "Type": "rev_dip",
        "Assets": "XLK,XLF,XLE,XLV,XLI",
        "Paper": "Hameed & Mian (2015) - Industries and Stock Return Reversals",
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2163621",
        "QP_URL": "https://quantpedia.com/strategies/stock-return-reversal-within-industries",
    },
    {
        "ID": "#0012",
        "Title": "Pairs Trading with Stocks",
        "Reb": "Daily",
        "Markets": "Equities",
        "Paper_Ret": 11.16,
        "Paper_Vol": 5.85,
        "Keywords": "equity long short, pairs trading, arbitrage",
        "Type": "rev_dip",
        "Assets": "SPY,QQQ,IWM,DIA",
        "Paper": (
            "Gatev, Goetzmann, & Rouwenhorst (2006) - Pairs Trading:"
            " Performance of a Relative-Value Rule"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=141615",
        "QP_URL": "https://quantpedia.com/strategies/pairs-trading-with-stocks",
    },
    {
        "ID": "#0013",
        "Title": "Short Term Reversal Effect in Stocks",
        "Reb": "Weekly",
        "Markets": "Equities",
        "Paper_Ret": 16.25,
        "Paper_Vol": 14.94,
        "Keywords": (
            "stock picking, reversal, equity long short, factor investing,"
            " smart beta"
        ),
        "Type": "rev_dip",
        "Assets": "SPY,QQQ,SMH,XBI",
        "Paper": (
            "Jegadeesh (1990) - Evidence of Predictable Behavior of Security"
            " Returns"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2328797",
        "QP_URL": (
            "https://quantpedia.com/strategies/short-term-reversal-in-stocks"
        ),
    },
    {
        "ID": "#0014",
        "Title": "Momentum Factor Effect in Stocks",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 8.30,
        "Paper_Vol": 16.60,
        "Keywords": (
            "momentum, stock picking, momentum in stocks, factor investing,"
            " smart beta"
        ),
        "Type": "top2",
        "Assets": "MTUM,QQQ,SPY,IWM",
        "Paper": (
            "Jegadeesh & Titman (1993) - Returns to Buying Winners and Selling"
            " Losers"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2329002",
        "QP_URL": (
            "https://quantpedia.com/strategies/momentum-factor-effect-in-stocks"
        ),
    },
    {
        "ID": "#0015",
        "Title": "Momentum Factor Effect in Country Equity Indexes",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 17.70,
        "Paper_Vol": 15.20,
        "Keywords": (
            "momentum, rotational system, country picking, factor investing,"
            " smart beta"
        ),
        "Type": "top2",
        "Assets": "SPY,EWJ,EWG,EWU,FXI,EWZ",
        "Paper": (
            "Bhojraj & Swaminathan (2006) - Macromomentum: Returns"
            " Predictability in International Equity Indices"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=267991",
        "QP_URL": "https://quantpedia.com/strategies/momentum-factor-effect-in-country-equity-indexes",
    },
    {
        "ID": "#0016",
        "Title": "Reversal Effect in International Equity ETFs",
        "Reb": "3 Years",
        "Markets": "Equities",
        "Paper_Ret": 6.40,
        "Paper_Vol": 14.10,
        "Keywords": (
            "rotational system, reversal, country picking, factor investing,"
            " smart beta"
        ),
        "Type": "valmom",
        "Assets": "SPY,EFA,VWO,EWJ,EWZ",
        "Paper": (
            "Richards (1997) - Winner-Loser Reversals in National Stock Market"
            " Indices"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2329472",
        "QP_URL": "https://quantpedia.com/strategies/mean-reversion-effect-in-country-equity-indexes",
    },
    {
        "ID": "#0017",
        "Title": "Momentum Effect in Anomalies/Trading Systems",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 13.76,
        "Paper_Vol": 11.40,
        "Keywords": (
            "momentum, factor investing, smart beta, factor allocation"
        ),
        "Type": "top2",
        "Assets": "MTUM,VLUE,QUAL,USMV,SIZE",
        "Paper": (
            "Arnott, Clements, Kalesnik, & Linnainmaa (2019) - Factor Momentum"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3116974",
        "QP_URL": "https://quantpedia.com/strategies/momentum-effect-in-anomalies-trading-systems",
    },
    {
        "ID": "#0018",
        "Title": "Liquidity Effect in Stocks",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 6.68,
        "Paper_Vol": 11.87,
        "Keywords": (
            "stock picking, equity long short, liquidity risk premium, factor"
            " investing, smart beta"
        ),
        "Type": "trend",
        "Assets": "IWM,IJH,SPY",
        "Paper": (
            "Ibbotson, Chen, Kim, & Hu (2013) - Liquidity as an Investment"
            " Style"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2008946",
        "QP_URL": "https://quantpedia.com/strategies/liquidity-effect-in-stocks",
    },
    {
        "ID": "#0019",
        "Title": "Dividend Month Anomaly",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 17.90,
        "Paper_Vol": 20.00,
        "Keywords": "seasonality, stock picking, factor investing, smart beta",
        "Type": "trend",
        "Assets": "SCHD,VYM,DVY,SPY",
        "Paper": "Hartzmark & Solomon (2013) - The Dividend Month Premium",
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1790634",
        "QP_URL": "https://quantpedia.com/strategies/dividend-month-anomaly",
    },
    {
        "ID": "#0020",
        "Title": "Volatility Risk Premium Effect",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 26.00,
        "Paper_Vol": 19.00,
        "Keywords": (
            "volatility effect, volatility premium, factor investing, smart"
            " beta"
        ),
        "Type": "trend",
        "Assets": "SVXY,PUTW,SPY,TLT",
        "Paper": (
            "Bollerslev, Tauchen, & Zhou (2009) - Expected Stock Returns and"
            " Variance Risk Premia"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=976312",
        "QP_URL": (
            "https://quantpedia.com/strategies/volatility-risk-premium-effect"
        ),
    },
    {
        "ID": "#0021",
        "Title": "Momentum Effect in Commodities",
        "Reb": "Monthly",
        "Markets": "Commodities",
        "Paper_Ret": 14.60,
        "Paper_Vol": 25.57,
        "Keywords": (
            "momentum, rotational system, factor investing, smart beta"
        ),
        "Type": "top2",
        "Assets": "GLD,SLV,USO,DBA,GSG",
        "Paper": (
            "Miffre & Rallis (2007) - Momentum Strategies in Commodity Futures"
            " Markets"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=929548",
        "QP_URL": (
            "https://quantpedia.com/strategies/momentum-effect-in-commodities"
        ),
    },
    {
        "ID": "#0022",
        "Title": "Term Structure Effect in Commodities",
        "Reb": "Monthly",
        "Markets": "Commodities",
        "Paper_Ret": 11.73,
        "Paper_Vol": 23.84,
        "Keywords": (
            "rotational system, term spread, factor investing, smart beta"
        ),
        "Type": "top2",
        "Assets": "DBC,USCI,GSG,GLD",
        "Paper": (
            "Gorton, Hayashi, & Rouwenhorst (2012) - The Fundamentals of"
            " Commodity Futures Returns"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=996930",
        "QP_URL": "https://quantpedia.com/strategies/term-structure-effect-in-commodities",
    },
    {
        "ID": "#0023",
        "Title": "Momentum Combined with Term Structure in Commodities",
        "Reb": "Monthly",
        "Markets": "Commodities",
        "Paper_Ret": 21.80,
        "Paper_Vol": 27.60,
        "Keywords": (
            "momentum, rotational system, term spread, factor investing, smart"
            " beta"
        ),
        "Type": "top2",
        "Assets": "DBC,USCI,GLD,SLV,USO",
        "Paper": (
            "Fuertes, Miffre, & Rallis (2010) - Tactical Allocation in"
            " Commodity Futures Markets"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1195522",
        "QP_URL": "https://quantpedia.com/strategies/momentum-effect-combined-with-term-structure-in-commodities",
    },
    {
        "ID": "#0024",
        "Title": "Merger Arbitrage",
        "Reb": "Daily",
        "Markets": "Equities",
        "Paper_Ret": 6.86,
        "Paper_Vol": 4.72,
        "Keywords": (
            "equity long short, arbitrage, factor investing, smart beta"
        ),
        "Type": "trend",
        "Assets": "MNA,USMV,SHY",
        "Paper": (
            "Mitchell & Pulvino (2001) - Characteristics of Risk and Return in"
            " Risk Arbitrage"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2697820",
        "QP_URL": "https://quantpedia.com/strategies/merger-arbitrage",
    },
    {
        "ID": "#0025",
        "Title": "Size Factor - Small Capitalization Stocks Premium",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 6.10,
        "Paper_Vol": 25.60,
        "Keywords": (
            "stock picking, equity long short, small cap, factor investing,"
            " smart beta"
        ),
        "Type": "trend",
        "Assets": "IWM,IJR,VB,SPY",
        "Paper": (
            "Banz (1981) & Fama-French (1992) - The Relationship Between Return"
            " and Market Value of Common Stocks"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2328882",
        "QP_URL": "https://quantpedia.com/strategies/small-capitalization-stocks-premium-anomaly",
    },
    {
        "ID": "#0026",
        "Title": "Value (Book-to-Market) Factor",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 3.60,
        "Paper_Vol": 12.02,
        "Keywords": (
            "stock picking, value, fundamental analysis, factor investing,"
            " smart beta"
        ),
        "Type": "valmom",
        "Assets": "VLUE,VTV,IWD,SPY",
        "Paper": (
            "Fama & French (1992) - The Cross-Section of Expected Stock Returns"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2329112",
        "QP_URL": (
            "https://quantpedia.com/strategies/value-book-to-market-factor"
        ),
    },
    {
        "ID": "#0027",
        "Title": "Market Timing with Aggregate and Idiosyncratic Volatilities",
        "Reb": "Quarterly",
        "Markets": "Equities",
        "Paper_Ret": 20.07,
        "Paper_Vol": 37.80,
        "Keywords": "market timing, volatility effect",
        "Type": "vol_time",
        "Assets": "SPY,TLT",
        "Paper": (
            "Guo & Savickas (2006) - Idiosyncratic Volatility, Stock Market"
            " Volatility, and Expected Stock Returns"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=480961",
        "QP_URL": "https://quantpedia.com/strategies/market-timing-with-aggregate-and-idiosyncratic-stock-volatilities",
    },
    {
        "ID": "#0028",
        "Title": "Value and Momentum Factors across Asset Classes",
        "Reb": "Monthly",
        "Markets": "Equities, Bonds, REITs",
        "Paper_Ret": 11.90,
        "Paper_Vol": 10.00,
        "Keywords": (
            "momentum, asset class picking, value, factor investing, smart beta"
        ),
        "Type": "valmom",
        "Assets": "SPY,EFA,VNQ,GLD,BND",
        "Paper": (
            "Asness, Moskowitz, & Pedersen (2013) - Value and Momentum"
            " Everywhere"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2174501",
        "QP_URL": "https://quantpedia.com/strategies/value-and-momentum-factors-across-asset-classes",
    },
    {
        "ID": "#0029",
        "Title": "Market Timing S&P 500 with VIX and COT Report",
        "Reb": "Weekly",
        "Markets": "Equities",
        "Paper_Ret": 9.70,
        "Paper_Vol": 11.00,
        "Keywords": "market timing, sentiment trading, alternative data",
        "Type": "vol_time",
        "Assets": "SPY,TLT",
        "Paper": (
            "Giot (2005) & Briese (2008) - Commitments of Traders and Implied"
            " Volatility Timing"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=496262",
        "QP_URL": "https://quantpedia.com/strategies/market-timing-sp-500-with-vix-and-cot-report",
    },
    {
        "ID": "#0030",
        "Title": "Timing Commodities and S&P500 with COT Report",
        "Reb": "Weekly",
        "Markets": "Equities, Commodities",
        "Paper_Ret": 16.80,
        "Paper_Vol": 10.30,
        "Keywords": (
            "asset class picking, market timing, sentiment trading,"
            " alternative data"
        ),
        "Type": "top2",
        "Assets": "SPY,DBC,GLD,TLT",
        "Paper": (
            "De Roon, Nijman, & Veld (2000) - Hedging Pressure Effects in"
            " Futures Markets"
        ),
        "Paper_URL": "https://www.jstor.org/stable/222456",
        "QP_URL": "https://quantpedia.com/strategies/timing-commodities-and-sp500-with-cot-report",
    },
    {
        "ID": "#0031",
        "Title": "Market Seasonality Effect in World Equity Indexes",
        "Reb": "6 Months",
        "Markets": "Equities",
        "Paper_Ret": 8.80,
        "Paper_Vol": 13.50,
        "Keywords": "market timing, seasonality",
        "Type": "trend",
        "Assets": "SPY,EFA,EWJ,EWU",
        "Paper": (
            "Bouman & Jacobsen (2002) - The Halloween Indicator, 'Sell in May"
            " and Go Away'"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=76248",
        "QP_URL": "https://quantpedia.com/strategies/market-seasonality-effect-in-world-equity-indexes",
    },
    {
        "ID": "#0032",
        "Title": "Combining Seasonality and Momentum in US Equity Sectors",
        "Reb": "Monthly",
        "Markets": "Equities",
        "Paper_Ret": 12.90,
        "Paper_Vol": 17.00,
        "Keywords": (
            "momentum, rotational system, sector picking, seasonality, equity"
            " long short"
        ),
        "Type": "top2",
        "Assets": "XLK,XLF,XLE,XLV,XLI,XLP",
        "Paper": (
            "Jacobsen & Visaltanachoti (2009) - The Halloween Effect in US"
            " Sectors"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=955639",
        "QP_URL": "https://quantpedia.com/strategies/combining-seasonality-and-momentum-in-us-equity-sectors",
    },
    {
        "ID": "#0033",
        "Title": "Post-Earnings Announcement Effect",
        "Reb": "Quarterly",
        "Markets": "Equities",
        "Paper_Ret": 15.00,
        "Paper_Vol": 14.00,
        "Keywords": (
            "stock picking, fundamental analysis, earnings announcement"
        ),
        "Type": "top2",
        "Assets": "MTUM,QUAL,QQQ,SPY",
        "Paper": (
            "Bernard & Thomas (1989) - Post-Earnings-Announcement Drift:"
            " Delayed Price Response"
        ),
        "Paper_URL": "https://www.jstor.org/stable/2491062",
        "QP_URL": "https://quantpedia.com/strategies/post-earnings-announcement-effect",
    },
    {
        "ID": "#0034",
        "Title": "Post-Loss/Profit Announcement Drift in Stocks",
        "Reb": "Daily",
        "Markets": "Equities",
        "Paper_Ret": 26.00,
        "Paper_Vol": 5.00,
        "Keywords": "stock picking, earnings announcement, trading earnings",
        "Type": "top2",
        "Assets": "QUAL,MTUM,SPY",
        "Paper": (
            "Balakrishnan, Bartov, & Faurel (2010) - Post-Loss/Profit"
            " Announcement Drift"
        ),
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1122990",
        "QP_URL": "https://quantpedia.com/strategies/post-loss-profit-announcement-drift-in-stocks",
    },
    {
        "ID": "#0035",
        "Title": "Insiders Trading Effect in Stocks",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 7.70,
        "Paper_Vol": 15.00,
        "Keywords": (
            "stock picking, insiders trading effect, alternative data"
        ),
        "Type": "trend",
        "Assets": "KNOW,SPY,IWM",
        "Paper": "Lakonishok & Lee (2001) - Are Insider Trades Informative?",
        "Paper_URL": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=165268",
        "QP_URL": (
            "https://quantpedia.com/strategies/insiders-trading-effect-in-stocks"
        ),
    },
    {
        "ID": "#0036",
        "Title": "Net Payout Yield Effect",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 22.13,
        "Paper_Vol": 15.50,
        "Keywords": (
            "stock picking, value, fundamental analysis, factor investing"
        ),
        "Type": "trend",
        "Assets": "PKW,SCHD,SYLD,SPY",
        "Paper": (
            "Boudoukh, Michaely, Richardson, & Roberts (2007) - On the"
            " Importance of Measuring Payout Yield"
        ),
        "Paper_URL": "https://www.jstor.org/stable/4123482",
        "QP_URL": "https://quantpedia.com/strategies/net-payout-yield-effect",
    },
    {
        "ID": "#0037",
        "Title": "Net Current Asset Value Effect",
        "Reb": "Yearly",
        "Markets": "Equities",
        "Paper_Ret": 31.19,
        "Paper_Vol": 18.00,
        "Keywords": (
            "stock picking, value, fundamental analysis, factor investing"
        ),
        "Type": "valmom",
        "Assets": "IWN,VBR,VLUE,SPY",
        "Paper": (
            "Benjamin Graham & Oppenheimer (1986) - Ben Graham's Net Current"
            " Asset Values"
        ),
        "Paper_URL": "https://www.jstor.org/stable/4478980",
        "QP_URL": (
            "https://quantpedia.com/strategies/net-current-asset-value-effect"
        ),
    },
]

KNOWN_KEYWORDS = sorted(
    [
        "momentum in stocks",
        "asset class picking",
        "trend-following",
        "rotational system",
        "sector picking",
        "market timing",
        "seasonality",
        "carry trade",
        "FX anomaly",
        "forex system",
        "factor investing",
        "smart beta",
        "stock picking",
        "volatility effect",
        "equity long short",
        "pairs trading",
        "country picking",
        "factor allocation",
        "liquidity risk premium",
        "volatility premium",
        "term spread",
        "small cap",
        "fundamental analysis",
        "sentiment trading",
        "alternative data",
        "earnings announcement",
        "trading earnings",
        "insiders trading effect",
        "accruals effect",
        "fund picking",
        "short selling",
        "volume effect",
        "beta factor",
        "growth stocks",
        "bond timing",
        "spread trading",
        "cryptocurrencies",
        "machine learning",
        "ESG investing",
        "diversification",
        "monetary policy",
        "arbitrage",
        "reversal",
        "momentum",
        "value",
        "sentiment",
    ],
    key=len,
    reverse=True,
)

VALID_REBS = {
    "Monthly",
    "Quarterly",
    "Yearly",
    "Daily",
    "Intraday",
    "Weekly",
    "6 Months",
    "3 Years",
}


def split_concatenated_keywords(raw_kw):
  """Splits squished Quantpedia keyword strings like 'momentumasset class picking' into clean tags."""
  rem = raw_kw.strip()
  found = []
  for kw in KNOWN_KEYWORDS:
    if kw in rem:
      found.append(kw)
      rem = rem.replace(kw, " ")
  return ", ".join(found) if found else raw_kw.strip()


def assign_proxy_assets_and_type(markets_str, keywords_str, title_str):
  """Automatically assigns liquid ETF proxies and signal logic to any parsed strategy."""
  m_low = markets_str.lower()
  k_low = keywords_str.lower()
  t_low = title_str.lower()

  # 1. Assign ETF Proxy Basket
  if "crypto" in m_low or "bitcoin" in t_low or "crypto" in t_low:
    if "equities" in m_low or "commodities" in m_low:
      assets = "BTC-USD,GLD,QQQ,SPY"
    else:
      assets = "BTC-USD,ETH-USD,SPY"
  elif (
      len(markets_str.split(",")) >= 3
      or "asset class" in k_low
      or "multi-asset" in t_low
  ):
    assets = "SPY,EFA,BND,VNQ,GLD"
  elif "currencies" in m_low:
    assets = "UUP,FXE,FXY,FXA,FXB"
  elif "commodities" in m_low and "equities" in m_low:
    assets = "SPY,DBC,GLD,USO,TLT"
  elif "commodities" in m_low:
    assets = "GLD,SLV,USO,DBA,DBC"
  elif "bonds" in m_low and "equities" in m_low:
    assets = "SPY,TLT,IEF,HYG,SHY"
  elif "bonds" in m_low:
    assets = "TLT,IEF,LQD,HYG,SHY"
  elif "reits" in m_low:
    assets = "VNQ,IYR,SCHH,SPY"
  elif "sector" in k_low or "industry" in t_low:
    assets = "XLK,XLF,XLE,XLV,XLI,XLP,XLU"
  elif (
      "country" in k_low
      or "international" in t_low
      or "china" in t_low
      or "india" in t_low
      or "european" in t_low
      or "japanese" in t_low
  ):
    assets = "SPY,EFA,VWO,EWJ,EWG,FXI"
  elif "small cap" in k_low or "smb" in t_low:
    assets = "IWM,IJR,VB,SPY"
  elif "value" in k_low or "hml" in t_low:
    assets = "VLUE,VTV,IWD,SPY"
  elif "volatility" in k_low or "vix" in t_low or "beta" in k_low:
    assets = "USMV,SPLV,SPY,TLT"
  else:
    assets = "MTUM,QUAL,VLUE,USMV,SPY"

  # 2. Assign Signal Type
  if "reversal" in k_low or "pairs trading" in k_low or "arbitrage" in k_low:
    stype = "rev_dip"
  elif "volatility" in k_low and "market timing" in k_low:
    stype = "vol_time"
  elif "value" in k_low:
    stype = "valmom"
  elif "trend-following" in k_low or "market timing" in k_low:
    stype = "trend"
  else:
    stype = "top2"

  return assets, stype


def parse_quantpedia_raw_text(raw_text):
  """Parses the raw text dump ('Untitled document.txt') into structured strategy dicts."""
  curated_map = {row["ID"]: row for row in MASTER_STRATEGIES}
  lines = [
      line.strip()
      for line in raw_text.replace("\r\n", "\n").split("\n")
      if line.strip()
  ]

  id_pattern = re.compile(r"^(#\d{4}|\d{3,4}|ff\d{2})$", re.IGNORECASE)
  blocks = []
  curr_id = None
  curr_lines = []

  for line in lines:
    if id_pattern.match(line):
      if curr_id is not None:
        blocks.append((curr_id, curr_lines))
      raw_id = line
      if raw_id.isdigit():
        curr_id = f"#{int(raw_id):04d}"
      elif raw_id.lower().startswith("ff"):
        curr_id = raw_id.upper()
      else:
        curr_id = raw_id
      curr_lines = []
    else:
      if curr_id is not None:
        curr_lines.append(line)
  if curr_id is not None:
    blocks.append((curr_id, curr_lines))

  parsed_rows = {}
  for cid, b_lines in blocks:
    if cid in curated_map:
      parsed_rows[cid] = curated_map[cid]
      continue
    if not b_lines:
      continue

    title = b_lines[0]
    reb = "Monthly"
    markets = "Equities"
    pcts = []
    kw_raw = ""

    for item in b_lines[1:]:
      if item in VALID_REBS:
        reb = item
      elif item.endswith("%") and re.match(r"^-?\d+(\.\d+)?%$", item):
        pcts.append(float(item.replace("%", "")))
      else:
        mkt_matches = re.findall(
            r"Equities|Bonds|Commodities|REITs|Currencies|Crypto", item
        )
        if mkt_matches and "".join(mkt_matches) == item.replace(" ", ""):
          markets = ", ".join(mkt_matches)
        else:
          kw_raw += " " + item

    if len(pcts) >= 2:
      paper_ret, paper_vol = pcts[0], max(pcts[1], 1.0)
    elif len(pcts) == 1:
      paper_ret = pcts[0]
      paper_vol = 14.0
    else:
      paper_ret, paper_vol = 9.5, 14.0

    keywords = (
        split_concatenated_keywords(kw_raw) if kw_raw.strip() else "factor investing, smart beta"
    )
    assets, stype = assign_proxy_assets_and_type(markets, keywords, title)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    qp_url = f"https://quantpedia.com/strategies/{slug}"
    paper_search_url = f"https://scholar.google.com/scholar?q={urllib.parse.quote(title + ' quantitative strategy')}"

    parsed_rows[cid] = {
        "ID": cid,
        "Title": title,
        "Reb": reb,
        "Markets": markets,
        "Paper_Ret": round(paper_ret, 2),
        "Paper_Vol": round(paper_vol, 2),
        "Keywords": keywords,
        "Type": stype,
        "Assets": assets,
        "Paper": f"Quantpedia Quantitative Factor Study — {title}",
        "Paper_URL": paper_search_url,
        "QP_URL": qp_url,
    }

  # Ensure all 37 curated strategies are always present
  for row in MASTER_STRATEGIES:
    if row["ID"] not in parsed_rows:
      parsed_rows[row["ID"]] = row

  return list(parsed_rows.values())


def compute_openquant_score(row):
  """Proprietary OpenQuant Alpha Score (0-100) combining 4 Quantitative Pillars."""
  ret = float(row["Paper_Ret"])
  vol = max(float(row["Paper_Vol"]), 4.0)
  sharpe = ret / vol

  p_sharpe = min(40.0, max(0.0, sharpe * 22.0))
  p_safety = max(5.0, 25.0 - max(0.0, (vol - 6.0) * 0.8))
  reb_map = {
      "Monthly": 20.0,
      "Quarterly": 19.0,
      "6 Months": 18.0,
      "Yearly": 18.0,
      "3 Years": 16.0,
      "Weekly": 14.0,
      "Daily": 9.0,
      "Intraday": 6.0,
  }
  p_exec = reb_map.get(row["Reb"], 15.0)
  mkt_count = len(str(row["Markets"]).split(","))
  p_div = min(15.0, 8.0 + mkt_count * 2.5)

  total = round(p_sharpe + p_safety + p_exec + p_div, 1)
  grade = (
      "A+"
      if total >= 82
      else ("A" if total >= 74 else ("B+" if total >= 66 else "B"))
  )
  return total, grade


# Auto-load from Untitled document.txt if present in repo, else strategies_master.csv
if os.path.exists(RAW_TXT_FILE):
  with open(RAW_TXT_FILE, "r", encoding="utf-8", errors="ignore") as f:
    parsed_list = parse_quantpedia_raw_text(f.read())
  df_strats = pd.DataFrame(parsed_list)
  df_strats.to_csv(CSV_FILE, index=False)
elif os.path.exists(CSV_FILE):
  df_strats = pd.read_csv(CSV_FILE)
  if len(df_strats) < 37:
    df_strats = pd.DataFrame(MASTER_STRATEGIES)
    df_strats.to_csv(CSV_FILE, index=False)
else:
  df_strats = pd.DataFrame(MASTER_STRATEGIES)
  df_strats.to_csv(CSV_FILE, index=False)

scores_grades = df_strats.apply(compute_openquant_score, axis=1)
df_strats["OQ_Score"] = [sg[0] for sg in scores_grades]
df_strats["Rating"] = [sg[1] for sg in scores_grades]
df_strats["Paper_Sharpe"] = (
    df_strats["Paper_Ret"] / df_strats["Paper_Vol"].replace(0, 14.0)
).round(2)


@st.cache_data(ttl=3600)
def fetch_related_papers(title_query, keywords_query):
  """Fetches real academic working papers related to the strategy from Cornell arXiv API."""
  papers = []
  try:
    clean_q = re.sub(
        r"[^a-zA-Z0-9 ]",
        "",
        f"{title_query} {str(keywords_query).split(',')[0]}",
    )
    terms = "+AND+".join(clean_q.split()[:4])
    url = f"http://export.arxiv.org/api/query?search_query=cat:q-fin*+AND+all:{terms}&start=0&max_results=4&sortBy=relevance"
    req = urllib.request.Request(
        url, headers={"User-Agent": "OpenQuantTerminal/7.3"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
      root = ET.fromstring(resp.read())
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall("atom:entry", ns):
      t = entry.find("atom:title", ns).text.strip().replace("\n", " ")
      s = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
      pub = entry.find("atom:published", ns).text[:10]
      link = entry.find("atom:id", ns).text
      authors = [
          a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)
      ]
      papers.append({
          "title": t,
          "authors": ", ".join(authors[:3]),
          "date": pub,
          "abstract": s[:280] + "...",
          "url": link,
          "pdf": link.replace("/abs/", "/pdf/") + ".pdf",
      })
  except Exception:
    pass
  return papers


@st.cache_data(ttl=3600)
def get_data(tickers, start_yr):
  """Downloads clean total-return adjusted price data and eliminates pre-inception flatlines."""
  t_list = list(tickers)
  try:
    raw = yf.download(
        t_list,
        start=f"{start_yr}-01-01",
        auto_adjust=True,
        progress=False,
        timeout=8,
    )
    if not raw.empty and "Close" in raw:
      pr = raw["Close"]
      if isinstance(pr, pd.Series):
        pr = pr.to_frame(name=t_list[0])
      pr = pr.ffill(limit=5).dropna(how="any")
      pr = pr[(pr > 0).all(axis=1)]
      if len(pr) > 260 and all(x in pr.columns for x in t_list):
        inception_date = pr.index[0].strftime("%Y-%m-%d")
        return (
            pr[t_list],
            f"🟢 Live Yahoo Finance Data (Common Inception: {inception_date})",
        )
  except Exception:
    pass
  dates = pd.date_range(start=f"{start_yr}-01-01", periods=2200, freq="B")
  sim = {
      t: 100
      * np.exp(
          np.cumsum(
              np.random.RandomState(abs(hash(t)) % 9999).normal(
                  0.00045, 0.011, len(dates)
              )
          )
      )
      for t in t_list
  }
  return pd.DataFrame(sim, index=dates), "🟡 Simulated Fallback Data"


def run_bt(prices, stype, assets, reb_freq="Monthly", cash_rate_pa=4.2):
  """Runs backtest with dynamic warmup, intra-period weight drift, and Beta-Equivalent Benchmark."""
  rets = prices[assets].pct_change().fillna(0.0)
  sma = prices[assets].rolling(200).mean()
  target_w = pd.DataFrame(0.0, index=prices.index, columns=assets)

  warmup_bars = 205
  if stype == "trend":
    target_w = (prices[assets] > sma).astype(float) * (1.0 / len(assets))
  elif stype == "top2":
    m = prices[assets].pct_change(126)
    k = min(2, len(assets))
    target_w = (
        (m.rank(axis=1, ascending=False) <= k) & (prices[assets] > sma)
    ).astype(float) * (1.0 / k)
  elif stype == "rev_dip":
    m20 = prices[assets].pct_change(20)
    k = min(2, len(assets))
    target_w = (
        (m20.rank(axis=1, ascending=True) <= k) & (prices[assets] > sma)
    ).astype(float) * (1.0 / k)
  elif stype == "vol_time":
    vol20 = rets[assets[0]].rolling(20).std() * np.sqrt(252)
    calm = (vol20 < 0.22) & (prices[assets[0]] > sma[assets[0]])
    target_w[assets[0]] = np.where(calm, 1.0, 0.0)
    if len(assets) > 1:
      target_w[assets[1]] = np.where(~calm, 1.0, 0.0)
  else:
    score = (
        prices[assets].pct_change(252).rank(axis=1)
        + 0.5 * (-prices[assets].pct_change(500)).rank(axis=1)
    )
    k = min(3, len(assets))
    target_w = (
        (score.rank(axis=1, ascending=False) <= k) & (prices[assets] > sma)
    ).astype(float) / k
    warmup_bars = 505

  if len(prices) <= warmup_bars + 60:
    warmup_bars = min(205, max(20, len(prices) // 4))

  Valid = prices.index[warmup_bars:]
  sig_w = target_w.shift(1).fillna(0.0).loc[Valid]
  valid_rets = rets.loc[Valid]

  freq_map = {
      "Weekly": "W-FRI",
      "Monthly": "ME",
      "Quarterly": "QE",
      "6 Months": "2QE",
      "Yearly": "YE",
      "3 Years": "3YE",
  }
  pd_freq = freq_map.get(reb_freq, None)
  if pd_freq and stype != "vol_time":
    reb_dates = set(sig_w.resample(pd_freq).last().index)
  else:
    reb_dates = set(Valid)

  daily_cash = (1.0 + cash_rate_pa / 100.0) ** (1.0 / 252.0) - 1.0

  # Simulate Real Intra-Period Portfolio Weight Drift Between Rebalance Dates
  n_days = len(Valid)
  n_assets = len(assets)
  drifted_w = np.zeros((n_days, n_assets))
  cash_w_arr = np.zeros(n_days)
  strat_ret_arr = np.zeros(n_days)

  curr_w = sig_w.iloc[0].values.copy()
  curr_cash = max(0.0, 1.0 - curr_w.sum())

  for i, dt in enumerate(Valid):
    if i == 0 or dt in reb_dates:
      curr_w = sig_w.iloc[i].values.copy()
      curr_cash = max(0.0, 1.0 - curr_w.sum())

    drifted_w[i, :] = curr_w
    cash_w_arr[i] = curr_cash

    r_vec = valid_rets.iloc[i].values
    day_ret = np.dot(curr_w, r_vec) + curr_cash * daily_cash
    strat_ret_arr[i] = day_ret

    denom = 1.0 + day_ret
    if denom > 1e-9:
      curr_w = curr_w * (1.0 + r_vec) / denom
      curr_cash = curr_cash * (1.0 + daily_cash) / denom

  sr = pd.Series(strat_ret_arr, index=Valid)
  mkt_r = valid_rets.mean(axis=1)

  # Beta-Equivalent Benchmark Calculation
  strat_excess = sr - daily_cash
  mkt_excess = mkt_r - daily_cash
  mkt_var = mkt_excess.var()
  beta = strat_excess.cov(mkt_excess) / mkt_var if mkt_var > 1e-12 else 1.0

  beta_bench_r = daily_cash + beta * mkt_excess
  ann_alpha = ((sr - beta_bench_r).mean() * 252) * 100.0

  out = pd.DataFrame(
      {"Strat_Ret": sr, "Beta_Bench_Ret": beta_bench_r, "EW_Ret": mkt_r},
      index=Valid,
  )
  out["Strategy"] = 10000.0 * (1.0 + sr).cumprod()
  out["Beta_Bench"] = 10000.0 * (1.0 + beta_bench_r).cumprod()

  weights_out = pd.DataFrame(drifted_w, index=Valid, columns=assets)
  weights_out["Cash (T-Bills)"] = cash_w_arr

  return out, weights_out, beta, ann_alpha


st.sidebar.title("🏛️ OpenQuant v8.0")
st.sidebar.caption(
    f"Loaded Database: **{len(df_strats):,} Quantitative Strategies**"
)
start_yr = st.sidebar.slider("Backtest Start Year", 2010, 2023, 2015)
min_score = st.sidebar.slider("Min OpenQuant Alpha Score", 40, 90, 55)

tab1, tab2 = st.tabs([
    f"🎯 Interactive Screener ({len(df_strats):,} Strategies)",
    "📥 Bulk Text / HTML Strategy Importer",
])

with tab1:
  st.subheader(
      "🔍 Click Any Strategy Row Below to Load Its Literature, Score Breakdown"
      " & Live Backtest"
  )
  f_col1, f_col2 = st.columns(2)
  search_q = f_col1.text_input(
      "Search by Title, ID, Market, or Factor (e.g., #0850, crypto, carry,"
      " machine learning):",
      "",
  ).lower()
  reb_f = f_col2.multiselect(
      "Filter Rebalancing:",
      df_strats["Reb"].unique().tolist(),
      default=df_strats["Reb"].unique().tolist(),
  )

  view_df = df_strats[
      (df_strats["OQ_Score"] >= min_score) & (df_strats["Reb"].isin(reb_f))
  ].copy()
  if search_q:
    view_df = view_df[
        view_df["Title"].astype(str).str.lower().str.contains(search_q)
        | view_df["Keywords"].astype(str).str.lower().str.contains(search_q)
        | view_df["ID"].astype(str).str.lower().str.contains(search_q)
        | view_df["Markets"].astype(str).str.lower().str.contains(search_q)
    ]
  view_df = view_df.reset_index(drop=True)

  event = st.dataframe(
      view_df[[
          "ID",
          "Title",
          "Rating",
          "OQ_Score",
          "Reb",
          "Markets",
          "Paper_Ret",
          "Paper_Vol",
          "Paper_Sharpe",
          "Keywords",
      ]],
      use_container_width=True,
      hide_index=True,
      on_select="rerun",
      selection_mode="single-row",
  )

  selected_idx = (
      event.selection.rows[0]
      if (event and event.selection and event.selection.rows)
      else 0
  )
  if not view_df.empty:
    sel_row = view_df.iloc[selected_idx]
    st.markdown("---")
    st.title(
        f"{sel_row['ID']}: {sel_row['Title']}  |  Grade: {sel_row['Rating']}"
        f" ({sel_row['OQ_Score']}/100)"
    )

    assets = [x.strip() for x in str(sel_row["Assets"]).split(",")]
    pr, badge = get_data(tuple(assets), start_yr)
    bt, w_df, strat_beta, strat_alpha = run_bt(
        pr, sel_row["Type"], assets, reb_freq=sel_row["Reb"]
    )

    s1, s2, s3, s4, s5, s6 = st.columns(6)
    s1.metric(
        "OpenQuant Alpha Score",
        f"{sel_row['OQ_Score']} / 100",
        f"Grade {sel_row['Rating']}",
    )
    s2.metric("Source Paper Return", f"{sel_row['Paper_Ret']}% p.a.")
    s3.metric("Source Paper Volatility", f"{sel_row['Paper_Vol']}% p.a.")
    s4.metric("Paper Sharpe Ratio", f"{sel_row['Paper_Sharpe']}")
    s5.metric(
        "Realized Market Beta (β)",
        f"{strat_beta:.2f}",
        "Risk-Matched Benchmark",
    )
    s6.metric(
        "Realized Annual Alpha (α)",
        f"{strat_alpha:+.2f}% p.a.",
        "vs. Beta Benchmark",
    )

    st.subheader("📚 Foundational Research & Related Literature")
    ac1, ac2 = st.columns(2)
    with ac1:
      st.info(f"""
            **📌 Source Study:**  
            **{sel_row['Paper']}**  
            *Factor Tags:* `{sel_row['Keywords']}`  
            🔗 **[Search Academic Paper (SSRN / Google Scholar)]({sel_row['Paper_URL']})**  
            🔗 **[View Strategy Specification on Quantpedia]({sel_row['QP_URL']})**
            """)
    with ac2:
      st.markdown("**🌐 Related Working Papers (Live arXiv Feed):**")
      rel_papers = fetch_related_papers(sel_row["Title"], sel_row["Keywords"])
      if rel_papers:
        for cp in rel_papers:
          with st.expander(f"📄 {cp['title']} ({cp['date']})"):
            st.caption(f"Authors: {cp['authors']}")
            st.write(cp["abstract"])
            st.markdown(
                f"🔗 **[Abstract]({cp['url']})** | **[Download"
                f" PDF]({cp['pdf']})**"
            )
      else:
        st.caption("Click any row to query related working papers.")

    # CHART 1: CUMULATIVE RETURN VS BETA-EQUIVALENT BENCHMARK
    st.subheader(
        f"📈 Cumulative Performance ({', '.join(assets)}) — {badge}"
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=bt.index,
            y=bt["Strategy"],
            name=f"{sel_row['ID']} Strategy ({sel_row['Reb']} Rebalance)",
            line=dict(color="#10B981", width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=bt.index,
            y=bt["Beta_Bench"],
            name=f"Beta-Equivalent Benchmark (β = {strat_beta:.2f})",
            line=dict(color="#F59E0B", width=2.5, dash="dot"),
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=390,
        yaxis_title="Portfolio Value ($10,000 Initial)",
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # CHART 2: UNSTACKED PORTFOLIO WEIGHTS & DRIFT OVER TIME (ANCHORED TO 0%)
    st.subheader(
        f"⚖️ Portfolio Weights & Drift Over Time ({sel_row['Reb']} Rebalancing"
        " — Unstacked Relative to 0%)"
    )
    fig_w = go.Figure()

    palette = [
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#EC4899",
        "#A855F7",
        "#06B6D4",
        "#EAB308",
    ]
    for idx, col in enumerate(w_df.columns):
      is_cash = col == "Cash (T-Bills)"
      fig_w.add_trace(
          go.Scatter(
              x=w_df.index,
              y=w_df[col] * 100.0,
              mode="lines",
              name=col,
              line=dict(
                  color="#64748B" if is_cash else palette[idx % len(palette)],
                  width=1.5 if is_cash else 2.2,
                  dash="dot" if is_cash else "solid",
              ),
          )
      )

    fig_w.add_hline(
        y=0,
        line_dash="solid",
        line_color="#FFFFFF",
        line_width=1.5,
        annotation_text="0% Baseline",
        annotation_position="bottom right",
    )

    fig_w.update_layout(
        template="plotly_dark",
        height=350,
        yaxis_title="Portfolio Weight (%)",
        yaxis_ticksuffix="%",
        yaxis=dict(range=[-5, 105]),
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0
        ),
    )
    st.plotly_chart(fig_w, use_container_width=True)

with tab2:
  st.subheader(
      "📥 Upload Your 'Untitled document.txt' (or Quantpedia HTML) to Import"
      " All 1,300+ Strategies"
  )
  uploaded_file = st.file_uploader(
      "Upload 'Untitled document.txt' or 'Screener - Quantpedia.html'",
      type=["txt", "html", "htm"],
  )
  if uploaded_file is not None:
    raw_content = uploaded_file.read().decode("utf-8", errors="ignore")
    if uploaded_file.name.endswith(".txt"):
      new_rows = parse_quantpedia_raw_text(raw_content)
      new_df = pd.DataFrame(new_rows)
      new_df.to_csv(CSV_FILE, index=False)
      st.success(
          f"✅ Parsed and saved {len(new_df):,} strategies into"
          f" `{CSV_FILE}`! Refresh or switch to Tab 1."
      )
    else:
      matches = re.findall(
          r'#(0\d{3})</div>.*?href="(https://quantpedia\.com/strategies/[^"]+)">([^<]+)</a>',
          raw_content,
      )
      st.success(f"Found {len(matches)} strategy rows inside uploaded HTML!")
      for m_id, m_url, m_title in matches:
        st.write(f"**#{m_id}**: [{m_title}]({m_url})")
