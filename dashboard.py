# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 13:48:27 2024

@author: Kelvin
"""

import pandas as pd
import json
import streamlit as st
import matplotlib.pyplot as plt
from streamlit_dynamic_filters import DynamicFilters
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide")

@st.cache_data
def get_raw_data():
    #exploring descendant stats
    col = ['desc_icon','desc_name'
           ,'skillp_name','skillp_icon','skillp_attr','skillp_arche'
           ,'skill1_name','skill1_icon','skill1_attr','skill1_arche'
           ,'skill2_name','skill2_icon','skill2_attr','skill2_arche'
           ,'skill3_name','skill3_icon','skill3_attr','skill3_arche'
           ,'skill4_name','skill4_icon','skill4_attr','skill4_arche']
    df = pd.DataFrame(columns=col)

    file_path = os.getenv('DESCENDANT_JSON_PATH', 'TFD_streamlit_analysis/Data/descendant.json')
    with open(file_path) as f:
        data = json.load(f) 

        
        
    for desc in data:
        obj = {'desc_name': desc['descendant_name']
                    ,'desc_icon':desc['descendant_image_url']
                    ,'skill1_icon':desc['descendant_skill'][0]['skill_image_url']
                        ,'skill1_name':desc['descendant_skill'][0]['skill_name']
                        ,'skill1_attr':desc['descendant_skill'][0]['element_type']
                        ,'skill1_arche':desc['descendant_skill'][0]['arche_type']
                    ,'skill2_icon':desc['descendant_skill'][1]['skill_image_url']
                        ,'skill2_name':desc['descendant_skill'][1]['skill_name']
                        ,'skill2_attr':desc['descendant_skill'][1]['element_type']
                        ,'skill2_arche':desc['descendant_skill'][1]['arche_type']
                    ,'skill3_icon':desc['descendant_skill'][2]['skill_image_url']
                        ,'skill3_name':desc['descendant_skill'][2]['skill_name']
                        ,'skill3_attr':desc['descendant_skill'][2]['element_type']
                        ,'skill3_arche':desc['descendant_skill'][2]['arche_type']
                    ,'skill4_icon':desc['descendant_skill'][3]['skill_image_url']
                        ,'skill4_name':desc['descendant_skill'][3]['skill_name']
                        ,'skill4_attr':desc['descendant_skill'][3]['element_type']
                        ,'skill4_arche':desc['descendant_skill'][3]['arche_type']
                    ,'skillp_icon':desc['descendant_skill'][4]['skill_image_url']
                        ,'skillp_name':desc['descendant_skill'][4]['skill_name']
                        ,'skillp_attr':desc['descendant_skill'][4]['element_type']
                        ,'skillp_arche':desc['descendant_skill'][4]['arche_type']}
        stat_type_dict = {}
        
        for item in desc['descendant_stat']:
            for detail in item['stat_detail']:
                stat_type = detail['stat_type']
                stat_value = float(detail['stat_value'])
                if stat_type not in stat_type_dict:
                    stat_type_dict[stat_type] = []
                
                stat_type_dict[stat_type].append(stat_value)
        
        obj.update(stat_type_dict)
        
        test = pd.DataFrame([obj])
        df = pd.concat([df,test], ignore_index=True)
    return df

skill_tab, stat_tab = st.tabs(['Skill','Stat'])
raw = get_raw_data()
raw['Shield Recovery In Combat'][8] = raw['Shield Recovery In Combat'][19]
#skill tab, show and filter by descendants' attributes and elements
with skill_tab:
    col= ['desc_icon','desc_name'
           ,'skillp_name','skillp_icon','skillp_attr','skillp_arche'
           ,'skill1_name','skill1_icon','skill1_attr','skill1_arche'
           ,'skill2_name','skill2_icon','skill2_attr','skill2_arche'
           ,'skill3_name','skill3_icon','skill3_attr','skill3_arche'
           ,'skill4_name','skill4_icon','skill4_attr','skill4_arche']
    display_df = raw[col]
    dynamic_filters = DynamicFilters(display_df, filters=['skillp_attr', 'skill1_attr', 'skill2_attr', 'skill3_attr', 'skill4_attr'])
    dynamic_filters.display_filters(location='columns', num_columns=2, gap='large')
    dynamic_filters.display_df(column_config={'desc_icon':st.column_config.ImageColumn('Icon')
                                    ,'skillp_icon': st.column_config.ImageColumn('Passive')
                                     ,'skill1_icon': st.column_config.ImageColumn('Skill 1')
                                     ,'skill2_icon': st.column_config.ImageColumn('Skill 2')
                                     ,'skill3_icon': st.column_config.ImageColumn('Skill 3')
                                     ,'skill4_icon': st.column_config.ImageColumn('Skill 4')}, hide_index=True, use_container_width=True)
    df_filtered = dynamic_filters.filter_df()
    
    
    
with stat_tab:
    #select descendants to display stats
    select_descendants = raw['desc_name'].unique()
    option = st.selectbox("Select a descendant: ", select_descendants)

    statdf = []
    stat_col = ['Max HP','Max Shield','Shield Recovery In Combat','Max MP','DEF','Shield Recovery Out of Combat']
    for _, row in raw.iterrows():
        descendant_name = row['desc_name']
        for stat in stat_col:
            stat_values = row[stat]
            for level, value in enumerate(stat_values, start=1):
                statdf.append({
                    'Descendant Name': descendant_name,
                    'Stat Name': stat,
                    'Level': level,
                    'Stat Value': value
                })
    result_df = pd.DataFrame(statdf)
    #contains desc icon and radar charts of stat
    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            image = raw[raw['desc_name'] == option]['desc_icon'].values[0]
            st.image(image, width=450)
        with col2:
            fig,ax = plt.subplots()
            max_stat_df = result_df.groupby(['Descendant Name', 'Stat Name'])['Stat Value'].max().reset_index()
            def normalize_and_scale(series, new_min=0, new_max=5):
                min_val = series.min()
                max_val = series.max()
                
                # Avoid division by zero in case of constant values
                if min_val == max_val:
                    return pd.Series([new_max] * len(series))  # All values will be max rating (5)
                
                normalized = (series - min_val) / (max_val - min_val)  # Normalize between 0 and 1
                scaled = normalized * (new_max - new_min) + new_min  # Scale to the range [1, 5]
                
                return scaled.round()
            max_stat_df['Normalized Value'] = max_stat_df.groupby('Stat Name')['Stat Value'].transform(normalize_and_scale)
            pivot_df = max_stat_df.pivot(index='Descendant Name', columns='Stat Name', values='Normalized Value').reset_index()
            
            stats = pivot_df.columns[1:]
# =============================================================================
#             def create_radar_chart(row, stats, title):
#                 num_stats = 6
#                 # Radar chart setup
#                 angles = [n / float(num_stats) * 2 * pi for n in range(num_stats)]
#                 angles += angles[:1]  # Complete the loop
#             
#                 fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
#                 
#                 # Plot the data
#                 row = row.iloc[0]
#                 values = row[1:].values.tolist()  # Exclude 'Descendant Name'
# 
#                 # Handling zero values: Replace zeros with a small value (e.g., 1)
#                 values = [max(v, 1) for v in values]
#                 
#                 values += values[:1]  # Complete the loop
#             
#                 ax.fill(angles, values, alpha=0.2)
#                 ax.plot(angles, values, linewidth=1)
#                 
#                 # Set labels for each axis
#                 ax.set_xticks(angles[:-1])
#                 ax.set_xticklabels(stats)
#                 
#                 # Set the range for the y-axis (1 to 5, as ratings are in this range)
#                 ax.set_yticks([1, 2, 3, 4, 5])
#                 ax.set_ylim(1, 5)
#                 ax.set_yticklabels([])
#                 ax.set_title(title, size=20, y=1.1)
#                 
#                 plt.show()
# =============================================================================
            def create_radar_chart(row, stats, title):
                # Extract the values for the radar chart from the row
                row = row.iloc[0]
                values = row[1:].values.tolist()  # Exclude 'Descendant Name'

                # Create a DataFrame for Plotly
                df = pd.DataFrame({
                    'Stat': stats,
                    'Value': values
                })

                # Create the radar chart using Plotly Express
                fig = px.line_polar(df, r='Value', theta='Stat', line_close=True, title=title)
            
                # Customize the radar chart appearance
                fig.update_traces(fill='toself', line=dict(color='blue'))
                fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5], showticklabels=False)),
                                  showlegend=False,
                                  title=dict(font=dict(size=20)))
            
                return fig
            fig = create_radar_chart(pivot_df[pivot_df['Descendant Name'] == option], stats, title= option)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.plotly_chart(fig)
        
    def stat_by_level_chart(result_df, desc):
        min_max_df = result_df.groupby(['Stat Name', 'Level'])['Stat Value'].agg(['min', 'max']).reset_index()
        color_map = {
                'Max HP': '#d62728',
                'Max Shield': '#ff7f0e',
                'Shield Recovery In Combat': '#2ca02c',
                'Max MP': '#1f77b4',
                'DEF': '#FFFDD0',
                'Shield Recovery Out of Combat': '#B9FFF1',
        }
        fig = go.Figure()
    
        for stat_name in result_df['Stat Name'].unique():
            stat_data = result_df[result_df['Stat Name'] == stat_name]
            min_max_data = min_max_df[min_max_df['Stat Name'] == stat_name]
    
            desc_stat_values = stat_data[stat_data['Descendant Name'] == desc].reset_index()
            fig.add_trace(go.Scatter(
                x=desc_stat_values['Level'],
                y=desc_stat_values['Stat Value'],
                mode='lines',
                line=dict(color=color_map[stat_name]),
                name=stat_name
            ))
    
            # Add the fill between the min and max values
            fig.add_trace(go.Scatter(
                x=min_max_data['Level'].tolist() + min_max_data['Level'].tolist()[::-1],
                y=min_max_data['min'].tolist() + min_max_data['max'].tolist()[::-1],
                fill='toself',
                fillcolor=color_map[stat_name],  # Use the same color but with opacity
                line=dict(color='rgba(255,255,255,0)'),  # No border line for the fill area
                opacity=0.2,
                showlegend=False,
                hoverinfo='skip'
            ))
    
        # Customize the layout
        fig.update_layout(
            xaxis_title='Level',
            yaxis_title='Stat Value',
            title='Stat Value by Level',
            legend_title='Stat Name',
            template='plotly_white'  # You can adjust the template
        )
        return fig 
    with st.container():
        fig = stat_by_level_chart(result_df, option)
        st.plotly_chart(fig, use_container_width=True)
    
    def stat_comparison_chart(result_df, desc, stat):
        color_map = {
                'Max HP': '#d62728',

        }
        fig = go.Figure()
        for d in result_df['Descendant Name'].unique():
            stat_data = result_df[result_df['Stat Name'] == stat]
            if d != desc:
                desc_stat_values = stat_data[stat_data['Descendant Name'] == d].reset_index()
                fig.add_trace(go.Scatter(
                    x=desc_stat_values['Level'],
                    y=desc_stat_values['Stat Value'],
                    mode='lines',
                    line=dict(color='white'),
                    opacity=0.1,
                    hoverinfo='skip',
                    name = d))
            else:
                desc_stat_values = stat_data[stat_data['Descendant Name'] == desc].reset_index()
                fig.add_trace(go.Scatter(
                    x=desc_stat_values['Level'],
                    y=desc_stat_values['Stat Value'],
                    mode='lines',
                    line=dict(color='#d62728'),
                    name=desc 
                    ))
        # Customize the layout
        fig.update_layout(
            xaxis_title='Level',
            yaxis_title='Stat Value',
            showlegend = False,
            title='Stat Value compared to other Descendants',
            template='plotly_white'  # You can adjust the template
        )
        return fig
    with st.container():
        stat_option = st.radio('Select stat:' ,stat_col, horizontal=True)
        fig = stat_comparison_chart(result_df, option,stat_option)
        st.plotly_chart(fig, use_container_width=True)


