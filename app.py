from flask import Flask, render_template
from pymongo import MongoClient
import plotly.graph_objs as go
import plotly
import json

app = Flask(__name__)

# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")
db = client["holmegrange"]

@app.route('/')
def dashboard():
    # Example data for bandwidth monitoring
    bandwidth_data = list(db.network_logs.find())
    bandwidth_segments = [log['segment'] for log in bandwidth_data]
    bandwidth_volumes = [log['trafficVolumeMB'] for log in bandwidth_data]

    # Create bandwidth plot
    bandwidth_fig = go.Figure([go.Bar(x=bandwidth_segments, y=bandwidth_volumes)])
    bandwidth_fig.update_layout(title="Bandwidth Monitoring", xaxis_title="Segment", yaxis_title="Traffic Volume (MB)")

    # Example data for asset utilisation
    pipeline = [
        {"$group": {"_id": "$assignedTo", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    asset_data = list(db.assets.aggregate(pipeline))
    asset_users = [r["_id"] if r["_id"] else "Unassigned" for r in asset_data]
    asset_counts = [r["count"] for r in asset_data]

    # Create asset utilisation plot
    asset_fig = go.Figure([go.Bar(x=asset_users, y=asset_counts)])
    asset_fig.update_layout(title="Asset Utilisation", xaxis_title="User ID", yaxis_title="Number of Assets")

    # Example data for maintenance
    today = datetime.datetime.today()
    future = today + datetime.timedelta(days=30)
    maintenance_data = list(db.maintenance.find({"scheduledDate": {"$gte": today.strftime("%Y-%m-%d"), "$lte": future.strftime("%Y-%m-%d")}}))
    maintenance_assets = [event['assetID'] for event in maintenance_data]
    maintenance_dates = [event['scheduledDate'] for event in maintenance_data]

    # Create maintenance plot
    maintenance_fig = go.Figure([go.Bar(x=maintenance_assets, y=maintenance_dates)])
    maintenance_fig.update_layout(title="Upcoming Maintenance", xaxis_title="Asset ID", yaxis_title="Scheduled Date")

    # Convert plots to JSON
    graphs = [
        json.dumps(bandwidth_fig, cls=plotly.utils.PlotlyJSONEncoder),
        json.dumps(asset_fig, cls=plotly.utils.PplotlyJSONEncoder),
        json.dumps(maintenance_fig, cls=plotly.utils.PlotlyJSONEncoder)
    ]

    return render_template('dashboard.html', graphs=graphs)

if __name__ == '__main__':
    app.run(debug=True)
