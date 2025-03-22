
# Integrated Data Management Simulation Tool
# Project: Holme Grange School - MongoDB-based Modeling

from pymongo import MongoClient
import matplotlib.pyplot as plt
import datetime

# Connect to local MongoDB instance
client = MongoClient("mongodb://localhost:27017/")
db = client["holmegrange"]

# Example Simulation: Bandwidth Monitoring and Alerting
def check_bandwidth(threshold=700):
    logs = db.network_logs.find({"trafficVolumeMB": {"$gt": threshold}})
    print("\nHigh Bandwidth Alerts (>{}MB):".format(threshold))
    for log in logs:
        print(f"Segment: {log['segment']} | Volume: {log['trafficVolumeMB']}MB | IP: {log['sourceIP']}")

# Example Simulation: Asset Utilisation Overview
def asset_utilisation():
    pipeline = [
        {"$group": {"_id": "$assignedTo", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(db.assets.aggregate(pipeline))
    users = [r["_id"] if r["_id"] else "Unassigned" for r in results]
    counts = [r["count"] for r in results]

    plt.figure(figsize=(8, 5))
    plt.bar(users, counts, color="skyblue")
    plt.title("Asset Distribution by User")
    plt.xlabel("User ID")
    plt.ylabel("Number of Assets")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Example Simulation: Scheduled Maintenance Outlook
def upcoming_maintenance(days=30):
    today = datetime.datetime.today()
    future = today + datetime.timedelta(days=days)
    events = db.maintenance.find({"scheduledDate": {"$gte": today.strftime("%Y-%m-%d"), "$lte": future.strftime("%Y-%m-%d")}})
    print("\nUpcoming Maintenance Events:")
    for event in events:
        print(f"Asset: {event['assetID']} | Date: {event['scheduledDate']} | Type: {event['type']} | Status: {event['status']}")

if __name__ == "__main__":
    check_bandwidth()
    asset_utilisation()
    upcoming_maintenance()
