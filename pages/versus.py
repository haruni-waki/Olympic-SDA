import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ページの設定
st.set_page_config(
    page_title="国比較 - レーダーチャート",
    layout="wide",
)

# タイトル
st.title("国別金メダル獲得割合比較 - レーダーチャート")

# データの読み込み
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

# データの読み込み
try:
    df = load_data("data.csv")
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

    # 季節がSummerのデータ
    summer_df = df_unique[df_unique['Season'] == 'Summer']

    # 金メダルのみにフィルタリング
    gold_df = summer_df[summer_df['Medal'] == 'Gold']

    # ジャンルごとのスポーツ分類
    category_mapping = {
        'Swimming': '水泳',
        'Athletics': '陸上競技',
        'Wrestling': '戦闘競技',
        'Fencing': '戦闘競技',
        'Judo': '戦闘競技',
        'Boxing': '戦闘競技',
        'Taekwondo': '戦闘競技',
        'Karate': '戦闘競技',
        'Modern Pentathlon': '戦闘競技',
        'Handball': '球技',
        'Football': '球技',
        'Basketball': '球技',
        'Volleyball': '球技',
        'Water Polo': '球技',
        'Baseball': '球技',
        'Softball': '球技',
        'Ice Hockey': '球技',
        'Field Hockey': '球技',
        'Rugby': '球技',
        'Equestrian': '乗り物競技',
        'Canoeing': '乗り物競技',
        'Cycling': '乗り物競技',
        'Rowing': '乗り物競技',
        'Sailing': '乗り物競技',
        'Shooting': '乗り物競技',
        'Archery': 'その他',
        'Artistic Gymnastics': 'その他',
        'Rhythmic Gymnastics': 'その他',
        'Triathlon': 'その他',
        'Diving': 'その他',
        'Synchronized Swimming': 'その他',
        'Table Tennis': 'その他',
        'Badminton': 'その他',
        'Tennis': 'その他',
        'Golf': 'その他',
        'Other Sports': 'その他'
        # 必要に応じて追加
    }

    # ジャンルごとのメダル数を集計する関数
    def aggregate_medals(df, mapping):
        df = df.copy()
        df['Category'] = df['Sport'].map(mapping)
        df['Category'] = df['Category'].fillna('その他')
        category_medals = df.groupby('Category')['Medal'].count()
        # 指定の順序で並べ替え、存在しないカテゴリは0
        category_medals = category_medals.reindex(['水泳', '陸上競技', '戦闘競技', '球技', '乗り物競技'], fill_value=0)
        return category_medals

    # ユーザーに複数の国を選択させる
    st.subheader("国を選択してください")
    countries = gold_df['Team'].unique()
    comparison_countries = st.multiselect(
        "比較する国を選択してください（最大5国まで）",
        options=sorted(countries),
        default=['Japan'],
        max_selections=5
    )

    if len(comparison_countries) < 2:
        st.warning("比較する複数の国を選択してください。最低2国を選択する必要があります。")
    else:
        # ジャンルごとの金メダル数と割合を集計
        medal_data = {}
        for country in comparison_countries:
            country_df = gold_df[gold_df['Team'] == country]
            medals = aggregate_medals(country_df, category_mapping)
            total_gold = medals.sum()
            if total_gold > 0:
                percentage = (medals / total_gold) * 100
            else:
                percentage = pd.Series([0]*5, index=medals.index)
            medal_data[country] = percentage

        # データをレーダーチャート用に準備
        categories = ['水泳', '陸上競技', '戦闘競技', '球技', '乗り物競技']
        N = len(categories)

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles += angles[:1]  # 完全な円を描くために最初の角度を追加

        # レーダーチャートの描画
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        # 色の設定
        colors = plt.cm.get_cmap('tab10', len(comparison_countries))

        for idx, country in enumerate(comparison_countries):
            values = medal_data[country].tolist()
            values += values[:1]
            ax.plot(angles, values, linewidth=2, linestyle='solid', label=country, color=colors(idx))
            ax.fill(angles, values, alpha=0.25, color=colors(idx))

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)

        # Y軸の設定
        ax.set_rlabel_position(30)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=10)

        plt.title(f'国別ジャンルごとの金メダル獲得割合比較', size=15, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

        st.pyplot(fig)
