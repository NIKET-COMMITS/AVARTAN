"""
Plotly Dash Application
Real-time analytics dashboard with AI Scanner & Profile
"""

from __future__ import annotations
import logging
import os
import sys
import time
import base64
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import dash
import requests
from dash import Input, Output, State, dcc, html, no_update
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

from backend.database import SessionLocal
from backend.services.dashboard_service import dashboard_service
from backend.models import RouteHistory, User

logger = logging.getLogger("avartan")
logging.basicConfig(level=logging.INFO)

API_BASE_URL = os.getenv("AVARTAN_API_BASE_URL", "http://localhost:8000")
LOGIN_ENDPOINT = f"{API_BASE_URL}/auth/login"
ANALYZE_ENDPOINT = f"{API_BASE_URL}/waste/analyze"
LOG_ENDPOINT = f"{API_BASE_URL}/waste/log"
PROFILE_ENDPOINT = f"{API_BASE_URL}/profile/"

app = dash.Dash(__name__, suppress_callback_exceptions=True)

dashboard_layout = html.Div([
    html.Div([
        html.H1("🌍 AVARTAN Impact Dashboard", className="header-title"),
        html.P("Real-time waste management analytics & community impact", className="header-subtitle"),
    ], className="header"),

    dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="📊 Overview", value="tab-1", children=[
            html.Div([
                html.Div(id="overview-metrics", className="metrics-container"),
                dcc.Graph(id="impact-over-time"),
            ], className="tab-content")
        ]),

        dcc.Tab(label="📸 AI Scanner", value="tab-scan", children=[
            html.Div([
                html.H3("Scan Waste with AI", style={"color": "#4f46e5", "marginBottom": "20px"}),
                dcc.Upload(
                    id='upload-waste-image',
                    children=html.Div(['Drag and Drop or ', html.A('Select an Image')]),
                    style={
                        'width': '100%', 'height': '80px', 'lineHeight': '80px',
                        'borderWidth': '2px', 'borderStyle': 'dashed',
                        'borderRadius': '10px', 'textAlign': 'center', 'margin': '10px 0',
                        'backgroundColor': '#f8fafc', 'cursor': 'pointer'
                    },
                    multiple=False
                ),
                html.Div(id='upload-preview', style={"marginTop": "20px", "textAlign": "center"}),
                dcc.Loading(html.Div(id='ai-analysis-result', style={"marginTop": "20px"})),
                html.Button("Log this Waste (+ Points)", id="log-waste-btn", className="submit-btn hidden"),
                html.Div(id="log-waste-status", style={"marginTop": "10px", "fontWeight": "bold"})
            ], className="tab-content")
        ]),

        dcc.Tab(label="👤 Profile", value="tab-profile", children=[
            html.Div([
                html.H3("Your Profile", style={"color": "#4f46e5"}),
                html.Button("Load Profile Data", id="load-profile-btn", className="submit-btn", style={"maxWidth": "200px"}),
                dcc.Loading(html.Div(id="profile-content", style={"marginTop": "20px"}))
            ], className="tab-content")
        ]),

        dcc.Tab(label="🌐 Community", value="tab-2", children=[
            html.Div([
                html.Div(id="community-stats", className="stats-grid"),
            ], className="tab-content")
        ]),
    ]),

    dcc.Interval(id="interval-component", interval=300000, n_intervals=0),
])

def build_login_layout() -> html.Div:
    return html.Div(
        [
            dcc.Location(id="login-url", refresh=True),
            html.Div(
                [
                    html.Div("AVARTAN", className="brand"),
                    html.H2("Welcome back", className="title"),
                    html.Div(id="login-banner", className="banner hidden"),
                    html.Form(
                        [
                            html.Label("Email", className="field-label"),
                            dcc.Input(id="login-email", type="email", className="input"),
                            html.Label("Password", className="field-label"),
                            dcc.Input(id="login-password", type="password", className="input"),
                            html.Button("Login", id="login-submit", type="submit", className="submit-btn", n_clicks=0),
                        ],
                        className="login-form",
                    ),
                ],
                className="login-card",
            ),
        ],
        className="page-shell",
    )

app.layout = html.Div([
    dcc.Location(id="app-url", refresh=False),
    dcc.Store(id="auth-token", storage_type="local"), 
    dcc.Store(id="current-ai-material"), # Stores AI data for the Log button
    dcc.Store(id="current-ai-weight"), 
    html.Div(id="page-content"),
])

@app.callback(Output("page-content", "children"), Input("app-url", "pathname"))
def render_page(pathname: str | None):
    if pathname in ("/dashboard", "/analytics"):
        return dashboard_layout
    return build_login_layout()

@app.callback(
    Output("login-banner", "children"),
    Output("login-banner", "className"),
    Output("login-url", "pathname"),
    Output("auth-token", "data"),
    Input("login-submit", "n_clicks"),
    State("login-email", "value"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def handle_login(n_clicks, email, password):
    if not email or not password:
        return "Enter email and password.", "banner banner-error", no_update, no_update
    try:
        res = requests.post(LOGIN_ENDPOINT, data={"username": email, "password": password}, timeout=10)
        payload = res.json()
        if res.ok:
            token = payload.get("data", payload).get("access_token", "")
            return "Success!", "banner banner-success", "/dashboard", {"access_token": token}
        return "Invalid credentials.", "banner banner-error", no_update, no_update
    except Exception:
        return "Error connecting to server.", "banner banner-error", no_update, no_update


# ==========================================
# NEW: AI SCANNER CALLBACKS
# ==========================================
@app.callback(
    Output('ai-analysis-result', 'children'),
    Output('log-waste-btn', 'className'),
    Output('upload-preview', 'children'),
    Output('current-ai-material', 'data'),
    Output('current-ai-weight', 'data'),
    Input('upload-waste-image', 'contents'),
    State('auth-token', 'data'),
    prevent_initial_call=True
)
def analyze_uploaded_image(contents, auth_data):
    if not contents:
        raise PreventUpdate
    if not auth_data or "access_token" not in auth_data:
        return html.Div("Unauthorized. Please log in.", className="banner banner-error"), "hidden", no_update, no_update, no_update

    token = auth_data["access_token"]
    content_type, content_string = contents.split(',')
    img_bytes = base64.b64decode(content_string)

    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("image.png", img_bytes, "image/png")}

    try:
        res = requests.post(ANALYZE_ENDPOINT, headers=headers, files=files)
        if res.ok:
            data = res.json().get("data", {})
            
            if not data.get("is_valid_waste", True):
                return html.Div(f"❌ Invalid: {data.get('rejection_reason')}", className="banner banner-error"), "hidden", html.Img(src=contents, style={'maxHeight': '200px', 'borderRadius': '10px'}), no_update, no_update

            material = data.get("material", "Mixed")
            weight_str = data.get("estimated_weight", "0.5")
            weight_float = 0.5
            try:
                weight_float = float(''.join(c for c in weight_str if c.isdigit() or c == '.'))
            except:
                pass

            result_ui = html.Div([
                html.H4(f"🔍 Item: {data.get('item_name', 'Unknown')}"),
                html.P(f"♻️ Material: {material}"),
                html.P(f"⚖️ Estimated Weight: {weight_str}"),
                html.P(f"💡 Action: {data.get('recommended_action', 'Recycle')}"),
            ], className="stat-box", style={"textAlign": "left"})

            preview = html.Img(src=contents, style={'maxHeight': '200px', 'borderRadius': '10px'})
            return result_ui, "submit-btn", preview, material, weight_float
        return html.Div("API Error", className="banner banner-error"), "hidden", no_update, no_update, no_update
    except Exception as e:
        return html.Div(f"Server Error: {str(e)}", className="banner banner-error"), "hidden", no_update, no_update, no_update

@app.callback(
    Output("log-waste-status", "children"),
    Input("log-waste-btn", "n_clicks"),
    State("current-ai-material", "data"),
    State("current-ai-weight", "data"),
    State('auth-token', 'data'),
    prevent_initial_call=True
)
def submit_waste_log(n_clicks, material, weight, auth_data):
    if not material:
        raise PreventUpdate
    
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"material": material, "weight_kg": weight}
    
    try:
        res = requests.post(LOG_ENDPOINT, headers=headers, json=payload)
        if res.ok:
            data = res.json().get("data", {})
            return html.Div(f"✅ Success! Earned {data.get('points_earned')} points.", className="banner banner-success")
        return html.Div("Failed to log waste.", className="banner banner-error")
    except Exception:
        return html.Div("Connection Error.", className="banner banner-error")

# ==========================================
# NEW: PROFILE CALLBACK
# ==========================================
@app.callback(
    Output("profile-content", "children"),
    Input("load-profile-btn", "n_clicks"),
    State('auth-token', 'data'),
    prevent_initial_call=True
)
def load_profile(n_clicks, auth_data):
    if not auth_data or "access_token" not in auth_data:
        return html.Div("Unauthorized.", className="banner banner-error")
    
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        res = requests.get(PROFILE_ENDPOINT, headers=headers)
        if res.ok:
            user = res.json().get("data", {})
            return html.Div([
                html.H3(user.get("name", "User")),
                html.P(f"Email: {user.get('email', 'N/A')}"),
                html.Hr(),
                html.H4(f"🏆 Total Points: {user.get('total_points', 0)}"),
                html.H4(f"🌱 CO2 Saved: {user.get('co2_saved', 0.0)} kg"),
            ], className="stat-box", style={"textAlign": "left", "maxWidth": "400px"})
        return html.Div("Failed to load profile.", className="banner banner-error")
    except Exception:
        return html.Div("Connection Error.", className="banner banner-error")


# (Keeping basic metrics callbacks to prevent crashes)
@app.callback(Output("overview-metrics", "children"), Input("interval-component", "n_intervals"))
def update_metrics(_n):
    return html.Div([html.P("Dashboard active.")])

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f1f5f9; padding: 20px; margin: 0; }
            .header { background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .header-title { color: #1e293b; margin: 0; font-size: 2.5em; }
            .header-subtitle { color: #64748b; margin: 10px 0 0 0; }
            .tab-content { background: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
            .stat-box { background: #f8fafc; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #e2e8f0; }
            .submit-btn { background: #4f46e5; color: white; padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.2s;}
            .submit-btn:hover { background: #4338ca; }
            .hidden { display: none; }
            .banner { padding: 12px; border-radius: 8px; margin-bottom: 15px; }
            .banner-success { background: #dcfce7; color: #166534; }
            .banner-error { background: #fee2e2; color: #991b1b; }
            .page-shell { min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .login-card { background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
            .input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; }
            .field-label { font-weight: bold; color: #334155; display: block; margin-bottom: 5px; }
            .brand { color: #4f46e5; font-weight: 900; letter-spacing: 2px; margin-bottom: 10px;}
        </style>
    </head>
    <body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=8050, host="0.0.0.0")