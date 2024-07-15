import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import akshare as ak
import matplotlib.pyplot as plt
import mplfinance as mpf

# Streamlit 页面配置
st.set_page_config(page_title="Futures Information Retrieval", layout="wide")

# 标题
st.title("Futures Information Retrieval -- created by 恒力期货上海分公司")

# 获取期货新闻资讯
st.header("Futures News")
news_commodity = st.selectbox("Select Commodity", ["全部", "要闻", "VIP", "财经", "铜", "铝", "铅", "锌", "镍", "锡", "贵金属", "小金属"])
news_num = st.number_input("Number of News to Display", min_value=1, max_value=100, value=10)
if st.button("Retrieve News"):
    try:
        news_df = ak.futures_news_shmet(symbol=news_commodity)
        news_df = news_df.tail(news_num)
        st.write(news_df)
    except KeyError as e:
        st.error(f"Error fetching news data for {news_commodity}: {e}")

# 获取期限结构图
st.header("Term Structure Chart")
structure_commodity = st.text_input("Enter Commodity Name (e.g., SHFE Copper)", value="SHFE Copper", key="structure_commodity")
structure_days = st.number_input("Number of Days to View (Recommended within 30 days)", min_value=1, max_value=30, value=30)
if st.button("Retrieve Term Structure Chart"):
    output_filename = f"{structure_commodity}_term_structure.png"
    try:
        def fetch_and_plot_futures_data(commodity_name, output_filename):
            continuous_contracts = [
                "V0", "P0", "B0", "M0", "I0", "JD0", "L0", "PP0", "FB0", "BB0", "Y0",
                "C0", "A0", "J0", "JM0", "CS0", "EG0", "RR0", "EB0", "PG0", "LH0",
                "TA0", "OI0", "RS0", "RM0", "WH0", "JR0", "SR0", "CF0", "RI0", "MA0",
                "FG0", "LR0", "SF0", "SM0", "CY0", "AP0", "CJ0", "UR0", "SA0", "PF0",
                "PK0", "SH0", "PX0", "FU0", "SC0", "AL0", "RU0", "ZN0", "CU0", "AU0",
                "RB0", "WR0", "PB0", "AG0", "BU0", "HC0", "SN0", "NI0", "SP0", "NR0",
                "SS0", "LU0", "BC0", "AO0", "BR0", "EC0", "IF0", "TF0", "IH0", "IC0",
                "TS0", "IM0", "SI0", "LC0"
            ]

            all_symbols = []

            try:
                futures_zh_realtime_df = ak.futures_zh_realtime(symbol=commodity_name)
                symbols = futures_zh_realtime_df['symbol'].tolist()
                all_symbols.extend([s for s in symbols if s not in continuous_contracts])
            except Exception as e:
                st.error(f"Error fetching realtime data for {commodity_name}: {e}")
                return

            all_symbols = sorted(set(all_symbols))

            symbol_close_prices = {}

            end_date = datetime.now()
            start_date = end_date - timedelta(days=structure_days)  # 获取数据的天数

            for symbol in all_symbols:
                try:
                    futures_zh_daily_sina_df = ak.futures_zh_daily_sina(symbol=symbol)
                    futures_zh_daily_sina_df['date'] = pd.to_datetime(futures_zh_daily_sina_df['date'])
                    recent_month_df = futures_zh_daily_sina_df[(futures_zh_daily_sina_df['date'] >= start_date) & (futures_zh_daily_sina_df['date'] <= end_date)]
                    symbol_close_prices[symbol] = recent_month_df.set_index('date')['close']
                except Exception as e:
                    st.error(f"Error fetching daily data for {symbol}: {e}")

            all_data = pd.DataFrame(symbol_close_prices)

            dates = all_data.index.unique()
            num_dates = len(dates)
            num_cols = 3  # 调整为3列
            num_rows = (num_dates + num_cols - 1) // num_cols

            fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 6 * num_rows), sharex=False, sharey=False)
            axes = axes.flatten()

            for i, current_date in enumerate(dates):
                ax = axes[i]
                date_str = current_date.strftime('%Y-%m-%d')
                prices_on_date = all_data.loc[current_date]
                
                ax.plot(prices_on_date.index, prices_on_date.values, marker='o')
                ax.set_title(date_str)
                ax.set_xticks(range(len(prices_on_date.index)))
                ax.set_xticklabels(prices_on_date.index, rotation=45)
                ax.set_ylabel('')
                ax.set_xlabel('')

            for j in range(i + 1, len(axes)):
                fig.delaxes(axes[j])

            plt.tight_layout()
            plt.savefig(output_filename, dpi=300)
            plt.show()

        fetch_and_plot_futures_data(structure_commodity, output_filename)
        st.image(output_filename)
    except Exception as e:
        st.error(f"Error generating futures structure chart: {e}")

# 获取期货库存
st.header("Futures Inventory")
inventory_commodity = st.text_input("Enter Commodity Name (e.g., SHFE Copper)", value="SHFE Copper", key="inventory_commodity")
if st.button("Retrieve Futures Inventory"):
    try:
        inventory_df = ak.futures_inventory_em(symbol=inventory_commodity)
        st.write(inventory_df)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(inventory_df['date'], inventory_df['inventory'], marker='o')
        ax.set_title(f'{inventory_commodity} Inventory')
        ax.set_xlabel('Date')
        ax.set_ylabel('Inventory')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    except KeyError as e:
        st.error(f"Error fetching inventory data for {inventory_commodity}: {e}")

# 获取基差情况
st.header("Basis Situation")
basis_commodity = st.text_input("Enter Commodity Code (e.g., CU)", value="CU", key="basis_commodity")
basis_start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
basis_end_date = st.date_input("End Date", datetime.now())
if st.button("Retrieve Basis Situation"):
    try:
        basis_df = ak.futures_spot_price_daily(
            start_day=basis_start_date.strftime("%Y%m%d"), 
            end_day=basis_end_date.strftime("%Y%m%d"), 
            vars_list=[basis_commodity]
        )
        if basis_df.empty:
            st.warning("No data found, please check the date range and commodity.")
        else:
            st.write(basis_df)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(basis_df['date'], basis_df['spot_price'], marker='o', label='Spot Price')
            ax.plot(basis_df['date'], basis_df['dominant_contract_price'], marker='o', label='Main Futures Price')
            ax.set_title(f'{basis_commodity} Basis Situation')
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
    except Exception as e:
        st.error(f"Error fetching basis data: {e}")

# 获取K线图
st.header("K-line Chart")
kline_commodity = st.text_input("Enter Commodity Contract Code (e.g., CU0)", value="CU0", key="kline_commodity")
kline_start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
kline_end_date = st.date_input("End Date", datetime.now())
if st.button("Retrieve K-line Chart"):
    try:
        kline_data = ak.futures_main_sina(symbol=kline_commodity, start_date=kline_start_date.strftime("%Y%m%d"), end_date=kline_end_date.strftime("%Y%m%d"))
        if kline_data.empty:
            st.warning("No data found, please check the date range and commodity.")
        else:
            kline_data.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
            kline_data['Date'] = pd.to_datetime(kline_data['Date'])
            kline_data.set_index('Date', inplace=True)
            kline_chart_path = f"{kline_commodity}_kline_chart.png"
            mpf.plot(kline_data, type='candle', volume=True, style='charles', title=f'{kline_commodity} K-line Chart', savefig=kline_chart_path)
            st.image(kline_chart_path)
    except KeyError as e:
        st.error(f"Error fetching or plotting K-line data for {kline_commodity}: {e}")
