# %%
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
import os
import branca
import numpy as np
import json
import time


def import_and_merge_geojson(list_of_postcodes):

    data_list = []
    for i in range(len(list_of_postcodes)):
        filepath = os.path.join(BASE_DIR,
                                'data',
                                'geo_data',
                                f'{list_of_postcodes[i]}.geojson')
        if not os.path.exists(filepath):
            f = open(os.path.join(BASE_DIR,
                                  'data',
                                  'geo_data',
                                  '01_blank.geojson'))
        else:
            f = open(filepath)

        data = json.load(f)
        data_list.append(data)

    for i in range(len(data_list)):
        if i == 0:
            bigger_dict = data_list[i]

        else:
            bigger_dict['features'].extend(data_list[i]['features'])

    return bigger_dict


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
    return {'fillOpacity': 0.6,
            'weight': 2,
            'fillColor': "#black" if rank is None else colorscale(rank),
            }


def load_map(postcodes_list):
    
    geojson_data_dict = import_and_merge_geojson(postcodes_list)

    map = folium.Map(tiles="cartodbpositron")    
    folium.GeoJson(geojson_data_dict,
                   style_function=style_function,
                   highlight_function=highlight_func,
                   ).add_to(map)
    map.fit_bounds(map.get_bounds(), padding=(-2, -2))

    st_map = st_folium(map, width=700, height=450)
    print(st_map)


def get_postcodes(council_area):
    list = council_area_postcodes[
        council_area_code_df[council_area]]
    return list


colorscale = branca.colormap.LinearColormap(['#800080',
                                             '#FF0000',
                                             '#FFA500',
                                             '#FFFF00',
                                             '#00FF00']
                                            ).scale(1, 6976)


# BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
BASE_DIR = os.getcwd()

simd_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'postcode_simd.csv'))
simd_series = simd_df.set_index('Postcode')['SIMD2020v2_Rank']

council_areas = pd.read_csv('https://www.opendata.nhs.scot/dataset/9f942fdb-'
                            'e59e-44f5-b534-d6e17229cc7b/resource/967937c4-'
                            '8d67-4f39-974f-fd58c4acfda5/download/ca11_ca19'
                            '.csv')
council_area_code_df = council_areas.set_index('CAName')['CA']
council_area_code_df = council_area_code_df.drop_duplicates()
council_area_names_list = council_area_code_df.index.unique().to_list()
council_area_names_list.insert(0, '')

postcode_lookup_df = pd.read_csv(os.path.join(BASE_DIR,
                                              'data',
                                              'scottish_postcodes_lookup.csv'))
council_area_postcodes = postcode_lookup_df \
    .groupby('RegistrationDistrict2007Code')['PostcodeDistrict'] \
    .apply(lambda x: list(np.unique(x)))

st.set_page_config(layout='wide')
st.title('Interactive Fuel Poverty Map')

requested_council_area = st.selectbox(
    'Which council area would you like to view?',
    council_area_names_list)


# %%
# requested_council_area = 'East Lothian'
if requested_council_area != '':
    # progress_text = "Operation in progress. Please wait."
    # my_bar = st.progress(0, text=progress_text)

    # for percent_complete in range(100):
    #     time.sleep(0.05)
    #     my_bar.progress(percent_complete + 1, text=progress_text)

    selected_council_area_postcodes = get_postcodes(requested_council_area)
    load_map(selected_council_area_postcodes)

    st.markdown(f'Showing postcodes {selected_council_area_postcodes} '
                f'that contain homes in council area {requested_council_area}.'
                '\nFor more information on how we calculate our fuel poverty'
                'score, please see [the about section](1_about.py)')
