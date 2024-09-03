import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import numpy as np


downtime_icon = html.I(className="bi bi-clock-fill me-2")
failure_rate_icon = html.I(className="bi bi-exclamation-triangle-fill me-2")


# Initialize the Dash app with the Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Helper function to determine badge color based on status
def get_badge_color(status):
    return "success" if status == "Running" else "danger"

# Sample Data
processes = [
    {"step": "Paste Grinding", "status": "Running", "lot": 20005, "units": 1043, "run_time": 1.3, "expected_time": 1.5, "downtime": 8, "failure_rate": 5, "availability": 86.67, "performance": 86.67, "quality":95, "oee":71.36},
    {"step": "Machine 1", "status": "Running", "lot": 20002, "units": 205, "run_time": 20, "expected_time": 30, "downtime": 12, "failure_rate": None, "availability": 66.67, "performance": 66.67, "material_used": 32.4, "waste_material": 4.2, "quality":100, "oee":44.44},
    {"step": "Machine 2", "status": "Running", "lot": 20004, "units": 102, "run_time": 74, "expected_time": 108, "downtime": 40, "failure_rate": None, "availability": 68.52, "performance": 68.52, "material_used": 42.5, "waste_material": 5.3, "quality":100, "oee":46.95},
    {"step": "Machine 3", "status": "Stopped", "lot": None, "units": 733, "run_time": None, "expected_time": None, "downtime": 3, "failure_rate": None, "availability": 0, "performance": 0, "quality":97, "oee":0},
    {"step": "Furnace", "status": "Running", "lot": 19999, "units": 1037, "run_time": 8, "expected_time": 10, "downtime": 4, "failure_rate": None, "availability": 80, "performance": 80, "quality":100, "oee":64},
    {"step": "Wirecut", "status": "Running", "lot": 20000, "units": 1036, "run_time": 3, "expected_time": 4, "downtime": 15, "failure_rate": None, "availability": 75, "performance": 75, "quality":100, "oee":56.25},
    {"step": "Machining", "status": "Stopped", "lot": None, "units": 1035, "run_time": None, "expected_time": None, "downtime": 20, "failure_rate": 4, "availability": 0, "performance": 0, "quality":96, "oee":0},
    {"step": "Dimension Measurement", "status": "Running", "lot": 19998, "units": 1034, "run_time": 1, "expected_time": 3, "downtime": 30, "failure_rate": 4, "availability": 33.33, "performance": 33.33, "quality":96, "oee":10.67},
    {"step": "Tensile Strength Measurement", "status": "Running", "lot": 19998, "units": 1034, "run_time": 0.5, "expected_time": 1, "downtime": 14, "failure_rate": 10, "availability": 50, "performance": 50, "quality":90, "oee":22.5},
    {"step": "Packing", "status": "Running", "lot": 19997, "units": 1033, "run_time": 1, "expected_time": 1, "downtime": 70, "failure_rate": None, "availability": 100, "performance": 100, "quality":100, "oee":100},
    {"step": "Shipping", "status": "Running", "lot": 19996, "units": 1032, "run_time": 1, "expected_time": 2, "downtime": 70, "failure_rate": None, "availability": 50, "performance": 50, "quality":100, "oee":25},
]


# Function to create the main overview dashboard layout
def create_overview_layout():
    return dbc.Container([
      html.H3("Operations Status", className="my-4 text-center"),
      # Row of process headings and badges
      dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(process['step'], className="text-center mb-1", style={"whiteSpace": "normal", "wordWrap": "break-word"}),  # Process as heading
                            dbc.Badge(process['status'], color=get_badge_color(process['status']), className="d-block mx-auto mt-2")
                        ]
                    ),
                    className="mb-3"
                ),
                width=3  # Adjust width as needed
            )
            for process in processes
        ],
        style={"paddingTop": "20px"},
        className="mb-4"
    ),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='downtime-uptime-chart', figure=create_downtime_uptime_chart()), width=6),
                dbc.Col(dcc.Graph(id='stacked-bar-chart', figure=create_stacked_bar_chart()), width=6)
            ],
            className="mb-4"
        ),

         dbc.Row(
            [
                 dbc.Col(dcc.Graph(id='units-bar-chart', figure=create_units_bar_chart()), width=6),
                dbc.Col(dcc.Graph(id='downtime-failure-chart', figure=create_downtime_failure_chart()), width=6),
            ],
            className="mb-4"
        ),
    ], fluid=True)


def calculate_material_percentages(material_used, waste_material):
    total_material = material_used + waste_material
    material_used_percentage = (material_used / total_material) * 100 if total_material > 0 else 0
    waste_material_percentage = 100 - material_used_percentage  # The rest is waste material
    return material_used_percentage, waste_material_percentage

def create_material_pie_chart(material_used, waste_material):
    # Calculate percentages
    material_used_percentage, waste_material_percentage = calculate_material_percentages(material_used, waste_material)

    # Data for the pie chart
    values = [material_used_percentage, waste_material_percentage]
    labels = ['Material Used', 'Waste Material']
    hover_text = [
        f"Material Used: {material_used} KG ({material_used_percentage:.2f}%)",
        f"Waste Material: {waste_material} KG ({waste_material_percentage:.2f}%)"
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Donut chart style
        hoverinfo='text',            # Use custom hover text
        textinfo='value',      
        text=hover_text,             # Custom text for hover
        marker=dict(colors=['#2ca02c', '#d62728'])  # Green for material used, red for waste material
    )])

    fig.update_layout(
        title="Material Usage Breakdown",
        height=300,
        width=400,
        margin=dict(t=20, b=20, l=20, r=20)  # Adjust margins as needed
    )

    return fig

def create_runtime_pie_chart(run_time, expected_time):
    # Handle case where either run_time or expected_time is None
    if run_time is None or expected_time is None:
        return go.Figure()

    # Calculate the percentage of run time out of the expected time
    total = expected_time
    run_time_percentage = (run_time / total) * 100 if total > 0 else 0
    remaining_time_percentage = 100 - run_time_percentage

    # Data for the pie chart
    values = [run_time_percentage, remaining_time_percentage]
    labels = ['Run Time', 'Remaining Time']
    hover_text = [
        f"Run Time: {run_time} hours ({run_time_percentage:.2f}%)",
        f"Remaining Time: {expected_time - run_time} hours ({remaining_time_percentage:.2f}%)"
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4, 
        textinfo='none',
        hoverinfo='text',            # Use custom hover text  
        text=hover_text,             # Custom text for hoverinfo
        marker=dict(colors=['#1f77b4', '#e5e5e5'])  # Colors for the pie slices: blue for run time, light grey for remaining time
    )])

    fig.update_layout(
        title="Progress of Process",
        height=300,
        width=400,
        margin=dict(t=20, b=20, l=20, r=20)  # Adjust margins as needed
    )

    return fig


def create_metric_gauges(process):
    plot_bgcolor = "#def"
    gauge_colors = ["#ff0000", "#ff8000", "#ffff00", "#80ff00"]  # Red to green gradient

    metrics = {
        "Availability": process['availability'],
        "Performance": process['performance'],
        "Quality": process['quality'],
        "OEE": process['oee'],
    }
    
    gauges = []
    
    for metric, value in metrics.items():
        gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            number={'suffix': '%'},
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': metric, 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': gauge_colors[0]},  # Red
                    {'range': [25, 50], 'color': gauge_colors[1]},  # Orange
                    {'range': [50, 75], 'color': gauge_colors[2]},  # Yellow
                    {'range': [75, 100], 'color': gauge_colors[3]}  # Green
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100}}))

        gauge.update_layout(
            height=240,
            width=240,
            margin=dict(t=50, b=10, l=10, r=10)
        )

        gauges.append(gauge)

    return gauges


# Define a function to create a card with "Not Information Available" message
def create_no_data_card():
    return dbc.Card(
        dbc.CardBody(
            html.P("No Information Related to Runtime is Available ", className="text-center", style={"fontSize": "18px", "fontWeight": "bold"})
        ),
        className="mb-3"
    )


def create_material_pie_chart_or_placeholder(material_used, waste_material):
    # Check if either material_used or waste_material is 0 or None
    if material_used == 0 or waste_material == 0:
        return dbc.Card(
            dbc.CardBody(
                html.P("No Information Related to Material Usage is Available", className="text-center", style={"fontSize": "18px", "fontWeight": "bold"})
            ),
            className="mb-3"
        )
    else:
        # Generate the material pie chart
        return dcc.Graph(figure=create_material_pie_chart(material_used, waste_material))
    

def create_process_layout(process):
    # Generate the gauge chart for the process
    gauge = create_gauge_charts(process)[0]  # Assuming a single gauge chart per process
    gauges = create_metric_gauges(process)
    gauges.insert(0, gauge)
    
    # Create runtime pie chart or placeholder card
    if process['run_time'] is not None and process['expected_time'] is not None:
        runtime_pie_chart = dcc.Graph(figure=create_runtime_pie_chart(process['run_time'], process['expected_time']))
    else:
        runtime_pie_chart = dbc.Card(
            dbc.CardBody(
                html.P("No Information Related to Runtime is Available", className="text-center", style={"fontSize": "18px", "fontWeight": "bold"})
            ),
            className="mb-3"
        )

    # Create units produced card
    units_produced_card = dbc.Card(
        dbc.CardBody(
            html.Div([
                html.H5("Units Produced", className="text-center mb-1"),
                html.P(f"{process['units'] if process['units'] is not None else 'N/A'}", className="text-center", style={"fontSize": "24px", "fontWeight": "bold"})
            ])
        ),
        className="mb-3"
    )

     # Create material pie chart or placeholder
    material_pie_chart = create_material_pie_chart_or_placeholder(
        process.get('material_used', 0),
        process.get('waste_material', 0)
    )

    # Create downtime card
    downtime_card = dbc.Card(
        dbc.CardBody(
            html.Div([
                html.H5("Downtime", className="text-center mb-1"),
                html.P(f"{process['downtime'] if process['downtime'] is not None else 'N/A'}%", className="text-center", style={"fontSize": "24px", "fontWeight": "bold"})
            ])
        ),
        className="mb-3"
    )

    # Create failure rate card
    failure_rate_card = dbc.Card(
        dbc.CardBody(
            html.Div([
                html.H5("Failure Rate", className="text-center mb-1"),
                html.P(
                    f"{process['failure_rate']}%" if process['failure_rate'] is not None else "No Information is Available", 
                    className="text-center", 
                    style={"fontSize": "24px", "fontWeight": "bold"}
                )
            ])
        ),
        className="mb-3"
    )

    return dbc.Container([
        html.H4(f"Details on {process['step']}", className="my-4 text-center"),
        # Row of five gauges
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(figure=gauge),
                            style={"width": "100%", "height": "100%"}
                        ),
                        className="mb-3",
                        style={"width": "300px", "padding": "10px"}  # Adjust padding to control spacing
                    ),
                    width=2,  # Set width to evenly distribute space
                )
                for gauge in gauges
            ],
            className="mb-4",
            justify="center",  # Center the cards horizontally
            align="center",    # Optional: Center the cards vertically
            style={"margin-bottom": "10px"}
        ),
        dbc.Row(
            [
                dbc.Col(runtime_pie_chart, width=6),
                dbc.Col(material_pie_chart, width=6),
            ],
            className="mb-4",
            style={"margin-top": "20px"} 
        ),
        dbc.Row(
            [
                dbc.Col(units_produced_card, width=4),
                dbc.Col(downtime_card, width=4),
                dbc.Col(failure_rate_card, width=4),
            ],
            className="mb-4"
        )
    ], fluid=True)


# Prepare data for chart
steps = [item["step"] for item in processes]
downtimes = [item["downtime"] for item in processes]
uptimes = [100 - downtime for downtime in downtimes]

# Create stacked horizontal bar chart
def create_downtime_uptime_chart():
    hover_text = [
        f"<b>{step}</b><br>Uptime: {uptime}%<br>Downtime: {downtime}%"
        for step, downtime, uptime in zip(steps, downtimes, uptimes)
    ]
    
    fig = go.Figure()

    # Add uptime as a percentage
    fig.add_trace(go.Bar(
        y=steps,
        x=uptimes,
        name='Uptime',
        orientation='h',
        marker=dict(color='green'),
        hoverinfo='text',
        hovertext=hover_text
    ))

    # Add downtime as a percentage
    fig.add_trace(go.Bar(
        y=steps,
        x=downtimes,
        name='Downtime',
        orientation='h',
        marker=dict(color='red'),
        hoverinfo='text',
        hovertext=hover_text
    ))

    fig.update_layout(
        barmode='stack',
        title='Process Uptime and Downtime',
        xaxis=dict(title='Percentage (%)'),
        yaxis=dict(title='Process Steps'),
        height=500,
    )

    return fig


# Function to create gauge charts
def create_gauge_charts(process):
    plot_bgcolor = "#def"
    quadrant_colors = ['#ffffff', "#f25829", "#f2a529", "#2bad4e"]
    quadrant_text = ["", "<b>Stopped</b>", "", "<b>Running</b>"]
    n_quadrants = len(quadrant_colors) - 1

    status = process['status']
    if status == 'Running':
        current_value = 10
    else:
        current_value = 40

    min_value = 0
    max_value = 50
    hand_length = np.sqrt(2) / 4
    hand_angle = np.pi * (1 - (max(min_value, min(max_value, current_value)) - min_value) / (max_value - min_value))

    gauge = go.Figure(
        data=[
            go.Pie(
                values=[0.5] + (np.ones(n_quadrants) / 2 / n_quadrants).tolist(),
                rotation=90,
                hole=0.5,
                marker_colors=quadrant_colors,
                text=quadrant_text,
                textinfo="text",
                hoverinfo="skip",
            ),
        ],
        layout=go.Layout(
            showlegend=False,
            margin=dict(b=0, t=50, l=10, r=10),  # Increase top margin for the title
            width=240,
            height=240,
            annotations=[
                go.layout.Annotation(
                    text=f"<b>Status</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=1.05, yanchor="bottom", yref="paper",  # Position the title above the chart
                    showarrow=False,
                    font=dict(size=18, color="black")
                ),
                go.layout.Annotation(
                    text=f"<br><b>Current Lot: {process['lot']}</b>",
                    x=0.5, xanchor="center", xref="paper",
                    y=0.2, yanchor="bottom", yref="paper",
                    showarrow=False,
                ),
            ],
            shapes=[
                go.layout.Shape(
                    type="circle",
                    x0=0.48, x1=0.52,
                    y0=0.48, y1=0.52,
                    fillcolor="#333",
                    line_color="#333",
                ),
                go.layout.Shape(
                    type="line",
                    x0=0.5, x1=0.5 + hand_length * np.cos(hand_angle),
                    y0=0.5, y1=0.5 + hand_length * np.sin(hand_angle),
                    line=dict(color="#333", width=4)
                ),
            ],
        )
    )

    return [gauge]

# Function to create the stacked bar chart with hover text
def create_stacked_bar_chart():
    steps = [process['step'] for process in processes]
    run_time_percentages = [(process['run_time'] / process['expected_time']) * 100 if process['expected_time'] else 0 for process in processes]
    remaining_time_percentages = [100 - run_time for run_time in run_time_percentages]

    # Hover text for each bar
    hover_text = [
        f"<b>{process['step']}</b><br>"
        f"Current Run Time: {process['run_time']}h<br>"
        f"Expected Run Time: {process['expected_time']}h<br>"
        f"Remaining Time: {process['expected_time'] - process['run_time']}h<br>"
        f"Progress: {run_time:.2f}%"
        if process['run_time'] is not None else "N/A"
        for process, run_time in zip(processes, run_time_percentages)
    ]


    fig = go.Figure()

    # Add current run time as a percentage
    fig.add_trace(go.Bar(
        y=steps,
        x=run_time_percentages,
        name='Current Run Time (%)',
        orientation='h',
        marker=dict(color='green'),
        hoverinfo='text',
        hovertext=hover_text
    ))

    # Add remaining time as a percentage
    fig.add_trace(go.Bar(
        y=steps,
        x=remaining_time_percentages,
        name='Remaining Time to Expected (%)',
        orientation='h',
        marker=dict(color='lightgrey'),
        hoverinfo='text',
        hovertext=hover_text
    ))

    fig.update_layout(
        barmode='stack',
        title='Progress of Operations',
        xaxis=dict(title='Percentage (%)'),
        yaxis=dict(title='Process Steps'),
        height=500
    )

    return fig

# Function to create the units produced bar chart
def create_units_bar_chart():
    return go.Figure(
        data=[
            go.Bar(
                x=[process["step"] for process in processes],
                y=[process["units"] for process in processes],
                marker=dict(color="#008080"),
            ),
        ],
        layout=go.Layout(
            title="Units Produced by Each Step",
            xaxis=dict(title="Process Steps"),
            yaxis=dict(title="Units Produced"),
        ),
    )

# Function to create the downtime and failure rate comparison chart
def create_downtime_failure_chart():
    return go.Figure(
        data=[
            go.Bar(
                x=[process["step"] for process in processes],
                y=[process["downtime"] for process in processes],
                name="Downtime",
                marker=dict(color="#008080"),
            ),
            go.Bar(
                x=[process["step"] for process in processes],
                y=[process["failure_rate"] if process["failure_rate"] is not None else 0 for process in processes],
                name="Failure Rate",
                marker=dict(color="#FF8C00"),
            ),
        ],
        layout=go.Layout(
            barmode="group",
            title="Downtime vs Failure Rate",
            xaxis=dict(title="Process Steps"),
            yaxis=dict(title="Percentage"),
        ),
    )

# App Layout with tabs
app.layout = html.Div([
    html.H3("Process Monitoring Dashboard", className="my-4 text-center"),
    dcc.Tabs([
        dcc.Tab(label="Overall Dashboard", children=create_overview_layout()),
        # Create individual tabs for each process
        *[
            dcc.Tab(label=process["step"], children=create_process_layout(process))
            for process in processes
        ],
    ])
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
