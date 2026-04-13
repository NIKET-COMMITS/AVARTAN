"""
Plotly Dash Application
Real-time analytics dashboard
Runs on port 8050

Run from project root:  python backend/dashboard_app.py
Or:                     python -m backend.dashboard_app
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure project root is on sys.path (works if cwd is backend/ or repo root)
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

from backend.database import SessionLocal
from backend.services.dashboard_service import dashboard_service
from backend.models import RouteHistory, User

logger = logging.getLogger("avartan")
logging.basicConfig(level=logging.INFO)

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("🌍 AVARTAN Impact Dashboard", className="header-title"),
        html.P("Real-time waste management analytics & community impact", className="header-subtitle"),
    ], className="header"),

    dcc.Tabs(id="tabs", value="tab-1", children=[
        dcc.Tab(label="📊 Overview", value="tab-1", children=[
            html.Div([
                html.Div(id="overview-metrics", className="metrics-container"),
                dcc.Graph(id="impact-over-time"),
                dcc.Graph(id="material-breakdown"),
            ], className="tab-content")
        ]),

        dcc.Tab(label="🌐 Community", value="tab-2", children=[
            html.Div([
                html.Div(id="community-stats", className="stats-grid"),
                dcc.Graph(id="community-growth"),
                dcc.Graph(id="category-distribution"),
            ], className="tab-content")
        ]),

        dcc.Tab(label="🏆 Leaderboards", value="tab-3", children=[
            html.Div([
                html.Div(id="leaderboard-co2", className="leaderboard-section"),
                html.Div(id="leaderboard-value", className="leaderboard-section"),
            ], className="tab-content")
        ]),

        dcc.Tab(label="🏅 Achievements", value="tab-4", children=[
            html.Div([
                html.Div(id="achievements-list", className="achievements-container"),
            ], className="tab-content")
        ]),
    ]),

    dcc.Interval(id="interval-component", interval=300000, n_intervals=0),
])


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


@app.callback(
    Output("overview-metrics", "children"),
    Input("interval-component", "n_intervals"),
)
def update_metrics(_n):
    try:
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                return html.P("No user data available")

            metrics = dashboard_service.calculate_user_metrics(user.id, db)
        finally:
            db.close()

        return html.Div([
            html.Div([
                html.Div([
                    html.H3(f"{metrics['total_routes']}"),
                    html.P("Routes Completed"),
                ], className="metric-box"),
                html.Div([
                    html.H3(f"{metrics['co2_saved_kg']} kg"),
                    html.P("CO2 Saved"),
                ], className="metric-box"),
                html.Div([
                    html.H3(f"₹{metrics['material_value_recovered']}"),
                    html.P("Value Recovered"),
                ], className="metric-box"),
                html.Div([
                    html.H3(f"{metrics['distance_traveled_km']} km"),
                    html.P("Distance Traveled"),
                ], className="metric-box"),
            ], className="metrics-grid"),
        ])
    except Exception as e:
        logger.exception("Error updating metrics: %s", e)
        return html.P("Error loading metrics")


@app.callback(
    Output("community-stats", "children"),
    Input("interval-component", "n_intervals"),
)
def update_community_stats(_n):
    try:
        db = SessionLocal()
        try:
            stats = dashboard_service.get_community_stats(db) or {}
        finally:
            db.close()

        health = stats.get("ecosystem_health")
        try:
            health_pct = float(health) if health is not None else 0.0
        except (TypeError, ValueError):
            health_pct = 0.0

        return html.Div([
            html.Div([
                html.H3(f"{stats.get('total_users', 0)}"),
                html.P("Total Users"),
            ], className="stat-box"),
            html.Div([
                html.H3(f"{stats.get('total_routes', 0)}"),
                html.P("Total Routes"),
            ], className="stat-box"),
            html.Div([
                html.H3(f"{health_pct:.0f}%"),
                html.P("Ecosystem Health"),
            ], className="stat-box"),
        ], className="stats-grid")
    except Exception as e:
        logger.exception("Error updating community stats: %s", e)
        return html.P("Error loading community stats")


@app.callback(
    Output("impact-over-time", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_impact_chart(_n):
    try:
        db = SessionLocal()
        try:
            user = db.query(User).first()
            if not user:
                return _empty_figure("No data available")

            routes = (
                db.query(RouteHistory)
                .filter(RouteHistory.user_id == user.id)
                .order_by(RouteHistory.created_at)
                .all()
            )
        finally:
            db.close()

        dates: dict = {}
        for route in routes:
            if route.created_at is None:
                continue
            date_key = route.created_at.date()
            if date_key not in dates:
                dates[date_key] = {"co2": 0.0, "value": 0.0}
            dates[date_key]["co2"] += route.co2_saved_kg or 0
            dates[date_key]["value"] += route.material_value_rupees or 0

        sorted_dates = sorted(dates.items())
        if not sorted_dates:
            return _empty_figure("No route history yet")

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=[d[0] for d in sorted_dates],
                y=[d[1]["co2"] for d in sorted_dates],
                mode="lines+markers",
                name="CO2 Saved (kg)",
                line=dict(color="#34A853", width=2),
            )
        )
        fig.update_layout(
            title="Impact Over Time",
            xaxis_title="Date",
            yaxis_title="CO2 Saved (kg)",
            hovermode="x unified",
        )
        return fig
    except Exception as e:
        logger.exception("Error creating chart: %s", e)
        return _empty_figure("Error loading data")


app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                margin: 0;
            }

            .header {
                background: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }

            .header-title {
                color: #333;
                margin: 0;
                font-size: 2.5em;
            }

            .header-subtitle {
                color: #666;
                margin: 10px 0 0 0;
            }

            .tab-content {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }

            .metrics-container {
                background: white;
                padding: 20px;
                border-radius: 10px;
            }

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }

            .metric-box {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }

            .metric-box h3 {
                margin: 0;
                font-size: 2em;
            }

            .metric-box p {
                margin: 10px 0 0 0;
                opacity: 0.9;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }

            .stat-box {
                background: #f0f0f0;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }

            .stat-box h3 {
                margin: 0;
                color: #667eea;
                font-size: 2em;
            }

            .stat-box p {
                margin: 10px 0 0 0;
                color: #666;
            }

            @media (max-width: 768px) {
                .metrics-grid {
                    grid-template-columns: 1fr 1fr;
                }

                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


if __name__ == "__main__":
    # Dash 2.14+: prefer run(); run_server() is deprecated
    app.run(debug=True, port=8050, host="0.0.0.0")
