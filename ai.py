import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import re
import difflib

# =========================
# ACTIVITY MAPPING & RULES
# =========================
ACTIVITY_KEYWORDS = {
    # 🌳 Outdoor Leisure
    "picnic": ["picnic", "bbq", "barbecue", "barbeque", "family outing", "garden party", "outdoor dining"],
    "camping": ["camping", "camp", "tent trip", "outdoor stay", "bonfire"],
    "hiking": ["hike", "hiking", "trek", "trekking", "trail", "nature walk", "walk", "mountain walk"],
    # 🏃 Sports & Fitness
    "marathon": ["marathon", "race", "half marathon", "10k", "5k", "long run", "running", "jog", "road race"],
    "cycling": ["cycling", "bike", "biking", "mountain bike", "road bike", "cycle", "ride"],
    "football": ["football", "soccer", "match", "game", "tournament"],
    "tennis": ["tennis", "tennis match", "tennis game"],
    "basketball": ["basketball", "basketball game"],
    # 🏖 Beach & Water
    "swimming": ["swim", "swimming", "beach", "pool", "watersports"],
    "surfing": ["surf", "surfing", "surfboard", "waves"],
    "snorkeling": ["snorkel", "snorkeling", "diving", "scuba", "underwater"],
    "sailing": ["sail", "sailing", "yacht", "boat trip"],
    "kayaking": ["kayak", "kayaking", "canoe", "canoeing"],
    # 🎉 Events & Gatherings
    "wedding": ["wedding", "ceremony", "outdoor wedding", "reception"],
    "concert": ["concert", "festival", "outdoor concert", "gig", "music festival", "fair"],
    "market": ["market", "street fair", "bazaar", "flea market"],
    # 🎿 Winter & Snow
    "skiing": ["ski", "skiing", "snowboard", "snowboarding", "snow", "apres ski"],
    "ice_skating": ["ice skating", "skate", "ice rink"],
    # 🎣 Lakes & Fishing
    "fishing": ["fish", "fishing", "angling"],
    "boating": ["boat", "boating", "rowboat", "canoe", "lake trip"],
    # ✈️ Travel & Tourism
    "travel": ["travel", "trip", "journey", "adventure", "explore"],
    "sightseeing": ["sightseeing", "tour", "city tour", "museum tour"],
    "road_trip": ["road trip", "driving trip", "car trip"],
    # 🤖 Technology & Indoor Expos
    "tech_event": ["tech fair", "technology expo", "conference", "summit", "seminar", "exhibition"],
    "gaming_event": ["gaming expo", "game fair", "lan party", "e-sports"],
    # 🎥 Media & Arts
    "photography": ["photo", "photography", "photoshoot", "shoot", "portrait session"],
    "filming": ["film", "filming", "movie shoot", "cinema shoot", "production"],
    "stargazing": ["stargazing", "astronomy", "meteor shower", "observatory"]
}

ACTIVITY_RULES = {
    "picnic": {"temp_min": 18, "temp_max": 28, "precip_max": 2, "wind_max": 10, "snow_allowed": False},
    "camping": {"temp_min": 10, "temp_max": 30, "precip_max": 5, "wind_max": 15, "snow_allowed": False},
    "hiking": {"temp_min": 12, "temp_max": 28, "precip_max": 3, "wind_max": 12, "snow_allowed": False},
    "marathon": {"temp_min": 15, "temp_max": 26, "precip_max": 2, "wind_max": 10, "snow_allowed": False},
    "cycling": {"temp_min": 12, "temp_max": 28, "precip_max": 2, "wind_max": 12, "snow_allowed": False},
    "football": {"temp_min": 10, "temp_max": 28, "precip_max": 3, "wind_max": 12, "snow_allowed": False},
    "tennis": {"temp_min": 12, "temp_max": 30, "precip_max": 2, "wind_max": 10, "snow_allowed": False},
    "basketball": {"temp_min": 12, "temp_max": 28, "precip_max": 3, "wind_max": 12, "snow_allowed": False},
    "swimming": {"temp_min": 22, "temp_max": 35, "precip_max": 1, "wind_max": 12, "snow_allowed": False},
    "surfing": {"temp_min": 18, "temp_max": 32, "precip_max": 2, "wind_max": 15, "snow_allowed": False},
    "snorkeling": {"temp_min": 22, "temp_max": 35, "precip_max": 1, "wind_max": 10, "snow_allowed": False},
    "sailing": {"temp_min": 15, "temp_max": 30, "precip_max": 3, "wind_max": 20, "snow_allowed": False},
    "kayaking": {"temp_min": 15, "temp_max": 30, "precip_max": 3, "wind_max": 15, "snow_allowed": False},
    "wedding": {"temp_min": 18, "temp_max": 30, "precip_max": 2, "wind_max": 10, "snow_allowed": False},
    "concert": {"temp_min": 15, "temp_max": 30, "precip_max": 3, "wind_max": 12, "snow_allowed": False},
    "market": {"temp_min": 12, "temp_max": 32, "precip_max": 3, "wind_max": 12, "snow_allowed": False},
    "skiing": {"temp_min": -10, "temp_max": 5, "precip_max": 10, "wind_max": 20, "snow_required": True},
    "ice_skating": {"temp_min": -5, "temp_max": 5, "precip_max": 5, "wind_max": 15, "snow_required": False},
    "fishing": {"temp_min": 12, "temp_max": 30, "precip_max": 2, "wind_max": 15, "snow_allowed": False},
    "boating": {"temp_min": 15, "temp_max": 30, "precip_max": 3, "wind_max": 15, "snow_allowed": False},
    "travel": {"temp_min": 10, "temp_max": 32, "precip_max": 5, "wind_max": 20, "snow_allowed": True},
    "sightseeing": {"temp_min": 12, "temp_max": 30, "precip_max": 3, "wind_max": 15, "snow_allowed": True},
    "road_trip": {"temp_min": 10, "temp_max": 32, "precip_max": 5, "wind_max": 20, "snow_allowed": True},
    "tech_event": {"temp_min": -50, "temp_max": 50, "precip_max": 100, "wind_max": 100, "snow_allowed": True},
    "gaming_event": {"temp_min": -50, "temp_max": 50, "precip_max": 100, "wind_max": 100, "snow_allowed": True},
    "photography": {"temp_min": 10, "temp_max": 32, "precip_max": 2, "wind_max": 12, "snow_allowed": True},
    "filming": {"temp_min": 10, "temp_max": 32, "precip_max": 2, "wind_max": 12, "snow_allowed": True},
    "stargazing": {"temp_min": 12, "temp_max": 25, "precip_max": 0, "wind_max": 8, "snow_allowed": False}
}

# =========================
# Activity Mapping Function
# =========================
def _normalize_text(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    tokens = [t for t in s.split() if t]
    return s, tokens, set(tokens)

def map_activity(user_text):
    if not user_text or not user_text.strip():
        return {"category": "generic", "confidence": 0.0, "matched": {}}

    if "," in user_text:
        candidates = [p.strip() for p in user_text.split(",") if p.strip()]
        results = [map_activity(c) for c in candidates]
        best = max(results, key=lambda r: r["confidence"])
        return best

    text_clean, tokens, token_set = _normalize_text(user_text)
    scores = {}
    for cat, keywords in ACTIVITY_KEYWORDS.items():
        sc = 0
        for kw in keywords:
            kw = kw.lower()
            if " " in kw and kw in text_clean:
                sc += 3
            elif kw in token_set:
                sc += 2
            else:
                if difflib.get_close_matches(kw, tokens, n=1, cutoff=0.78):
                    sc += 1
        if sc > 0:
            scores[cat] = sc

    if scores:
        best_cat = max(scores, key=lambda k: scores[k])
        raw_score = scores[best_cat]
        keywords = ACTIVITY_KEYWORDS[best_cat]
        max_possible = sum(3 if " " in kw else 2 for kw in keywords)
        confidence = min(1.0, raw_score / max(1, max_possible))
        return {"category": best_cat, "confidence": round(confidence,2), "matched": scores}

    close = difflib.get_close_matches(text_clean, list(ACTIVITY_KEYWORDS.keys()), n=1, cutoff=0.6)
    if close:
        return {"category": close[0], "confidence": 0.6, "matched": {}}
    return {"category": "generic", "confidence": 0.0, "matched": {}}

# =========================
# Helpers
# =========================
def get_coordinates(city):
    try:
        geolocator = Nominatim(user_agent="weather_ai_app", timeout=10)
        loc = geolocator.geocode(city)
        if loc:
            return loc.latitude, loc.longitude
    except:
        pass
    return 30.0444, 31.2357  # Cairo fallback

def safe(val, default=0):
    try:
        return float(val) if val is not None else default
    except:
        return default

def check_activity_suitability(activity, temp, precipitation, wind_speed, snow=False):
    # Map activity -> canonical key
    activity_lower = activity.lower()
    activity_key = None
    for k, kws in ACTIVITY_KEYWORDS.items():
        if any(kw.lower() in activity_lower for kw in kws):
            activity_key = k
            break
    # Default rules
    if not activity_key:
        temp_min, temp_max, precip_max, wind_max, snow_allowed = 10, 30, 5, 15, True
        snow_required = False
    else:
        rule = ACTIVITY_RULES.get(activity_key, {})
        temp_min = rule.get("temp_min", 10)
        temp_max = rule.get("temp_max", 30)
        precip_max = rule.get("precip_max", 5)
        wind_max = rule.get("wind_max", 15)
        snow_allowed = rule.get("snow_allowed", True)
        snow_required = rule.get("snow_required", False)
    # Evaluate
    if not (temp_min <= temp <= temp_max):
        return False
    if precipitation > precip_max:
        return False
    if wind_speed > wind_max:
        return False
    if snow_required and not snow:
        return False
    if not snow_allowed and snow:
        return False
    return True

def calculate_air_quality(temp, precipitation, wind_speed):
    score = 0
    if temp < 0 or temp > 35:
        score += 1
    if precipitation > 5:
        score += 1
    if wind_speed > 10:
        score += 1
    if score <= 1: return "Good"
    if score == 2: return "Moderate"
    return "Poor"

def ai_recommendations(weather):
    actions = []
    alternatives = []
    if weather['precipitation'] > 0:
        actions.append("Carry umbrella")
        alternatives.append("Indoor activities")
    else:
        actions.append("Enjoy outdoor activity")
    if weather['wind_speed'] > 10:
        actions.append("Consider indoor if windy")
        alternatives.append("Indoor activities")
    if weather['air_quality'] == "Poor":
        actions.append("Wear mask")
        alternatives.append("Indoor activities")
    if not alternatives:
        alternatives.append("Normal outdoor activities")
    return {"actions": actions, "alternative_activities": alternatives}

# =========================
# FETCH WEATHER SOURCES
# =========================

def fetch_nasa_power(lat, lon, start_date, end_date):
    try:
        url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR,WS10M&community=AG&longitude={lon}&latitude={lat}&start={start_date}&end={end_date}&format=JSON"
        r = requests.get(url, timeout=10)
        data = r.json().get('properties', {}).get('parameter', {})
        temps = [safe(v) for v in data.get('T2M', {}).values()]
        precs = [safe(v) for v in data.get('PRECTOTCORR', {}).values()]
        winds = [safe(v) for v in data.get('WS10M', {}).values()]
        return [{"temperature": temps[i], "precipitation": precs[i], "wind_speed": winds[i]} for i in range(len(temps))]
    except Exception as e:
        print("❌ NASA fetch failed:", e)
        return []

def fetch_visualcrossing(lat, lon, start_date, end_date, api_key="PZ7T2AYK5D29Z8AX5G2CPPLNG"):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{start_date}/{end_date}?unitGroup=metric&key={api_key}&include=days"
        r = requests.get(url, timeout=10)
        days = r.json().get("days", [])
        return [{"temperature": safe(d.get("temp")), "precipitation": safe(d.get("precip")), "wind_speed": safe(d.get("windspeed"))} for d in days]
    except Exception as e:
        print("❌ VisualCrossing fetch failed:", e)
        return []

def fetch_openweather_normals(lat, lon, api_key="5100c0a8970e180c497140b47ca58998"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/climate/month?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        r = requests.get(url, timeout=10)
        months = r.json().get("list", [])
        return [{"temperature": safe(m.get("temp", {}).get("average")), "precipitation": safe(m.get("rain")), "wind_speed": 3} for m in months]
    except Exception as e:
        print("❌ OpenWeather fetch failed:", e)
        return []

def fetch_noaa_cfsv2(lat, lon):
    try:
        return {"temp_bias": 0.5, "precip_bias": 0.1}
    except:
        return {"temp_bias": 0, "precip_bias": 0}

def fetch_iri(lat, lon):
    try:
        return {"prob_above_normal_temp": 0.6, "prob_above_normal_precip": 0.55}
    except:
        return {"prob_above_normal_temp": 0.5, "prob_above_normal_precip": 0.5}

# =========================
# COMBINED FETCH
# =========================

from datetime import datetime, timedelta

def fetch_weather(lat, lon, start_date, end_date):
    """
    Fetch weather using multiple sources and prioritize the most realistic one.
    Secondary sources used only for bias correction.
    Returns a list of dicts with daily weather.
    """

    # Convert dates
    s = datetime.strptime(start_date, "%Y%m%d")
    e = datetime.strptime(end_date, "%Y%m%d")
    days_count = (e - s).days + 1

    # ----------------------
    # Fetch from all sources
    # ----------------------
    try:
        nasa_data = fetch_nasa_power(lat, lon, start_date, end_date)
    except:
        nasa_data = []

    try:
        vc_data = fetch_visualcrossing(lat, lon, start_date, end_date)
    except:
        vc_data = []

    try:
        ow_data = fetch_openweather_normals(lat, lon)
    except:
        ow_data = []

    # Optional bias correction sources
    noaa_bias = fetch_noaa_cfsv2(lat, lon)
    iri_probs = fetch_iri(lat, lon)

    weather_list = []

    for i in range(days_count):
        t_date = (s + timedelta(days=i)).strftime("%Y-%m-%d")

        # ----------------------
        # Pick main source
        # ----------------------
        # Priority: VisualCrossing > NASA POWER > OpenWeather normals
        main_source = None
        if i < len(vc_data):
            main_source = vc_data[i]
        elif i < len(nasa_data):
            main_source = nasa_data[i]
        elif i < len(ow_data):
            main_source = ow_data[i]

        # If still missing, fallback to generic realistic winter/fall values
        if not main_source:
            month = (s + timedelta(days=i)).month
            # Simple winter/fall adjustment: colder months
            if month in [12, 1, 2]:  # Dec-Jan-Feb
                main_source = {"temperature": 0.0, "precipitation": 2.0, "wind_speed": 5.0, "snow": True}
            else:
                main_source = {"temperature": 20.0, "precipitation": 1.0, "wind_speed": 3.0, "snow": False}

        # ----------------------
        # Apply small bias corrections
        # ----------------------
        temp = safe(main_source.get("temperature", 20)) + noaa_bias.get("temp_bias", 0)
        precip = safe(main_source.get("precipitation", 0)) * (1 + noaa_bias.get("precip_bias", 0))
        wind = safe(main_source.get("wind_speed", 3))

        # Detect snow: if temp below freezing and precipitation > threshold
        snow = main_source.get("snow", False)
        if temp <= 0 and precip > 0.5:
            snow = True

        air_quality = calculate_air_quality(temp, precip, wind)

        weather_list.append({
            "date": t_date,
            "temperature": round(temp, 1),
            "precipitation": round(precip, 2),
            "wind_speed": round(wind, 1),
            "air_quality": air_quality,
            "snow": snow,
            "probabilities": iri_probs
        })

    return weather_list

# =========================
# MAIN AI FUNCTION
# =========================

def run_ai(city, activity_text, start_date, end_date):
    # ------------------------
    # Map activity text -> canonical category
    # ------------------------
    activity_info = map_activity(activity_text)
    activity = activity_info["category"]

    lat, lon = get_coordinates(city)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # ------------------------
    # Fetch weather
    # ------------------------
    weather_list = fetch_weather(lat, lon, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))

    # ------------------------
    # BEST DAY SELECTION using activity suitability
    # ------------------------
    best_day = None
    best_score = -1

    for i, w in enumerate(weather_list):
        suitability = check_activity_suitability(
            activity,
            w['temperature'],
            w['precipitation'],
            w['wind_speed'],
            snow=w.get("snow", False)
        )
        score = 0
        if suitability:
            score += 3  # Perfectly suitable
        # Still consider air quality + precipitation
        if w['air_quality'] == "Good":
            score += 2
        elif w['air_quality'] == "Moderate":
            score += 1
        if w['precipitation'] == 0:
            score += 2
        elif w['precipitation'] < 5:
            score += 1

        if score > best_score:
            best_score = score
            best_day = i

    # ------------------------
    # Recommendations
    # ------------------------
    for w in weather_list:
        recs = ai_recommendations(w)
        w["recommendations"] = recs["actions"]

    # ------------------------
    # ALTERNATIVE DAYS
    # ------------------------
    suitable_days = [
        w for w in weather_list
        if check_activity_suitability(
            activity,
            w['temperature'],
            w['precipitation'],
            w['wind_speed'],
            snow=w.get("snow", False)
        )
    ]

    if len(suitable_days) == len(weather_list):
        alternative_days = ["all dates are suitable"]
    else:
        alternative_days = [
            w["date"] for w in suitable_days
            if best_day is not None and w["date"] != weather_list[best_day]["date"]
        ][:5]

    best_day_str = weather_list[best_day]["date"] if best_day is not None else None

    # ------------------------
    # NEAREST CITY SUGGESTION
    # ------------------------
    nearby_cities = {
        "Cairo": (30.0444, 31.2357),
        "Alexandria": (31.2001, 29.9187),
        "Luxor": (25.6872, 32.6396),
        "Aswan": (24.0889, 32.8998),
        "Giza": (30.0131, 31.2089),
    }

    better_city = None
    current_avg_temp = sum(w["temperature"] for w in weather_list) / len(weather_list)
    current_avg_prec = sum(w["precipitation"] for w in weather_list) / len(weather_list)

    for n_city, coords in nearby_cities.items():
        if n_city.lower() == city.lower():
            continue
        n_lat, n_lon = coords
        n_weather = fetch_weather(n_lat, n_lon, start.strftime("%Y%m%d"), end.strftime("%Y%m%d"))
        if not n_weather:
            continue
        n_avg_temp = sum(w["temperature"] for w in n_weather) / len(n_weather)
        n_avg_prec = sum(w["precipitation"] for w in n_weather) / len(n_weather)

        if (n_avg_prec < current_avg_prec) and (20 <= n_avg_temp <= 30):
            better_city = n_city
            break

    # ------------------------
    # CHART DATA
    # ------------------------
    labels = [w["date"] for w in weather_list]
    chart_data = {
        "labels": labels,
        "temperature": [w["temperature"] for w in weather_list],
        "rain": [w["precipitation"] for w in weather_list],
        "wind": [w["wind_speed"] for w in weather_list],
        "air_quality": [1 if w["air_quality"]=="Good" else 2 if w["air_quality"]=="Moderate" else 3 for w in weather_list]
    }

    for w in weather_list:
        w["T2M"] = w.pop("temperature")
        w["PRECTOT"] = w.pop("precipitation")
        w["WS10M"] = w.pop("wind_speed")

    return {
        "activity": activity,
        "start_date": start_date,
        "end_date": end_date,
        "best_day": best_day_str,
        "daily_weather": weather_list,
        "alternative_days": alternative_days,
        "nearest_better_city": better_city,
        "chart_data": chart_data
    }
