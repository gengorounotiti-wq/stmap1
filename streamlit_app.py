import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="九州・中国地方 気温 3D Map", layout="wide")
st.title("九州・中国地方主要都市の現在の気温 3Dカラムマップ")

# 九州＋中国地方の県庁所在地
cities = {
    # --- 九州 ---
    'Fukuoka':    {'lat': 33.5904, 'lon': 130.4017},
    'Saga':       {'lat': 33.2494, 'lon': 130.2974},
    'Nagasaki':   {'lat': 32.7450, 'lon': 129.8739},
    'Kumamoto':   {'lat': 32.7900, 'lon': 130.7420},
    'Oita':       {'lat': 33.2381, 'lon': 131.6119},
    'Miyazaki':   {'lat': 31.9110, 'lon': 131.4240},
    'Kagoshima':  {'lat': 31.5600, 'lon': 130.5580},

    # --- 中国地方 ---
    'Hiroshima':  {'lat': 34.3853, 'lon': 132.4553},
    'Okayama':    {'lat': 34.6551, 'lon': 133.9195},
    'Yamaguchi':  {'lat': 34.1858, 'lon': 131.4714},
    'Tottori':    {'lat': 35.5011, 'lon': 134.2351},
    'Shimane':    {'lat': 35.4723, 'lon': 133.0505},
}

# --- データ取得関数 ---
@st.cache_data(ttl=600)
def fetch_weather_data():
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'

    for city, coords in cities.items():
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'current': 'temperature_2m'
        }
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            weather_info.append({
                'City': city,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'Temperature': data['current']['temperature_2m']
            })
        except Exception as e:
            st.error(f"{city} の取得に失敗しました: {e}")

    return pd.DataFrame(weather_info)

# データ取得
with st.spinner('最新の気温データを取得中...'):
    df = fetch_weather_data()

# 気温を高さに変換（1℃ = 3000m）
df['elevation'] = df['Temperature'] * 3000

# --- レイアウト ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("取得したデータ")
    st.dataframe(df[['City', 'Temperature']], use_container_width=True)

    if st.button('データを更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    st.subheader("3D カラムマップ")

    view_state = pdk.ViewState(
        latitude=33.8,   # 九州＋中国地方の中心付近
        longitude=132.0,
        zoom=5.6,
        pitch=45,
        bearing=0
    )

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=12000,
        get_fill_color='[255, 100, 0, 180]',
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{City}</b><br>気温: {Temperature}°C",
                "style": {"color": "white"}
            }
        )
    )


