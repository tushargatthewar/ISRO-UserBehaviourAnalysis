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
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load and preprocess data
data = pd.read_csv('overallhomedata.csv')

# Ensure 'timestamp' exists and is in datetime format
if 'timestamp' not in data.columns:
    raise ValueError("The dataset must contain a 'timestamp' column.")
data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')

# Handle any potential NaT values after conversion
data = data.dropna(subset=['timestamp'])

# Feature engineering
data['hour'] = data['timestamp'].dt.hour
data['day_of_week'] = data['timestamp'].dt.dayofweek
data['elapsed_time'] = data['timestamp'].diff().dt.total_seconds().fillna(0)

# Define feature types
categorical_features = ['event', 'element', 'page']
numerical_features = ['hour', 'day_of_week', 'x', 'y', 
                      'timeSpent', 'scroll', 'depth', 
                      'timeSpentOnHover', 'elapsed_time']

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
    ('imputer', SimpleImputer(strategy='mean')),  # Use 'median' if preferred
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

# Fit the model
iso_forest.fit(X_preprocessed)

# Predict anomalies
data['anomaly'] = iso_forest.predict(X_preprocessed)
# In Isolation Forest, -1 indicates anomaly and 1 indicates normal

# Extract anomalies
anomalies = data[data['anomaly'] == -1]

print(f"Number of anomalies detected: {anomalies.shape[0]}")

# PCA for visualization
pca = PCA(n_components=2, random_state=42)
# Check if X_preprocessed is sparse and convert if necessary
if hasattr(X_preprocessed, "toarray"):
    X_pca = pca.fit_transform(X_preprocessed.toarray())
else:
    X_pca = pca.fit_transform(X_preprocessed)
data['PCA1'] = X_pca[:, 0]
data['PCA2'] = X_pca[:, 1]

# Add a descriptive explanation for anomalies
data['Anomaly_Score'] = iso_forest.decision_function(X_preprocessed)
# Higher negative scores indicate more severe anomalies

# Initialize Dash app
app = dash.Dash(_name_)
server = app.server  # For deployment purposes

# Define a function to create descriptive explanations
def explain_anomaly(row):
    explanation = []
    # Example: Highlight key features that are unusual
    # This can be customized based on domain knowledge
    threshold = 2  # Arbitrary threshold for illustration
    for feature in numerical_features:
        if abs(row[feature] - data[feature].mean()) > threshold * data[feature].std():
            explanation.append(f"{feature} is unusually {'high' if row[feature] > data[feature].mean() else 'low'}")
    if not explanation:
        explanation.append("No significant deviation in numerical features.")
    return "; ".join(explanation)

# Apply the explanation to anomalies
anomalies['Explanation'] = anomalies.apply(explain_anomaly, axis=1)

# Layout of the dashboard
app.layout = html.Div(children=[
    html.H1(children='User Logs Anomaly Detection Dashboard', style={'textAlign': 'center'}),

    html.Div(children='''
        This dashboard visualizes anomalies detected in user interaction logs. Anomalies are events that deviate significantly from typical user behavior.
    ''', style={'textAlign': 'center', 'marginBottom': '20px'}),

    # Dropdown to select visualization type
    html.Div([
        html.Label('Select Visualization:', style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='viz-type',
            options=[
                {'label': 'Scatter Plot (X vs Y)', 'value': 'scatter_xy'},
                {'label': 'PCA Plot', 'value': 'pca'},
                {'label': 'Heatmap', 'value': 'heatmap'},
                {'label': 'Time Series', 'value': 'time_series'},
                {'label': 'Box Plot', 'value': 'box_plot'},
            ],
            value='scatter_xy',
            clearable=False
        )
    ], style={'width': '50%', 'margin': 'auto', 'marginBottom': '40px'}),

    # Graph component to display the selected visualization
    dcc.Graph(
        id='anomaly-graph'
    ),

    # Section to display detailed anomalies
    html.H2('Detected Anomalies', style={'textAlign': 'center', 'marginTop': '50px'}),

    html.Div([
        dash_table.DataTable(
            id='anomaly-table',
            columns=[{"name": i, "id": i} for i in anomalies.columns if i != 'Explanation'],
            data=anomalies.to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '100px', 'width': '150px', 'maxWidth': '180px',
                'whiteSpace': 'normal',
                'textAlign': 'left'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            tooltip_data=[
                {
                    column: {'value': str(row[column]), 'type': 'markdown'}
                    for column in anomalies.columns if column != 'Explanation'
                } for row in anomalies.to_dict('records')
            ],
            tooltip_duration=None,
        )
    ], style={'width': '90%', 'margin': 'auto'}),

    # Display explanations for selected anomaly
    html.Div(id='anomaly-details', style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'})
])

# Callback to update graph based on selected visualization
@app.callback(
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

# Callback to display detailed explanation when a row is selected
@app.callback(
    Output('anomaly-details', 'children'),
    Input('anomaly-table', 'active_cell'),
    Input('anomaly-table', 'data')
)
def display_anomaly_details(active_cell, data_table):
    if active_cell:
        row = active_cell['row']
        column = active_cell['column_id']
        selected_row = data_table[row]
        # Fetch the explanation
        explanation = anomalies.iloc[row]['Explanation']
        # Display the details
        details = html.Div([
            html.H4(f"Details for Anomaly ID: {anomalies.index[row]}"),
            html.P(f"*Timestamp:* {selected_row['timestamp']}"),
            html.P(f"*Event:* {selected_row['event']}"),
            html.P(f"*Element:* {selected_row['element']}"),
            html.P(f"*Page:* {selected_row['page']}"),
            html.P(f"*X Coordinate:* {selected_row['x']}"),
            html.P(f"*Y Coordinate:* {selected_row['y']}"),
            html.P(f"*Time Spent:* {selected_row['timeSpent']}"),
            html.P(f"*Scroll:* {selected_row['scroll']}"),
            html.P(f"*Depth:* {selected_row['depth']}"),
            html.P(f"*Time Spent on Hover:* {selected_row['timeSpentOnHover']}"),
            html.P(f"*Elapsed Time:* {selected_row['elapsed_time']} seconds"),
            html.P(f"*Anomaly Score:* {selected_row['Anomaly_Score']:.2f}"),
            html.P(f"*Explanation:* {explanation}")
        ], style={'border': '1px solid #ccc', 'padding': '10px', 'borderRadius': '5px'})
        return details
    else:
        return html.Div([
            html.P("Click on a row in the table above to see detailed information about the anomaly.")
        ], style={'fontStyle': 'italic'})

# Run the Dash app
if __name__ == '_main_':
    app.run_server(debug=True)