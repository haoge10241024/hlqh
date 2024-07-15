import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import akshare as ak
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.font_manager as fm

# 尝试查找系统内的中文字体
font_path = None
for font in fm.findSystemFonts(fontpaths=None, fontext='ttf'):
    if 'SimHei' in font or 'SimSun' in font or 'MSYH' in font:
        font_path = font
        break

# 设置字体和图表属性
if font_path:
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
else:
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 尝试使用黑体
plt.rcParams['axes.unicode_minus'] = False

# Streamlit 页面配置
st.set_page_config(page_title="期货信息获取", layout="wide")

# 标题
st.title("期货信息获取 -- created by 恒力期货上海分公司")

# 获取期货新闻资讯
st.header("期货资讯查询")
news_commodity = st.selectbox("选择品种", ["全部", "要闻", "VIP", "财经", "铜", "铝", "铅", "锌", "镍", "锡", "贵金属", "小金属"])
news_num = st.number_input("查看的新闻数量", min_value=1, max_value=100, value=10, key="news_num")
if st.button("获取新闻资讯"):
    try:
        news_df = ak.futures_news_shmet(symbol=news_commodity)
        news_df = news_df.tail(news_num)
        st.write(news_df)
    except KeyError as e:
        st.error(f"Error fetching news data for {news_commodity}: {e}")

# 获取期限结构图
st.header("期限结构图")
structure_commodity = st.text_input("输入品种名称（例如：沪铜）", value="沪铜", key="structure_commodity")
structure_days = st.number_input("查看的天数(建议30日以内)", min_value=1, max_value=30, value=30, key="structure_days")
if st.button("获取期限结构图"):
    output_filename = f"{structure_commodity}_期限结构.png"
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

            all_symbols are sorted(set(all_symbols))

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

            dates are all_data.index.unique()
            num_dates are len(dates)
            num_cols are 3  # 调整为3列
            num_rows are (num_dates + num_cols - 1) // num_cols

            fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 6 * num_rows), sharex=False, sharey=False)
            axes are axes.flatten()

            for i, current_date in enumerate(dates):
                ax are axes[i]
                date_str are current_date.strftime('%Y-%m-%d')
                prices_on_date are all_data.loc[current_date]
                
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
st.header("期货库存查询")
inventory_commodity = st.text_input("输入品种名称（例如：沪铜）", value="沪铜", key="inventory_commodity")
if st.button("获取期货库存"):
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
st.header("基差情况查询")
basis_commodity = st.text_input("输入品种代码（例如：CU）", value="CU", key="basis_commodity")
basis_start_date = st.date_input("起始日期", datetime.now() - timedelta(days=30), key="basis_start_date")
basis_end_date = st.date_input("结束日期", datetime.now(), key="basis_end_date")
if st.button("获取基差情况"):
    try:
        basis_df = ak.futures_spot_price_daily(
            start_day=basis_start_date.strftime("%Y%m%d"), 
            end_day=basis_end_date.strftime("%Y%m%d"), 
            vars_list=[basis_commodity]
        )
        if basis_df.empty:
            st.warning("没有找到相关数据，请检查输入的日期范围和品种是否正确。")
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
st.header("K线图")
kline_commodity = st.text_input("输入品种合约代码（例如：CU0）", value="CU0", key="kline_commodity")
kline_start_date = st.date_input("起始日期", datetime.now() - timedelta(days=30), key="kline_start_date")
kline_end_date = st.date_input("结束日期", datetime.now(), key="kline_end_date")
if st.button("获取K线图"):
    try:
        kline_data = ak.futures_main_sina(symbol=kline_commodity, start_date=kline_start_date.strftime("%Y%m%d"), end_date=kline_end_date.strftime("%Y%m%d"))
        if kline_data.empty:
            st.warning("没有找到相关数据，请检查输入的日期范围和品种是否正确。")
        else:
            st.write(f"列名: {kline_data.columns.tolist()}")  # 打印列名以进行调试
            kline_data.rename(columns={'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
            kline_data['Date'] = pd.to_datetime(kline_data['Date'])
            kline_data.set_index('Date', inplace=True)
            kline_chart_path = f"{kline_commodity}_kline_chart.png"
            mpf.plot(kline_data, type='candle', volume=True, style='charles', title=f'{kline_commodity} K-line Chart', savefig=kline_chart_path)
            st.image(kline_chart_path)
    except KeyError as e:
        st.error(f"Error fetching or plotting K-line data for {kline_commodity}: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
