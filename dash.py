from flask import Flask, render_template_string
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from PIL import Image
import random

app = Flask(__name__)

@app.route('/')
def index():
    # Load CSV data for user activity
    df = pd.read_csv('user_activity.csv')

    # Filter only the 'click' events to track navigation
    click_data = df[df['event'] == 'click']
    click_data = click_data[click_data['element'] != 'BUTTON']
    click_data=click_data[click_data['element'] != 'IMG']

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

    max_time_spent_page_html = max_time_spent_page.to_frame().to_html()

    html_template = '''
    <!doctype html>
    <html>
    <head>
        <title>User Activity Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }
            h1, h2 {
                color: #333;
                text-align: center;
            }
            .container {
                width: 80%;
                margin: auto;
                overflow: hidden;
                padding: 20px;
                background: #fff;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                border-radius: 8px;
            }
            .chart {
                margin-bottom: 30px;
            }
            .chart img {
                max-width: 100%;
                height: auto;
            }
            p {
                font-size: 1.1em;
                line-height: 1.5em;
                color: #555;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>User Activity Dashboard</h1>
            <div class="chart">
                <h2>User Click Navigation Flow</h2>
                {{ graph_nav|safe }}
            </div>
            <div class="chart">
                <h2>Total Time Spent on Each Page</h2>
                {{ graph_time|safe }}
            </div>
            <div class="chart">
                <h2>User Interaction Heatmap Overlay</h2>
                {{ graph_heatmap|safe }}
            </div>
            <div class="chart">
                <h2>Most Clicked Elements</h2>
                {{ graph_clicks|safe }}
            </div>
            <h3>Page with the Most Time Spent:</h3>
            <p>{{ max_time_spent_page_html|safe }}</p>
        </div>
    </body>
    </html>
    '''

    return render_template_string(html_template, graph_nav=graph_nav_html, graph_time=graph_time_html, graph_heatmap=graph_heatmap_html, graph_clicks=graph_clicks_html, max_time_spent_page_html=max_time_spent_page_html)

if __name__ == '__main__':
    app.run(debug=True)
