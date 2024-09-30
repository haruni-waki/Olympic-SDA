import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib_fontja

def display_data(data, title):
    st.write("### "+ title)
    st.write(data)

def calculate_medal_count_by_country(data):
    #使えないデータを消している
    data=data.dropna(subset=["Medal"])
    data=data.groupby(["NOC","Medal"])
    data=data.size().unstack(fill_value=0)
    return data

def calculate_medal_count_by_gender(data):
    data=data.dropna(subset=["Medal"])
    data=data.groupby(["Gender","Medal"])
    data=data.size().unstack(fill_value=0)
    return data

def test(data):
    data=data.dropna(subset=["Medal"])
    data=data.groupby(["Age","Medal"])
    data=data.size().unstack(fill_value=0)
    return data


def visualize_medal_count(medal_count):
    st.write("### メダル数の可視化")
    country=st.selectbox("国を選択してください",medal_count.index)
    medals = medal_count.loc[country]

    fig,ax=plt.subplots()
    medals.plot(kind="bar",ax=ax)
    ax.set_title(f"{country}のメダルの数")
    ax.set_xlabel("メダルの種類")
    ax.set_ylabel("数")

    st.pyplot(fig)

def main():




    #データの読み込みをしている
    st.title("Olympic SDA")
    csv_data=open("data.csv","rb")
    data=pd.read_csv(csv_data)

    #冬を除外（夏のみのデータに）
    data=data[data["Season"]=="Summer"]

    display_data(data, "オリンピックの選手データ")


    medal_data = calculate_medal_count_by_country(data)
    display_data(medal_data, "メダルデータ")

    visualize_medal_count(medal_data)

if __name__=="__main__":
    main()