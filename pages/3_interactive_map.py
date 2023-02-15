# %%
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import StripePattern
import os
import branca
import numpy as np
import json
# import time


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


def add_layer(geojson_data_dict, series, show, name):
    # stripe = StripePattern(angle=45,
    #                        color='grey',
    #                        space_color='white')

    def create_style(feature):
        rank = series.get(feature["properties"]["postcodes"], None)
        if rank is None:
            style_dict = {
                "fillOpacity": 0.5,
                "weight": 0,
                # 'fillPattern': stripe}
                'fillColor': 'black'}
        else:
            style_dict = {
                "fillOpacity": 0.5,
                "weight": 0,
                "fillColor": colorscale(rank)}
        return style_dict

    def amend_highlight(feature):
        rank = series.get(feature["properties"]["postcodes"], None)
        highlight_dict = {'fillOpacity': 0.7,
                          'weight': 2,
                          'fillColor': "#black" if rank is None
                          else colorscale(rank)}
        return highlight_dict

    popup = folium.GeoJsonTooltip(fields=[series.index])

    return folium.GeoJson(geojson_data_dict,
                          style_function=create_style,
                          highlight_function=amend_highlight,
                          show=show,
                          name=name,
                          overlay=False,
                          smooth_factor=1.0)
                        #   tooltip=popup)


def load_map(postcodes_list):

    geojson_data_dict = import_and_merge_geojson(postcodes_list)

    map = folium.Map(tiles=None)
    folium.TileLayer('cartodbpositron', control=False).add_to(map)

    add_layer(geojson_data_dict,
              fpr_series,
              True,
              'Fuel Poverty Risk Rating').add_to(map)

    add_layer(geojson_data_dict,
              simd_series,
              False,
              'Index of Multiple Deprivation').add_to(map)

    add_layer(geojson_data_dict,
              epc_mean_series,
              False,
              'EPC Mean for Postcode').add_to(map)

    map.fit_bounds(map.get_bounds(), padding=(-2, -2))
    folium.LayerControl(collapsed=False).add_to(map)

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
                                            ).scale(1, 100)


BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
# BASE_DIR = os.getcwd()

simd_full_df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'postcode_simd.csv'))
simd_rank_series = simd_full_df.set_index('Postcode')['SIMD2020v2_Rank']
simd_series = (simd_rank_series / simd_rank_series.max())*100
simd_series = round(simd_series).astype(int)

# simd_full_df = pd.read_csv(os.path.join(BASE_DIR, 'data',
#                                        'postcode_simd.csv'))
# simd_rank_series = simd_full_df.set_index('Postcode')['SIMD2020v2_Rank']
# simd_series = round((simd_rank_series / simd_rank_series.max())*100)
# simd_series = simd_series.astype(int)
# simd_series = simd_series.astype(str)
# simd_series = simd_series.astype('int64')

epc_mean_df = pd.read_csv(os.path.join(BASE_DIR,
                                       'data',
                                       'epc_grouped_2012-22.csv'))
epc_mean_series = epc_mean_df.set_index('Postcode')[
    'average_energy_efficiency_rating']
epc_mean_series = round(epc_mean_series).astype(int)

# fpr_series = round((epc_mean_series + simd_series)/2)
# fpr_series = fpr_series.fillna(-1)
# fpr_series = fpr_series.astype(int)
# fpr_series = fpr_series.astype(str)
# fpr_series = fpr_series.astype('int64')
# fpr_series = fpr_series.replace('-1', None)

fpr_series = simd_series.add(epc_mean_series)/2
fpr_series = round(fpr_series).fillna(-1).astype(int).replace(-1, None)

# %%

council_areas = pd.read_csv('https://www.opendata.nhs.scot/dataset/9f942fdb-'
                            'e59e-44f5-b534-d6e17229cc7b/resource/967937c4-'
                            '8d67-4f39-974f-fd58c4acfda5/download/ca11_ca19'
                            '.csv')
council_area_code_df = council_areas.set_index('CAName')['CA']
council_area_code_df = council_area_code_df.drop_duplicates()
council_area_names = council_area_code_df.index.unique()
council_area_names_list = council_area_names.sort_values().to_list()

# %%

postcode_lookup_df = pd.read_csv(os.path.join(BASE_DIR,
                                              'data',
                                              'scottish_postcodes_lookup.csv'))
council_area_postcodes = postcode_lookup_df \
    .groupby('RegistrationDistrict2007Code')['PostcodeDistrict'] \
    .apply(lambda x: list(np.unique(x)))

# st.set_page_config(layout='wide')
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
                f'\nFor more information on how we calculate our fuel poverty'
                f'score, please see [the about section](1_about.py/#our-fuel-'
                f'poverty-risk-rating).')
