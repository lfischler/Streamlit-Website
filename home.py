# %%
import streamlit as st
import pandas as pd

more_smid = ('https://www.gov.scot/collections/scottish-index-of-multiple-'
             'deprivation-2020/')
more_epc = ('https://www.gov.scot/publications/energy-performance-certificates'
            '-introduction/')

st.markdown("""# Fuel Poverty Estimation Calculator
This website helps activists, front-line organisations and local government in
Scotland to target support to those at highest risk of fuel poverty.
""")


# %%
simd_df = pd.read_csv('postcode_simd.csv', index_col='Postcode')
epc_mean_df = pd.read_csv('epc_grouped_2012-22.csv', index_col='Postcode')


# %%
postcode = st.text_input('Postcode (case sensitive)', '')

simd_percentile_score = round((simd_df.loc[postcode, 'SIMD2020v2_Rank']
                               / simd_df['SIMD2020v2_Rank'].max()*100))
epc_score = round(epc_mean_df.loc[postcode,
                  'average_energy_efficiency_rating'])
risk_score = round(((float(simd_percentile_score) + float(epc_score))/2))

# %%

if st.button('Submit'):
    if (postcode in simd_df.index):
        st.markdown('## Postcode Overview')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('**Index of Multiple Deprivation score**')
            st.metric(label="Percentile",
                      value=simd_percentile_score)
            st.markdown(f'[About the SIMD.]({more_smid})')

        with col2:
            st.markdown('**Mean EPC rating for this postcode**')
            st.metric(label="Mean Score",
                      value=epc_score)
            st.markdown(f'[About EPC ratings.]({more_epc})')

        with col3:
            st.markdown('**Estimated fuel poverty risk rating**')
            st.metric(label="Score",
                      value=risk_score)
            st.markdown('[How we calculate this.](1_about.py#fps)')

    else:
        st.write('Sorry. This postcode has not been recognised.')
