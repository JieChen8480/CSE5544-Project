# (C) Author: Yuechen Tang, Jingyi Li, Jie Chen
# 
# 2022 Spring: For The Ohio State University, Intro. Data. Vis Lectures
#
# Import libraries
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import altair as alt
import squarify
import matplotlib

# Page setup
st.set_page_config(
    layout="wide"
)

# Import the DEA's pain pill Data
data = pd.read_csv("https://raw.githubusercontent.com/tristatyc/cse5544FinalProject/main/county_annual14.csv")
delaware_data = pd.read_csv("https://raw.githubusercontent.com/JingyiLi9597/CSE5544lab3/main/5544table2.csv")

# Set title for overall trend
st.markdown("<div style = 'background:#e6e6e6'><h3 style = 'font-weight:bold; color:#ac2217'>Overall Trend of Pills in Selectd State from 2006 to 2014</h3></div>", unsafe_allow_html = True)

# Data process for Figure 1
df1 = data.copy()
df1 = df1.drop_duplicates(subset = ['year'])
df2 = data.copy()
df2 = df2.drop_duplicates(subset = ['BUYER_STATE'])
years = df1['year']
states = df2['BUYER_STATE']

# View the country as a whole
mean_num_pills1 = data.groupby('year')['DOSAGE_UNIT'].mean()

# Select one state
option = st.selectbox("Select one state", states)
# Filter the data with the selected state
filter_data = data[data['BUYER_STATE'] == option]
mean_num_pills2 = filter_data.groupby('year')['DOSAGE_UNIT'].mean()
                 
filter_df = pd.DataFrame({'DOSAGE_UNIT_ALL': mean_num_pills1,
                          'DOSAGE_UNIT_STATE': mean_num_pills2})
filter_df = filter_df.reset_index()
filter_df['BUYER_STATE'] = option
filter_df['year'] = filter_df['year'].apply(str)

# Data process for Figure 2
county_df = data.copy()
county_df = county_df[county_df['BUYER_STATE'] == "OH"]
county = county_df['BUYER_COUNTY']

num_by_county = county_df.groupby(['year', 'BUYER_COUNTY']).agg({'DOSAGE_UNIT': ['sum']})
num_by_county.columns = ['DOSAGE_SUM']
num_by_county = num_by_county.reset_index()
num_by_county['DOSAGE_SUM'] = num_by_county['DOSAGE_SUM'].apply(pd.to_numeric, errors = 'coerce')
num_by_county['year'] = num_by_county['year'].apply(pd.to_numeric, errors = 'coerce')

# Data process for Figure 3
p2_data = pd.melt(delaware_data, id_vars = ['manufacturer'], var_name = 'year')
p2_data['value'] = p2_data['value'].apply(pd.to_numeric, errors = 'coerce')
p2_data.rename(columns = {'manufacturer' : 'manufacturer', 'value' : 'dosage_unit'}, inplace = True)


# Interface

# Generate Figure 1

# Line chart of the number of pills of the selected state
line_chart_state = alt.Chart(filter_df).mark_line().encode(
    x = alt.X('year', axis = alt.Axis(title = 'Years')),
    y = alt.Y('DOSAGE_UNIT_STATE', axis = alt.Axis(title = 'Number of Pills')),
    tooltip = ['year', 'DOSAGE_UNIT_STATE'],
    color = alt.value('blue')
).properties(
    title = 'Average Number of Pills Bought in Selected State in Years 2006-2014'
).interactive()

# Scatter plot of the number of pills of the selected state
scatter_plot_state = alt.Chart(filter_df).mark_point().encode(
    x = 'year',
    y = 'DOSAGE_UNIT_STATE',
    tooltip = ['year', 'DOSAGE_UNIT_STATE'],
    color = alt.value('purple')
).interactive()

# Text of the maximum point
max_text = (alt.Chart(filter_df).mark_text(dy = -15, color = 'red').transform_window(
    sort = [alt.SortField('DOSAGE_UNIT_STATE', order = 'descending')], 
    rank = 'rank(DOSAGE_UNIT_STATE)'
).transform_filter(
    alt.datum.rank == 1
).encode(
    x = alt.X('year'),
    y = alt.Y('DOSAGE_UNIT_STATE'),
    text = alt.Text('DOSAGE_UNIT_STATE'))
)

# Text of the minimum point
min_text = (alt.Chart(filter_df).mark_text(dy = -15, color = 'green').transform_window(
    sort = [alt.SortField('DOSAGE_UNIT_STATE', order = 'descending')], 
    rank = 'rank(DOSAGE_UNIT_STATE)'
).transform_filter(
    alt.datum.rank == 9
).encode(
    x = alt.X('year'), 
    y = alt.Y('DOSAGE_UNIT_STATE'), 
    text = alt.Text('DOSAGE_UNIT_STATE'))
)

# Line chart of the number of pills of the whole country
line_chart_all = alt.Chart(filter_df).mark_line(color = '#ac2217').encode(
    x = 'year',
    y = 'DOSAGE_UNIT_ALL',
    size = alt.SizeValue(3),
    tooltip = ['year', 'DOSAGE_UNIT_ALL'],
    color = alt.value('red')
).interactive()

st.altair_chart(line_chart_state + scatter_plot_state + max_text + min_text + line_chart_all, use_container_width = True)

# Set title for figures of Ohio State
st.markdown("<div style = 'background:#e6e6e6'><h3 style = 'font-weight:bold; color:#ac2217'>Pills Buying and Manufacturing Trend in Ohio from 2006 to 2014</h3></div>", unsafe_allow_html = True)

# Generate Figure 2 and Figure 3
chart2, chart3 = st.columns([1.3, 1.5])

# Figure 2
with chart2:
    selected_year = st.select_slider(
        'Select one year',
        options = [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014]
    )
    
    filter_year_df = num_by_county[num_by_county['year'] == selected_year]
    filter_year_df2 = filter_year_df.sort_values(by = 'DOSAGE_SUM', ascending = False)
    filter_year_df2 = filter_year_df2.head(8)

    quantity_pills = filter_year_df2['DOSAGE_SUM']
    labels = filter_year_df2['BUYER_COUNTY']

    cmap = matplotlib.cm.Blues
    min = min(quantity_pills)
    max = max(quantity_pills)
    norm = matplotlib.colors.Normalize(vmin = min, vmax = max)
    colors = [cmap(norm(value)) for value in quantity_pills]

    plt.figure(figsize = (10, 6))
    plt.rc('font', size = 13)
    axis = squarify.plot(sizes = quantity_pills, label = labels,
             color = colors, alpha = 0.7)
    plt.axis('off')
    axis.set_title("The proportion of buying power in each county in Ohio in the selected year")
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    
# Figure 3
with chart3:
    
    # Generate heatmap using altair
    heatmap_2 = alt.Chart(p2_data).mark_rect().encode(
        x = alt.X('manufacturer', title = 'Manufacturers'),
        y = alt.Y('year', title = 'Years'),
        color = alt.Color('dosage_unit', scale = alt.Scale(scheme = 'inferno')),
        tooltip = ['manufacturer', 'year', 'dosage_unit']
    ).properties(
        title = 'The heatmap to show the pills produced by all manufacturers among years in Delaware County',
        width = 1000,
        height = 535
    )

    st.altair_chart(heatmap_2, use_container_width = True)

