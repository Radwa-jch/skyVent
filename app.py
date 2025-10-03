from flask import Flask, render_template, request, jsonify
from ai import run_ai, map_activity   # import both

app = Flask(__name__)

# --------- ROUTES FOR PAGES ---------
@app.route("/")
def home():
    return render_template("globe.html")

@app.route("/maps")
def maps():
    return render_template("maps.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/results")
def results():
    return render_template("result.html")

# --------- API ROUTE FOR WEATHER DATA ---------
@app.route("/api/weather", methods=["POST"])
def api_weather():
    data = request.get_json() or {}

    # ------------------------
    # SAFE CITY HANDLING
    # ------------------------
    city = data.get("city", "Cairo")
    if isinstance(city, dict):
        city = city.get("city", "Cairo")
    city = str(city).strip() or "Cairo"

    # ------------------------
    # SAFE ACTIVITY HANDLING
    # ------------------------
    activity_raw = data.get("activity", "generic")
    if isinstance(activity_raw, dict):
        activity_raw = activity_raw.get("category", "generic")
    activity_raw = str(activity_raw).strip()
    if not activity_raw:
        return jsonify({"error": "Activity not provided"}), 400

    # ------------------------
    # DATES
    # ------------------------
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    if not start_date or not end_date:
        return jsonify({"error": "Start or end date missing"}), 400

    try:
        # Map raw activity into structured activity info
        activity_info = map_activity(activity_raw)

        # Run AI weather recommendation
        result = run_ai(city, activity_info["category"], start_date, end_date)

        return jsonify(result)

    except Exception as e:
        print("❌ ERROR in /api/weather:", e)
        return jsonify({"error": "Server error. Check your input and try again."}), 500

# --------- RUN APP ---------
if __name__ == "__main__":
    app.run(debug=True)
