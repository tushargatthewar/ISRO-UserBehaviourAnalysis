from flask import Flask, request, jsonify, render_template, redirect
import csv
import os
import pandas as pd
import threading
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from PIL import Image
import random
import plotly.express as px
import folium
from folium.plugins import HeatMap
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
import subprocess  # Import subprocess for running external commands
from zapv2 import ZAPv2 
import ast

app = Flask(__name__)

# Path to the CSV file for storing persisitant Data
overall_csv='overallhomedata.csv'
overall_csv_mapliteuserdata='overall_csv_mapliteuserdata.csv'
overall_csv_homesession='overall_csv_homesession.csv'
overall_csv_2DmapTimespent='overall_csv_2DmapTimespent.csv'
overall_csv_archivetimespent='overall_csv_archivetimespent.csv'
overall_csv_archive_user='overall_csv_archive_user.csv'

#path file for csv for the storing the session data for specific user
CSV_FILE_PATH = 'home_user_activity.csv'
CSV_FILE_PATH_Map= '2DmapTimespent.csv'
CSV_FILE_PATH_Homesession='Homesession.csv'
CSV_FILE_PATH_archive='archive.csv'
csv_file = 'archive_user activity.csv'#in process
CSV_FILE_PATH2 = 'mapLite_user_activity.csv'#lite map user data
SQLMAP_CSV_FILE_PATH = 'sqlmap_results.csv'
ZAP_CSV_FILE_PATH = 'zap_results.csv'

@app.route('/')
def index():
    #complete data collection
    #home page for bhuvan
    return render_template('analyatical.html')

@app.route('/come')
def come():
    
    return render_template('comesoon.html')


@app.route('/tod')
def tod():
    #2d map page
    return render_template('2d.html')

@app.route('/thd')
def thd():
    #3d map page
    return render_template('3d.html')

@app.route('/archive')
def archive():
    #Bhuvan lite page
    return render_template('archive.html')

@app.route('/lite')
def lite():
    #complete data collection
    #Data archive page
    return render_template('lite.html')

@app.route('/map')
def map():
    #Task bar map page
    return render_template('map.html')

def get_client_ip():
    """Retrieve the client's IP address from the request."""
    if request.headers.getlist("X-Forwarded-For"):
        # If behind a proxy, the client's IP is in the first position
        ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip


 #**************************here is the persistant Data******************************#
 #***********************************************************************************#
def overall_homeuserdata():
    if not os.path.exists(overall_csv):
        with open(overall_csv,mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['ip_address',
                'event', 'element', 'timestamp', 'x', 'y', 'page', 
                'relatedElement', 'inputValue', 'location', 
                'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'
            ])
overall_homeuserdata()

def overall_mapliteuserdata():
    if not os.path.exists(overall_csv_mapliteuserdata):
        with open(overall_csv_mapliteuserdata,mode='w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ip_address','event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover']) 

overall_mapliteuserdata()

def overall_archiveuserdata():
    if not os.path.exists(overall_csv_archive_user):
        with open(overall_csv_archive_user, mode='w',newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ip_address','Timestamp', 'Event', 'TimeSpent', 'Link', 'Section'])

overall_archiveuserdata()


def overall_2dmap():
        if not os.path.exists(overall_csv_2DmapTimespent):
            with open(overall_csv_2DmapTimespent,mode='w',newline='') as file:
                writer=csv.writer(file)
                writer.writerow(['ip_address','page', 'timeSpent'])  

overall_2dmap()


def overall_homesession():
    if not os.path.exists(overall_csv_homesession):
        with open(overall_csv_homesession,mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['ip_address','page','timeSpent'])

overall_homesession()


def overall_archivesession():
    if not os.path.exists(overall_csv_archivetimespent):
        with open(overall_csv_archivetimespent,mode='w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['ip_address','page','timeSpent'])

overall_archivesession()



#*************************************Here is the session wise data is Storing******************************************#
#*********************************************************************************************************************#

def initialize_csv():
    """Delete existing CSV file and create a new one with headers."""
    if os.path.exists(CSV_FILE_PATH):
        os.remove(CSV_FILE_PATH)
    
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'])

# Initialize the CSV file
initialize_csv()

#this is  for tarcking data of the maplite 
def initialize_csvmaplite():
    """Delete existing CSV file and create a new one with headers."""
    if os.path.exists(CSV_FILE_PATH2):
        os.remove(CSV_FILE_PATH2)
    
    with open(CSV_FILE_PATH2, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','event', 'element', 'timestamp', 'x', 'y', 'page', 'relatedElement', 'inputValue', 'location', 'destination', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover'])

# Initialize the CSV file
initialize_csvmaplite()



def initialize_csv1():
    """Create a new CSV file if it doesn't exist with appropriate headers."""

    if os.path.exists(CSV_FILE_PATH_Map):
        os.remove(CSV_FILE_PATH_Map)

    # if not os.path.exists(CSV_FILE_PATH_Map):
    with open(CSV_FILE_PATH_Map, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','page', 'timeSpent'])  # CSV Headers

initialize_csv1()

#home ke liye CSV timesspent
def initialize_csvhome():
    """Create a new CSV file if it doesn't exist with appropriate headers."""
    if os.path.exists(CSV_FILE_PATH_Homesession):
        os.remove(CSV_FILE_PATH_Homesession)
    
    #if not os.path.exists(CSV_FILE_PATH_Homesession):
    with open(CSV_FILE_PATH_Homesession, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','page', 'timeSpent'])  # CSV Headers

initialize_csvhome()

#archive ke liye CSV time spent
def initialize_csvarchive():
    """Create a new CSV file if it doesn't exist with appropriate headers."""
    if os.path.exists(CSV_FILE_PATH_archive):
        os.remove(CSV_FILE_PATH_archive)
    
    #if not os.path.exists(CSV_FILE_PATH_archive):
    with open(CSV_FILE_PATH_archive, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','page', 'timeSpent'])  # CSV Headers

initialize_csvarchive()

#lite page ke liye CSV file hain ye wali
def litecsv():
    if os.path.exists(csv_file):
        os.remove(csv_file)
    #if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ip_address','Timestamp', 'Event', 'TimeSpent', 'Link', 'Section'])

litecsv()

@app.route('/track-click', methods=['POST'])
def track_click():
    data = request.json
    
    # Print the data to debug
    #print(f"Received data: {data}")
    client_ip = get_client_ip()
    # Extract data from the JSON request
    event = data.get('event', '')  
    element = data.get('element', '')
    timestamp = data.get('timestamp', '')
    x = data.get('x', '')  # Ensure x is provided       
    y = data.get('y', '')
    page = data.get('page', '')
    relatedElement = data.get('relatedElement', '')
    inputValue = data.get('inputValue', '')
    location = data.get('location', '')
    destination = data.get('destination', '')
    timeSpent = data.get('timeSpent', 0)  # Ensure timeSpent is numeric
    scroll = data.get('scroll', 0)  # New parameter for scroll value
    depth = data.get('depth', 0)  # New parameter for depth
    timeSpentOnHover = data.get('timeSpentOnHover', 0)  # New parameter for hover time
    
    # Write the data to the CSV file, maintaining the original order
    with open(CSV_FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            client_ip,event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    with open(overall_csv,mode='a',newline='') as file:
        writer=csv.writer(file)
        writer.writerow([
            client_ip,event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    return jsonify({'status': 'success'}), 201

@app.route('/archive1', methods=['POST'])
def archive1():
    data = request.json
    
    # Print the data to debug
    #print(f"Received data: {data}")
    client_ip = get_client_ip()
    # Extract data from the JSON request
    event = data.get('event', '')  
    element = data.get('element', '')
    timestamp = data.get('timestamp', '')
    x = data.get('x', '')  # Ensure x is provided
    y = data.get('y', '')
    page = data.get('page', '')
    relatedElement = data.get('relatedElement', '')
    inputValue = data.get('inputValue', '')
    location = data.get('location', '')
    destination = data.get('destination', '')
    timeSpent = data.get('timeSpent', 0)  # Ensure timeSpent is numeric
    scroll = data.get('scroll', 0)  # New parameter for scroll value
    depth = data.get('depth', 0)  # New parameter for depth
    timeSpentOnHover = data.get('timeSpentOnHover', 0)  # New parameter for hover time
    
    # Write the data to the CSV file, maintaining the original order
    with open(CSV_FILE_PATH2, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            client_ip, event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    with open(overall_csv_mapliteuserdata, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            client_ip, event, element, timestamp, x, y, page, 
            relatedElement, inputValue, location, 
            destination, timeSpent, scroll, depth,
            timeSpentOnHover
        ])

    return jsonify({'status': 'success'}),201 


@app.route('/track_activitylite', methods=['POST'])
def track_activitylite():
    activity_data = request.json
    client_ip = get_client_ip()
    event = activity_data.get('event')
    time_spent = activity_data.get('timeSpent', None)
    link = activity_data.get('link', None)
    section = activity_data.get('section', None)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Log activity into CSV file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip,timestamp, event, time_spent, link, section])

    with open(overall_csv_archive_user, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip,timestamp, event, time_spent, link, section])

    

    return jsonify({'status': 'success', 'message': 'Activity recorded successfully'}), 201



@app.route('/track-time', methods=['POST'])
def track_time():
    data = request.json
    client_ip = get_client_ip()
    page = data.get('page', '')
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_Map, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page, time_spent])

    with open(overall_csv_2DmapTimespent, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page, time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201


@app.route('/track-timehome', methods=['POST'])
def track_timehome():
    data = request.json
    client_ip = get_client_ip()
    page = data.get('page', '')
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_Homesession, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])

    with open(overall_csv_homesession, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])


    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201

@app.route('/track_timearchive', methods=['POST'])
def track_timearchive():
    data = request.json
    print(data)
    client_ip = get_client_ip()
    page = data.get('page', '')
    print(page)
    time_spent = data.get('timeSpent', 0)  # Time spent in seconds

    # Log the time spent to the CSV file
    with open(CSV_FILE_PATH_archive, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])

    with open(overall_csv_archivetimespent, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([client_ip, page , time_spent])

    return jsonify({'status': 'success', 'message': 'Time spent recorded successfully'}), 201




#from here dashbaord.py code will start
##################################################################################
########################################################################################################
####################################################################################################################
#################################################################################################################################
################################################################################################################################################
##############################################################################################################################################################

@app.route('/dashboard')
def dashboard():
    # Load CSV data for user activity
    df = pd.read_csv('home_user_activity.csv')

    # Filter only the 'click' events to track navigation
    click_data = df[df['event'] == 'click']
    click_data = click_data[click_data['element'] != 'BUTTON']
    click_data = click_data[click_data['element'] != 'IMG']

    # Create a list for the navigation flow, starting with 'Home'
    navigation_flow = ['Home']
    for _, row in click_data.iterrows():
        navigation_flow.append(row['element'])
        navigation_flow.append('Home')
    if navigation_flow[-1] == 'Home':
        navigation_flow.pop()

    home_data = pd.DataFrame({
        'element': navigation_flow[:-1],
        'next_element': navigation_flow[1:]
    })

    # Define a color palette for the navigation flow (modify colors as needed)
    color_palette = ['#FF5733', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#900C3F', '#581845']
    
    # Function to randomly assign colors from the palette to navigation elements
    color_map = {'Home': '#636EFA'}  # Fixed color for 'Home'
    unique_elements = home_data['element'].unique()
    for element in unique_elements:
        if element != 'Home':
            color_map[element] = random.choice(color_palette)

    # Create a line plot to visualize the flow with mixed colors
    fig_nav = go.Figure()

    # Add lines between each transition with mixed colors
    for i in range(len(home_data)):
        element = home_data.iloc[i]['element']
        next_element = home_data.iloc[i]['next_element']
        color = color_map[element]  # Assign color based on the element
        
        fig_nav.add_trace(go.Scatter(
            x=[i, i+1],
            y=[0, 0],
            mode='lines+markers',
            marker=dict(size=10, color=color),  # Set color for the marker
            line=dict(width=2, color=color),  # Set color for the line
            text=[element, next_element],
            textposition='top center'
        ))

    fig_nav.update_layout(
        title="User Click Navigation Flow (Mixed Colors)",
        xaxis=dict(
            tickvals=list(range(len(home_data)+1)),
            ticktext=navigation_flow,
            title="Navigation Steps"
        ),
        yaxis=dict(
            title="",
            showticklabels=False
        ),
        showlegend=False
    )

    graph_nav_html = pio.to_html(fig_nav, full_html=False)

    # Load and process time spent data
    df1 = pd.read_csv('Homesession.csv')
    df2 = pd.read_csv('archive.csv')
    df3 = pd.read_csv('2DmapTimespent.csv')
    dfs = [df1, df2, df3]
    combined_df = pd.concat(dfs, ignore_index=True)
    if 'page' in combined_df.columns and 'timeSpent' in combined_df.columns:
        combined_df = combined_df[['page', 'timeSpent']]  
    else:
        combined_df.columns = combined_df.columns[:2]  
        combined_df.columns = ['page', 'timeSpent']

    
    combined_df['timeSpent'] = pd.to_numeric(combined_df['timeSpent'], errors='coerce')

    time_spent_by_page = combined_df.groupby('page')['timeSpent'].sum().reset_index()
    max_time_spent_page = time_spent_by_page.loc[time_spent_by_page['timeSpent'].idxmax()]

    fig_time = go.Figure()
    fig_time.add_trace(go.Bar(
        x=time_spent_by_page['page'],
        y=time_spent_by_page['timeSpent'],
        text=time_spent_by_page['timeSpent'],
        textposition='auto'
    ))

    fig_time.update_layout(
        title="Total Time Spent on Each Page",
        xaxis=dict(
            title="Page"
        ),
        yaxis=dict(
            title="Time Spent"
        )
    )

    graph_time_html = pio.to_html(fig_time, full_html=False)

    # Create heatmap overlay with image
    img = Image.open('Screenshot (17).png')
    img_width, img_height = img.size
    vertical_shift = 200

    fig_heatmap = go.Figure()
    fig_heatmap.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=0,
            y=img_height,
            sizex=img_width,
            sizey=img_height,
            sizing="stretch",
            layer="below"
        )
    )

    def generate_overlay(data, color, name):
        fig_heatmap.add_trace(go.Scatter(
            x=data['x'],
            y=img_height - (data['y'] + vertical_shift),
            mode='markers',
            marker=dict(size=12, color=color, opacity=0.6),
            name=name
        ))

    generate_overlay(df[df['event'] == 'hover'], 'green', 'Hover')
    generate_overlay(df[df['event'] == 'click'], 'red', 'Click')

    fig_heatmap.update_layout(
        title="User Interaction Heatmap Overlay",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False, scaleanchor='x', scaleratio=1),
        height=img_height,
        width=img_width,
        xaxis_range=[0, img_width],
        yaxis_range=[0, img_height],
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0)
    )

    graph_heatmap_html = pio.to_html(fig_heatmap, full_html=False)

    # Calculate most clicked elements
    click_counts = click_data['element'].value_counts().reset_index()
    click_counts.columns = ['element', 'click_count']
    click_counts = click_counts.sort_values(by='click_count', ascending=False)

    fig_clicks = px.bar(click_counts, x='element', y='click_count', title='Most Clicked Elements', labels={'element':'Element', 'click_count':'Click Count'}, template="plotly_dark")

    graph_clicks_html = pio.to_html(fig_clicks, full_html=False)

    return render_template('dashboard.html', 
                           graph_nav=graph_nav_html, 
                           graph_time=graph_time_html, 
                           graph_heatmap=graph_heatmap_html, 
                           graph_clicks=graph_clicks_html, 
                           max_time_spent_page=max_time_spent_page)


@app.route('/map1')
def map1():
    # Key Metrics
    df = pd.read_csv('mapLite_user_activity.csv')
    total_region_changes = df[df['event'] == 'Region Change'].shape[0]
    average_time_spent = df['timeSpent'].mean()
    unique_regions_covered = df[['location', 'destination']].nunique()

    # Scatter Map Visualization
    region_change_data = df[df['event'] == 'Region Change']
    scatter_map = px.scatter_geo(region_change_data,
                                 lat=region_change_data['x'],
                                 lon=region_change_data['y'],
                                 hover_name="location",
                                 title="Region Changes on Map",
                                 projection="natural earth",
                                 template="plotly_dark")
    scatter_map_html = scatter_map.to_html(full_html=False)

    # Heatmap
    heat_data = [[row['x'], row['y'], row['timeSpent']] for index, row in df.iterrows()]
    map_center = [df['x'].mean(), df['y'].mean()]
    base_map = folium.Map(location=map_center, zoom_start=7)
    HeatMap(heat_data, radius=15, blur=20, min_opacity=0.2, max_opacity=0.6,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(base_map)
    base_map.save('static/heatmap.html')  # Save heatmap as a static HTML file

    # Bar Chart for Most Frequent Destinations
    destination_counts = df[df['event'] == 'Region Change']['destination'].value_counts().reset_index()
    destination_counts.columns = ['destination', 'count']
    bar_chart = px.bar(destination_counts,
                       x='destination',
                       y='count',
                       title='Most Frequent Destinations',
                       labels={'destination': 'Destination', 'count': 'Count'},
                       template='plotly_dark')
    bar_chart_html = bar_chart.to_html(full_html=False)

    # Render the template with key metrics and visualizations
    return render_template('mapdash.html',
                           total_region_changes=total_region_changes,
                           average_time_spent=average_time_spent,
                           unique_regions_covered=unique_regions_covered,
                           scatter_map=scatter_map_html,
                           bar_chart=bar_chart_html)


data = pd.read_csv('home_user_activity.csv')



def detect_user_behavior_insights(data):
    feedback = []

    # Add a column to calculate time differences between events (if timestamp available)
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['time_diff'] = data['timestamp'].diff().dt.total_seconds()

    # Detect Rapid Clicks (clicks within 1 second of each other)
    click_data = data[data['event'] == 'click']
    rapid_clicks = click_data[click_data['time_diff'] < 1]
    if len(rapid_clicks) > 0:
        feedback.append(f"Behavioral Insight: {len(rapid_clicks)} rapid clicks detected within 1 second of each other.")

    # Time spent hovering over each element before interacting
    hover_data = data[data['event'] == 'hover']
    click_data = click_data.set_index('element')
    hover_data['hover_time'] = hover_data['time_diff']

    long_hover = hover_data[hover_data['hover_time'] > 5]  # Assume 5 seconds is an unusually long hover time
    if len(long_hover) > 0:
        for i, row in long_hover.iterrows():
            feedback.append(f"Behavioral Insight: Long hover over element '{row['element']}' for {row['hover_time']} seconds before interaction.")

    # Scroll without interaction
    scroll_data = data[data['event'] == 'scroll']
    non_interacting_scrolls = scroll_data[~scroll_data['element'].isin(hover_data['element'])]

    if len(non_interacting_scrolls) > 0:
        feedback.append(f"Behavioral Insight: {len(non_interacting_scrolls)} scroll events without interaction detected.")

    # Scroll speed calculation (assuming timestamp data is present)
    if 'time_diff' in scroll_data.columns:
        fast_scrolls = scroll_data[scroll_data['time_diff'] < 0.5]  # Assuming scrolls within 0.5 sec are fast
        if len(fast_scrolls) > 0:
            feedback.append(f"Observation: {len(fast_scrolls)} fast scrolling events detected.")

    # Interaction Diversity
    interaction_counts = data['element'].value_counts()
    low_interaction_elements = interaction_counts[interaction_counts < 2].index.tolist()  # Elements with less than 2 interactions

    if len(low_interaction_elements) > 0:
        feedback.append(f"Observation: Low engagement with {len(low_interaction_elements)} elements.")

    # Element Visibility (can be based on screen position if recorded)
    if 'screen_position' in data.columns:
        non_visible_interactions = data[(data['screen_position'] == 'below fold') & (data['event'] == 'click')]
        if len(non_visible_interactions) > 0:
            feedback.append(f"Behavioral Insight: {len(non_visible_interactions)} interactions with elements outside visible screen area.")

    return feedback

# Flask route to display the insights on a dashboard
@app.route('/anamoly')
def anamoly():
    feedback = detect_user_behavior_insights(data)
    return render_template('anamoly.html', feedback=feedback)






#here will dashbaord for anomoly detection
#################################################################################################################################
##########################################################################################################################################
###################################################################################################################################
############################################################################################################################
##################################################################################################################
##########################################################################################################################
data = pd.read_csv('overallhomedata.csv')

if 'timestamp' not in data.columns:
    raise ValueError("The dataset must contain a 'timestamp' column.")
data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')

data = data.dropna(subset=['timestamp'])
data['hour'] = data['timestamp'].dt.hour
data['day_of_week'] = data['timestamp'].dt.dayofweek
data['elapsed_time'] = data['timestamp'].diff().dt.total_seconds().fillna(0)

categorical_features = ['event', 'element', 'page']
numerical_features = ['hour', 'day_of_week', 'x', 'y', 'timeSpent', 'scroll', 'depth', 'timeSpentOnHover', 'elapsed_time']

# Ensure all required features are present
missing_features = set(categorical_features + numerical_features) - set(data.columns)
if missing_features:
    raise ValueError(f"The dataset is missing the following required columns: {missing_features}")

# Select features
features = categorical_features + numerical_features
X = data[features]

# Define the preprocessing for categorical features
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='None')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Define the preprocessing for numerical features
numerical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

# Combine preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', categorical_transformer, categorical_features),
        ('num', numerical_transformer, numerical_features)
    ])

# Apply preprocessing
X_preprocessed = preprocessor.fit_transform(X)

# Initialize Isolation Forest
iso_forest = IsolationForest(contamination=0.01, random_state=42)
iso_forest.fit(X_preprocessed)

# Predict anomalies
data['anomaly'] = iso_forest.predict(X_preprocessed)

# PCA for visualization
pca = PCA(n_components=2, random_state=42)
if hasattr(X_preprocessed, "toarray"):
    X_pca = pca.fit_transform(X_preprocessed.toarray())
else:
    X_pca = pca.fit_transform(X_preprocessed)
data['PCA1'] = X_pca[:, 0]
data['PCA2'] = X_pca[:, 1]

# Add a descriptive explanation for anomalies
data['Anomaly_Score'] = iso_forest.decision_function(X_preprocessed)

# Initialize Dash app
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard1/')

# Define a function to create descriptive explanations for anomalies
def explain_anomaly(row):
    explanation = []
    threshold = 2
    for feature in numerical_features:
        if abs(row[feature] - data[feature].mean()) > threshold * data[feature].std():
            explanation.append(f"{feature} is unusually {'high' if row[feature] > data[feature].mean() else 'low'}")
    if not explanation:
        explanation.append("No significant deviation in numerical features.")
    return "; ".join(explanation)

# Apply the explanation to anomalies
anomalies = data[data['anomaly'] == -1]
anomalies['Explanation'] = anomalies.apply(explain_anomaly, axis=1)

# Layout of the dashboard
dash_app.layout = html.Div(children=[
    html.H1(children='User Logs Anomaly Detection Dashboard', style={'textAlign': 'center'}),

    html.Div(children='''This dashboard visualizes anomalies detected in user interaction logs. Anomalies are events that deviate significantly from typical user behavior.''', style={'textAlign': 'center', 'marginBottom': '20px'}),

    html.Div([html.Label('Select Visualization:', style={'fontWeight': 'bold'}),
              dcc.Dropdown(id='viz-type', options=[{'label': 'Scatter Plot (X vs Y)', 'value': 'scatter_xy'},
                                                   {'label': 'PCA Plot', 'value': 'pca'},
                                                   {'label': 'Heatmap', 'value': 'heatmap'},
                                                   {'label': 'Time Series', 'value': 'time_series'},
                                                   {'label': 'Box Plot', 'value': 'box_plot'}], value='scatter_xy', clearable=False)], style={'width': '50%', 'margin': 'auto', 'marginBottom': '40px'}),

    dcc.Graph(id='anomaly-graph'),

    html.H2('Detected Anomalies', style={'textAlign': 'center', 'marginTop': '50px'}),

    html.Div([dash_table.DataTable(id='anomaly-table',
                                  columns=[{"name": i, "id": i} for i in anomalies.columns if i != 'Explanation'],
                                  data=anomalies.to_dict('records'), page_size=10,
                                  style_table={'overflowX': 'auto'},
                                  style_cell={'height': 'auto', 'minWidth': '100px', 'width': '150px', 'maxWidth': '180px', 'whiteSpace': 'normal', 'textAlign': 'left'},
                                  style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'})], style={'width': '90%', 'margin': 'auto'}),
])

# Callback to update graph based on selected visualization
@dash_app.callback(
    Output('anomaly-graph', 'figure'),
    Input('viz-type', 'value')
)
def update_graph(viz_type):
    if viz_type == 'scatter_xy':
        fig = px.scatter(data, x='x', y='y', color=data['anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
                         title='Scatter Plot of User Interactions',
                         labels={'color': 'Anomaly Status'},
                         hover_data=['timestamp', 'element', 'page', 'timeSpent'])
        fig.update_traces(marker=dict(size=8,
                                      line=dict(width=1,
                                                color='DarkSlateGrey')),
                          selector=dict(mode='markers'))
    elif viz_type == 'pca':
        fig = px.scatter(data, x='PCA1', y='PCA2', color=data['anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
                         title='PCA Scatter Plot with Anomalies',
                         labels={'color': 'Anomaly Status'},
                         hover_data=['timestamp', 'element', 'page', 'timeSpent'])
        fig.update_traces(marker=dict(size=8,
                                      line=dict(width=1,
                                                color='DarkSlateGrey')),
                          selector=dict(mode='markers'))
    elif viz_type == 'heatmap':
        heatmap_data = data.pivot_table(index='day_of_week', columns='hour', 
                                        values='anomaly', 
                                        aggfunc=lambda x: (x == -1).sum())
        fig = px.imshow(heatmap_data,
                        labels=dict(x="Hour of Day", y="Day of Week", color="Anomaly Count"),
                        x=heatmap_data.columns,
                        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                        title='Heatmap of Anomalies by Day and Hour',
                        color_continuous_scale='Reds')
    elif viz_type == 'time_series':
        data_sorted = data.sort_values('timestamp')
        data_sorted['is_anomaly'] = data_sorted['anomaly'].apply(lambda x: 1 if x == -1 else 0)
        fig = px.scatter(data_sorted, x='timestamp', y='is_anomaly', color=data_sorted['anomaly'].map({1: 'Normal', -1: 'Anomaly'}),
                         title='Time Series of Anomalies',
                         labels={'color': 'Anomaly Status', 'is_anomaly': 'Anomaly'},
                         hover_data=['x', 'y', 'element', 'page'])
        fig.update_yaxes(tickvals=[0, 1], ticktext=['Normal', 'Anomaly'])
    elif viz_type == 'box_plot':
        fig = px.box(data, x='anomaly', y='timeSpentOnHover', color='anomaly',
                     labels={'anomaly': 'Anomaly Status', 'timeSpentOnHover': 'Time Spent on Hover'},
                     title='Box Plot of Time Spent on Hover by Anomaly Status',
                     color_discrete_map={1: 'blue', -1: 'red'})
        fig.update_layout(showlegend=False)
    else:
        fig = {}
    return fig

@app.route('/dashboard1')
def dashboard1():
    return redirect('/dashboard1/') 



#Threat Detection Model start from here
######################################################################################################################
#############################################################################################################################
#####################################################################################################
###########################################################################################
################################################################################
# OWASP ZAP settings
ZAP_API_KEY = '<ZAP API key>'  # Replace with your actual ZAP API key
ZAP_BASE_URL = 'http://localhost:8080'  # The address where ZAP is running
ZAP_CSV_FILE_PATH = 'zap_results.csv'  # Log ZAP results
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}

def initialize_zap():
    zap = ZAPv2(apikey=ZAP_API_KEY, proxies=proxies)  # No baseurl here
    zap.baseurl = ZAP_BASE_URL  # Set baseurl separately
    return zap


def log_scan_results(tool_name, output, csv_file_path):
    """Log scan results to a specific CSV file."""
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([tool_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), output])

def run_zap_scan(zap, target_url):
    """Run OWASP ZAP scan and return the output."""
    zap.urlopen(target_url)  # Access the URL
    time.sleep(2)  # Allow the site to be loaded by ZAP

    # Start Active Scan (you can also use Passive Scan or Spider based on needs)
    scan_id = zap.ascan.scan(target_url)
    
    while int(zap.ascan.status(scan_id)) < 100:  # Wait until scan is 100% complete
        print(f"Scan progress: {zap.ascan.status(scan_id)}%")
        time.sleep(5)

    print("Scan completed!")
    
    # Get the scan results in JSON format
    scan_results = zap.core.alerts(baseurl=target_url)
    
    return scan_results

def run_sqlmap(target_url):
    """Run SQLMap scan with crawling and return the output."""
    sqlmap_command = f'python sqlmap/sqlmap.py -u "{target_url}" --crawl=2 --batch --output-dir=sqlmap_results'
    process = subprocess.run(sqlmap_command, shell=True, capture_output=True, text=True)
    return process.stdout

@app.route('/scan-sql-injection', methods=['POST'])
def scan_sql_injection():
    target_url = request.json.get('target_url')
    
    # Run SQLMap scan
    sqlmap_output = run_sqlmap(target_url)

    # Log SQLMap results
    log_scan_results('SQLMap', sqlmap_output, SQLMAP_CSV_FILE_PATH)
    
    return jsonify({'status': 'success', 'message': 'SQLMap scan completed', 'results': sqlmap_output}), 200

@app.route('/track-url', methods=['POST'])
def track_url():
    target_url = request.json.get('target_url')  # Get the redirected URL dynamically

    # Log the URL tracking before scans
    log_scan_results('URL Tracking', target_url, SQLMAP_CSV_FILE_PATH)  # Log URL tracking to SQLMap results

    # Initialize OWASP ZAP client
    zap = initialize_zap()

    def scan_and_log():
        while True:
            # Perform ZAP scan and log results
            zap_results = run_zap_scan(zap, target_url)
            log_scan_results('OWASP ZAP', zap_results, ZAP_CSV_FILE_PATH)

            # Perform SQLMap scan and log results
            sqlmap_result = run_sqlmap(target_url)
            log_scan_results('SQLMap', sqlmap_result, SQLMAP_CSV_FILE_PATH)

            print(f"Scanned {target_url} successfully. Waiting for 5 minutes before next scan.")
            time.sleep(300)  # Sleep for 5 minutes before the next scan

    # Start scanning in a background thread
    threading.Thread(target=scan_and_log, daemon=True).start()

    return jsonify({
        'status': 'success',
        'message': f'URL {target_url} tracking and scans initiated successfully',
    }), 200



csv_file_path = 'zap_results.csv'

@app.route('/display_logs')
def display_logs():
    log_list = []

    # Open and read the CSV file
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            source = row[0]  
            timestamp = row[1] 
            
            # Convert the string representation of a list of dictionaries to an actual list
            alerts = ast.literal_eval(row[2])  

            # Process each alert in the list of alerts
            alert_entries = []
            for alert in alerts:
                # Create a dictionary for each alert, extracting known keys
                alert_entry = {
                    'sourceid': alert.get('sourceid', ''),
                    'other': alert.get('other', ''),
                    'method': alert.get('method', ''),
                    'evidence': alert.get('evidence', ''),
                    'pluginId': alert.get('pluginId', ''),
                    'cweid': alert.get('cweid', ''),
                    'confidence': alert.get('confidence', ''),
                    'wascid': alert.get('wascid', ''),
                    'description': alert.get('description', ''),
                    'messageId': alert.get('messageId', ''),
                    'inputVector': alert.get('inputVector', ''),
                    'url': alert.get('url', ''),
                    'tags': alert.get('tags', {}),
                    'reference': alert.get('reference', ''),
                    'solution': alert.get('solution', ''),
                    'alert': alert.get('alert', ''),
                    'param': alert.get('param', ''),
                    'attack': alert.get('attack', ''),
                    'name': alert.get('name', ''),
                    'risk': alert.get('risk', ''),
                    'id': alert.get('id', ''),
                    'alertRef': alert.get('alertRef', '')
                }
                alert_entries.append(alert_entry)

            # Append a single entry for all alerts in the row with one timestamp and source
            log_list.append({
                'source': source,
                'timestamp': timestamp,
                'alerts': alert_entries  # List of alerts for this row
            })

    # Render logs to HTML page
    return render_template('threat.html', logs=log_list)



if __name__ == '__main__':
    app.run(debug=True)
