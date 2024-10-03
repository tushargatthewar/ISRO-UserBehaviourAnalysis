from flask import Flask, render_template, url_for
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from PIL import Image
import random
import plotly.express as px
import folium
from folium.plugins import HeatMap

app = Flask(__name__)

@app.route('/')
def index():
    # Load CSV data for user activity
    df = pd.read_csv('user_activity.csv')

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

@app.route('/map')
def map():
    # Key Metrics
    df = pd.read_csv('mapLite.csv')
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


data = pd.read_csv('user_activity.csv')

# Function to identify user behavior insights and provide feedback
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

if __name__ == '__main__':
    app.run(debug=True)
