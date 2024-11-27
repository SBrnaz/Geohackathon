# streamlit_app.py
import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import missingno as msno
import matplotlib.pyplot as plt
from io import StringIO

# Load the different CSV files
st.title("Well Data Analysis Dashboard")

# Base path for well data
official_files_path = "./Data/Wells/Official Files"

# Load the CSV files
collar_file = os.path.join(official_files_path, "Wells_Collar.csv")
geology_file = os.path.join(official_files_path, "Wells_Geology.csv")
geology_strat_simpl_file = os.path.join(official_files_path, "Wells_Geology_StratSimpl.csv")
las_points_file = os.path.join(official_files_path, "Wells_LAS_Points.csv")
survey_dip_file = os.path.join(official_files_path, "Wells_Survey_Dip.csv")

# Read the CSV files into Pandas DataFrames
collar_df = pd.read_csv(collar_file)
geology_df = pd.read_csv(geology_file, encoding='latin1')
geology_strat_simpl_df = pd.read_csv(geology_strat_simpl_file)
las_points_df = pd.read_csv(las_points_file)
survey_dip_df = pd.read_csv(survey_dip_file)

# Display datasets
def display_dataset(dataframe, title):
    st.subheader(title)
    st.dataframe(dataframe.head())

# Display header of the datasets
display_dataset(collar_df, "Collar Dataset")
display_dataset(geology_df, "Geology Dataset")
display_dataset(geology_strat_simpl_df, "Simplified Geology Dataset")
display_dataset(las_points_df, "LAS Points Dataset")
display_dataset(survey_dip_df, "Survey Dip Dataset")

# LAS Summary
las_summary = pd.DataFrame({
    'Variable': [
        'AC', 'CAL', 'CN', 'DEN', 'depth', 'GR', 'holeid', 'PERM', 'PF', 'POR',
        'PORT', 'PORW', 'R16', 'R64', 'RD', 'RLML', 'RNML', 'SP', 'TEMP'
    ],
    'Description': [
        'Acoustic log (travel time)',
        'Caliper log (borehole diameter)',
        'Compensated Neutron log (neutron porosity)',
        'Bulk Density (g/cc)',
        'Depth of measurement in meters',
        'Gamma Ray (API units)',
        'Well identifier',
        'Permeability (mD)',
        'Formation factor (resistivity factor)',
        'Porosity (%)',
        'Total porosity (%)',
        'Water-filled porosity (%)',
        'Resistivity at 16 inches (ohm-m)',
        'Resistivity at 64 inches (ohm-m)',
        'Deep resistivity (ohm-m)',
        'Laterolog medium resistivity (ohm-m)',
        'Neutron-medium resistivity (ohm-m)',
        'Spontaneous Potential (mV)',
        'Temperature (\u00b0C)'
    ]
})

# Display LAS Summary as a table
st.subheader("Summary of LAS Dataset")
st.dataframe(las_summary)

# Interactive plot of missing data for each variable in the LAS dataset
def plot_missing_data():
    fig, ax = plt.subplots()
    msno.matrix(las_points_df, ax=ax)
    st.pyplot(fig)

st.subheader("Missing Data Overview for LAS Points Dataset")
if st.button("Show Missing Data Plot"):
    plot_missing_data()

# Plot missing data for each well
well_id = st.selectbox('Select Well ID to visualize missing data:', las_points_df['holeid'].unique())

def plot_missing_data_for_well(holeid):
    filtered_df = las_points_df[las_points_df['holeid'] == holeid]
    fig, ax = plt.subplots()
    msno.matrix(filtered_df, ax=ax)
    st.pyplot(fig)

if st.button("Show Missing Data for Selected Well"):
    plot_missing_data_for_well(well_id)

# Simplified Stratigraphy Visualization
st.subheader("Simplified Stratigraphy for Wells (Interactive)")
formations = geology_strat_simpl_df['Strat_Simplified_Viro'].unique()
colors = plt.cm.get_cmap('tab20', len(formations))
fig = go.Figure()
for idx, well_id in enumerate(geology_strat_simpl_df['WellID'].unique()):
    well_strat = geology_strat_simpl_df[geology_strat_simpl_df['WellID'] == well_id]
    for _, row in well_strat.iterrows():
        color_index = list(formations).index(row['Strat_Simplified_Viro'])
        fig.add_trace(go.Bar(
            x=[row['To'] - row['From']],
            y=[well_id],
            base=row['From'],
            orientation='h',
            marker=dict(color=f'rgba({colors(color_index)[0]*255},{colors(color_index)[1]*255},{colors(color_index)[2]*255},1.0)'),
            name=row['Strat_Simplified_Viro']
        ))
fig.update_layout(
    xaxis_title='Depth (m)',
    yaxis_title='Well ID',
    title='Simplified Stratigraphy for Wells',
    barmode='stack',
    showlegend=True
)
st.plotly_chart(fig)

# Interactive visualization of LAS variables
variables = las_points_df.columns.tolist()
variables.remove('holeid')  # Remove the well identifier column
variables.remove('depth')  # Remove the depth column as it will be the x-axis

st.subheader("Interactive Visualization of LAS Profiles")
selected_variable = st.selectbox('Select Variable to Plot:', variables)

if st.button("Show LAS Profile Plot"):
    fig = px.line(
        las_points_df,
        x='depth',
        y=selected_variable,
        color='holeid',
        title=f'Profiles of {selected_variable} for Wells',
        labels={
            'depth': 'Depth (m)',
            selected_variable: selected_variable,
            'holeid': 'Well Name'
        }
    )
    fig.update_layout(
        xaxis_title='Depth (m)',
        yaxis_title=selected_variable,
        legend_title='Well Name'
    )
    st.plotly_chart(fig)
