# %%
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import os
import branca

def style_function(feature):
        rank = simd_series.get(feature["properties"]["postcodes"], None)
        # rank = 6000
        return {
            "fillOpacity": 0.5,
            "weight": 0,
            "fillColor": "#black" if rank is None else colorscale(rank),
        }


def highlight_func(feature):
    rank = simd_series.get(feature["properties"]["postcodes"], None)
    return {'color': colorscale(rank),
            'fillOpacity': 0.6,
            'weight': 2}

# def load_data(selected):
#     data = pd.read_csv(DATA_URL, nrows=nrows)
#     lowercase = lambda x: str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#     return data


# colorscale = branca.colormap.linear.PuRd_09.scale(1, 6976)
colorscale = branca.colormap.LinearColormap(['#800080',
                                             '#FF0000',
                                             '#FFA500',
                                             '#FFFF00',
                                             '#00FF00']
                                             ).scale(1, 6976)


BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
simd_df = pd.read_csv(os.path.join(BASE_DIR, 'postcode_simd.csv'))
simd_series = simd_df.set_index('Postcode')['SIMD2020v2_Rank']
postcodes_map = os.path.join(BASE_DIR, 'KW16.geojson')

st.set_page_config(layout='wide')
st.title('Interactive Fuel Poverty Map')

option = st.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone'))

if st.button('Submit'):
    m = folium.Map(location=[58.96, -03.29],
                   tiles="cartodbpositron",
                   zoom_start=10)

    # working cloropleth
    # m.choropleth(geo_data='KW16.geojson',
    #              name="choropleth",
    #              data=simd_df,
    #              columns=["Postcode", "SIMD2020v2_Rank"],
    #              key_on=feature["properties"]["postcodes"])
   
    folium.GeoJson(postcodes_map,
                   style_function=style_function,
                   highlight_function=highlight_func
                   ).add_to(m)

    st_data = st_folium(m, width=800)
