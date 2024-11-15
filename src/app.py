from dash import Dash, dcc, html, Input, Output, State, callback_context
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import os
from datetime import datetime
from openai import OpenAI
from dash.exceptions import PreventUpdate
from utils import  slicing_df, col_change, convert_percent_to_num, encode_image

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

df = pd.read_csv('/Users/rishinigam/kaggle_competitions/dash_app_november_24/dataset/MTA_Daily_Ridership.csv')

saved_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# processing
df['Date'] = pd.to_datetime(df['Date'].values)
df = convert_percent_to_num(df)
#print(df.head(2))

# Initialize the Dash app
app = Dash(__name__)

# Layout of the app
app.layout = html.Div(className="main-container", children=[
    html.H1("MTA Post-Pandemic Ridership Recovery Trends", className="title"),
    html.P("Explore ridership trends across MTA services post-pandemic.", className="description"),
    
    # Dropdown to select service type
    html.Div([
        html.Label("Select Service Type:", className="label"),
        dcc.Dropdown(
            id='service-type',
            options=[
                {'label': 'Subways', 'value': 'Subways'},
                {'label': 'Buses', 'value': 'Buses'},
                {'label': 'LIRR', 'value': 'LIRR'},
                {'label': 'Metro-North', 'value': 'Metro-North'},
                {'label': 'Access-A-Ride', 'value': 'Access-A-Ride'},
                {'label': 'Bridges and Tunnels', 'value': 'Bridges and Tunnels'},
                {'label': 'Staten Island Railway', 'value': 'Staten Island Railway'}
            ],
            value='Subways',
            clearable=False,
            className="input-sizer stacked",
        ),
    ], className="input-group"),

    # Date range picker for the user to select a range of dates
    html.Div([
        html.Label("Select Date Range:", className="label"),
        dcc.DatePickerRange(
            id='Date',
            start_date=pd.to_datetime('2020-01-01'),
            end_date=pd.to_datetime('2023-12-31'),
            display_format='YYYY-MM',
            className="input-sizer stacked",
        ),
    ], className="input-group"),

    # COVID Peak Period Button
    html.Div([
        html.Button("Show COVID Peak Period", id="covid-peak-button", className="button"),
    ], className="input-group"),

    # Graph to display ridership trends side by side
    html.Div([
        dcc.Graph(id='ridership-graph-1', className="graph"),
        dcc.Graph(id='ridership-graph-pre-pandemic', className="graph")
    ], className="graph-container"),
    
    html.Div([
        html.Button("Download graph as Image", id="download-button", className="button"),
        dcc.Download(id="download-image"),
    ], className="download-section"),

    html.Div(id="image-save-confirmation", className="confirmation-message"),

    html.Div(className="query-section", children=[
        html.Label("Ask a question about ridership trends:", className="label"),
        dcc.Input(id='query-input', type='text', placeholder='What was the trend for subways in 2021?', className="input-sizer stacked"),
        html.Button("Submit", id="query-button", className="button"),
    ]),

    html.Div(id="llm-response", className="llm-response"),
])

# Callback to set date range to COVID peak period when the button is clicked
@app.callback(
    [Output('Date', 'start_date'),
    Output('Date', 'end_date'),
    Output('ridership-graph-1', 'figure'),
    Output('ridership-graph-pre-pandemic', 'figure')],
    [Input('covid-peak-button', 'n_clicks'),
    Input('Date', 'start_date'),
    Input('Date', 'end_date'),
    Input('service-type', 'value')],
)

def update_graphs(n_clicks, start_date, end_date, selected_service):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'covid-peak-button':
        start_date = pd.to_datetime('2020-03-01')
        end_date = pd.to_datetime('2021-06-30')
    filtered_df = col_change(df)
    df1, df2 = slicing_df(filtered_df, selected_service, start_date, end_date)

    # Create first line chart
    fig1 = px.line(
        df1,
        x="Date",
        y=df1.columns[1],
        title=f"Ridership Trends for {selected_service} (Post-Pandemic)"
        #labels={"Ridership": "Monthly Ridership", "Date": "Date"}
    )
    fig1.update_layout(template="plotly_white")

    # Create first line chart
    fig2 = px.line(
        df2,
        x="Date",
        y=df2.columns[1],
        title=f"Ridership Trends for {selected_service} (Pre-Pandemic)"
        #labels={"Ridership": "Monthly Ridership", "Date": "Date"}
    )
    fig2.update_layout(template="plotly_white")

    return start_date, end_date, fig1, fig2

@app.callback(
    Output('image-save-confirmation', 'children'),
    [Input('download-button', 'n_clicks')],
    [State("ridership-graph-1", "figure"), State("ridership-graph-pre-pandemic", 'figure')],
    prevent_initial_call=True,suppress_callback_exceptions=True,
)
def download_image(n_clicks, fig1, fig2):
    global saved_timestamp
    if n_clicks is None:
        raise PreventUpdate
    if not os.path.exists("imgs"):
        os.mkdir("imgs")

    fig1 = go.Figure(fig1)
    fig2 = go.Figure(fig2)
    #saved_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fig1_filename = f"imgs/fig1_{saved_timestamp}.png"
    fig2_filename = f"imgs/fig2_{saved_timestamp}.png"
    # convert figure to image
    fig1.write_image(fig1_filename)
    fig2.write_image(fig2_filename)
    # img_bytes_1 = pio.to_image(fig1, format="png", engine='kaliedo')
    # img_bytes_2 = pio.to_image(fig2, format="png", engine='kaliedo')
    return f'Images saved for referencing with LLM.'#dcc.send_file(fig1_path)


# openai LLM
@app.callback(
    Output('llm-response', 'children'),
    [Input('query-button', 'n_clicks'),
     Input('query-input', 'value'), Input('service-type', 'value'), Input('Date', 'start_date'), Input('Date', 'end_date')]
)
def handle_query(n_clicks, query, selected_service, start_date, end_date):
    global saved_timestamp
    if not n_clicks or not query:
        return "No query sent"
    fig1_path = f"imgs/fig1_{saved_timestamp}.png"
    fig2_path = f"imgs/fig2_{saved_timestamp}.png"
    base64_img_1 = encode_image(fig1_path)
    base64_img_2 = encode_image(fig2_path)

    # prompt
    user_message = f"The user inquired: '{query}'. Based on the selected service '{selected_service}', please provide detailed insights into MTA ridership trends between {start_date} and {end_date}. Use data patterns and relevant metrics to deliver a comprehensive response."
    if base64_img_1 and base64_img_2:
        user_message += f" Also take reference from the following images:\nImage 1: {base64_img_1}\nImage 2: {base64_img_2}."
    else:
        user_message += " No images were available for reference."

    # llm resp
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an insightful assistant specializing in MTA ridership data, committed to providing clear, data-driven explanations based on the data you receive. If a question falls outside the data provided, respond with 'I don't have that information.' Avoid creating unsupported solutions or assumptions."},
            {
                "role": "user",
                "content": user_message,
            }
        ],
        model="gpt-4o-mini",
        max_tokens=500,
        temperature=0.5
    )
    answer = chat_completion.choices[0].message.content
    return answer

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
