import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ページの設定
st.set_page_config(
    page_title="オリンピック記録",
    layout="wide",
    initial_sidebar_state="expanded",
)

# タイトル
st.title("オリンピック記録紹介ページ")

# データの読み込み
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# データの読み込み
try:
    with open("data.csv", "rb") as csv_file:
        df = pd.read_csv(csv_file)
except FileNotFoundError:
    st.error("data.csv ファイルが見つかりません。ファイルが存在することを確認してください。")
    st.stop()

if df is not None:

    # データの前処理
    # 'Medal'がNAでない行のみを対象とする
    df = df.dropna(subset=['Medal'])

    # メダルの重複を排除
    # 同じYear、Sport、Event、Medal、Teamの組み合わせを一意とみなす
    df_unique = df.drop_duplicates(subset=['Year', 'Sport', 'Event', 'Medal', 'Team'])

    # サイドバーに国を選択するセレクトボックスを追加
    st.sidebar.header("フィルター")
    countries = df_unique['Team'].unique()
    selected_country = st.sidebar.selectbox("国を選択してください", sorted(countries))

    # 選択された国のデータを抽出
    country_df = df_unique[df_unique['Team'] == selected_country]

    # 季節がSummerのデータ
    country_summer_df = country_df[country_df['Season'] == 'Summer']

    st.header("1. 夏季オリンピックのメダル推移（個数・割合）")

    # 年ごとの選択国のメダル数を集計
    medals_per_year = country_summer_df.groupby('Year')['Medal'].count().reset_index()
    medals_per_year = medals_per_year.sort_values('Year')

    # 各年の総メダル数を集計（全国）
    # 全体の重複を排除したデータを使用
    total_medals_per_year = df_unique[df_unique['Season'] == 'Summer'].groupby('Year')['Medal'].count().reset_index()
    total_medals_per_year = total_medals_per_year.sort_values('Year')

    # メダルの割合を計算
    merged_df = pd.merge(medals_per_year, total_medals_per_year, on='Year', suffixes=('_Country', '_Total'))
    merged_df['Medal_Percentage'] = (merged_df['Medal_Country'] / merged_df['Medal_Total']) * 100

    # 選択ボックスで表示タイプを選択
    display_option = st.radio(
        "表示形式を選択してください",
        ('個数', '割合'),
        horizontal=True
    )

    # 折れ線グラフの描画
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    if display_option == '個数':
        ax1.plot(merged_df['Year'], merged_df['Medal_Country'], marker='o', linestyle='-', color='blue', label='メダル数')
        ax1.set_ylabel('メダル数', color='blue')
        ax1.set_title(f'{selected_country} の夏季オリンピックにおけるメダル獲得数の推移')
    else:
        ax1.plot(merged_df['Year'], merged_df['Medal_Percentage'], marker='o', linestyle='-', color='green', label='メダル獲得割合 (%)')
        ax1.set_ylabel('メダル獲得割合 (%)', color='green')
        ax1.set_title(f'{selected_country} の夏季オリンピックにおけるメダル獲得割合の推移')

    ax1.set_xlabel('オリンピック開催年')
    ax1.grid(True)
    ax1.legend()
    st.pyplot(fig1)

    st.header("2. 競技ごとのメダル獲得選手")

    # 競技ごとのメダル獲得選手を表示
    sports = country_summer_df['Sport'].unique()
    if len(sports) > 0:
        selected_sport = st.selectbox("競技を選択してください", sorted(sports))
        sport_df = country_summer_df[country_summer_df['Sport'] == selected_sport]

        if not sport_df.empty:
            st.subheader(f"{selected_sport} におけるメダル獲得選手")
            st.dataframe(sport_df[['Name', 'Event', 'Medal']].reset_index(drop=True))
        else:
            st.write("該当するデータがありません。")
    else:
        st.write("選択された国の夏季オリンピックにおいてメダルを獲得した競技がありません。")

    st.header("3. オリンピックイヤーごとのメダル獲得選手")

    # オリンピックイヤーを選択
    years = country_summer_df['Year'].unique()
    if len(years) > 0:
        selected_year = st.selectbox("オリンピック開催年を選択してください", sorted(years))
        year_df = country_summer_df[country_summer_df['Year'] == selected_year]

        if not year_df.empty:
            st.subheader(f"{selected_year}年のメダル獲得選手")
            st.dataframe(year_df[['Name', 'Sport', 'Event', 'Medal']].reset_index(drop=True))
        else:
            st.write("該当するデータがありません。")
    else:
        st.write("選択された国の夏季オリンピックにおいてメダルを獲得した年がありません。")
