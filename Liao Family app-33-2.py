import streamlit as st
import webbrowser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone, date
import urllib.parse
import time
import pandas as pd
import math
import re
import streamlit.components.v1 as components
import concurrent.futures
import os  # 新增：用於處理實體檔案路徑

# ==========================================
# 依賴套件檢查與匯入
# ==========================================
try:
    import googlemaps
except ImportError:
    googlemaps = None

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

try:
    import altair as alt
except ImportError:
    alt = None

try:
    from lunarcalendar import Converter, Solar, Lunar
except ImportError:
    Converter = None
    Solar = None
    Lunar = None

# ==========================================
# 設定：Google Maps API Key
# ==========================================
GOOGLE_MAPS_API_KEY = "AIzaSyBK2mfGSyNnfytW7sRkNM5ZWqh2SVGNabo" 

# ==========================================
# Streamlit 頁面設定 (必須是第一個 Streamlit 指令)
# ==========================================
st.set_page_config(
    page_title="宸竹專屬工具箱",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CSS 樣式注入
# ==========================================
st.markdown("""
    <style>
    /* === 強制全域背景與文字顏色 === */
    .stApp {
        background-color: #f5f5f5;
    }
    
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, li, span, div {
        color: #333333;
    }

    /* === 針對 Streamlit Tabs (分頁) === */
    button[data-baseweb="tab"] div p {
        color: #000000 !important; 
        font-weight: bold;
        font-size: 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] div p {
        color: #e74c3c !important;
    }
    
    /* === 標題樣式 === */
    .main-title {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 40px; 
        font-weight: bold;
        text-align: center;
        color: #000000 !important;
        margin-bottom: 10px;
    }
    .section-title {
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 28px; 
        font-weight: bold;
        color: #000000 !important;
        margin-top: 5px;
        margin-bottom: 5px;
        border-bottom: 2px solid #ccc;
    }
    
    /* === 數據框與卡片樣式 === */
    .data-box {
        background-color: #2c3e50;
        padding: 15px;
        border-radius: 5px;
        font-family: "Consolas", "Microsoft JhengHei", sans-serif; 
        font-size: 28px; 
        font-weight: bold;
        line-height: 1.5;
        margin-bottom: 10px;
        color: #ecf0f1 !important; 
    }

    .traffic-card {
        background-color: #2c3e50;
        border: 1px solid #546E7A;
        border-radius: 4px;
        padding: 10px 15px;
        margin-bottom: 12px;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .traffic-card-title {
        color: #ecf0f1 !important;
        font-size: 22px; 
        font-weight: normal;
        margin-bottom: 8px;
        border-bottom: 1px solid #455a64;
        display: inline-block;
        padding-right: 10px;
        padding-bottom: 2px;
    }
    .traffic-row {
        display: block;
        font-size: 28px; 
        font-weight: bold;
        margin-bottom: 5px;
        text-decoration: none !important;
    }
    .traffic-row:hover {
        opacity: 0.8;
    }

    /* === 顏色定義 === */
    .text-gold { color: #ffca28 !important; }
    .text-cyan { color: #26c6da !important; }
    .text-green { color: #2ecc71 !important; } 
    .text-red { color: #ff5252 !important; }   
    .text-white { color: #ffffff !important; }
    
    .data-box span, .traffic-card span {
        color: inherit;
    }

    .stButton>button {
        font-family: "Microsoft JhengHei", sans-serif;
        font-weight: bold;
        border-radius: 5px;
    }

    /* === 家族時光樣式 === */
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    div[data-testid="stMetricLabel"] label {
        color: #555 !important;
        font-size: 18px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 36px !important;
    }

    .birthday-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #ff4b4b;
    }
    .big-font {
        font-size: 26px !important; 
        font-weight: bold;
        color: #333 !important;
    }
    .sub-font {
        font-size: 18px; 
        color: #555 !important;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    .highlight {
        color: #ff4b4b !important;
        font-weight: bold;
        font-size: 22px; 
    }
    .top-card-highlight {
        border-left: 8px solid #ff4b4b !important;
        background-color: #fff9f9 !important;
        border: 1px solid #ffebeb;
    }
    
    div[data-testid="stToolbar"] {
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 5px;
    }
    
    /* 交通方式分類標題 */
    .traffic-section-header {
        font-size: 22px;
        font-weight: bold;
        color: #333;
        margin-top: 15px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* === 單獨針對公車動態的按鈕 (310/952) 放大字體 === */
    a[href*="ebus.gov.taipei"] p {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 邏輯功能函式庫 (工具類)
# ==========================================

def get_time_str(dt):
    return dt.strftime("%H:%M:%S")

@st.cache_data(ttl=600) 
def get_weather_data_html():
    locations = [
        {"name": "新竹", "lat": 24.805, "lon": 120.985},
        {"name": "板橋", "lat": 25.029, "lon": 121.472},
        {"name": "京樺牛肉麵", "lat": 25.056, "lon": 121.526},
        {"name": "長榮航空", "lat": 25.042, "lon": 121.296},
    ]
    
    result_html = ""
    
    for loc in locations:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&current=temperature_2m,weather_code&hourly=precipitation_probability&timezone=auto&forecast_days=1"
            res = requests.get(url, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                temp = data['current']['temperature_2m']
                w_code = data['current'].get('weather_code', -1)
                
                icon = ""
                rain_text = ""
                try:
                    current_time_str = data['current']['time']
                    try:
                        cur_dt = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M")
                    except ValueError:
                        cur_dt = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%S")
                    
                    cur_hour_dt = cur_dt.replace(minute=0, second=0)
                    search_time = cur_hour_dt.strftime("%Y-%m-%dT%H:%M")
                    hourly_times = data['hourly']['time']
                    
                    if search_time in hourly_times:
                        idx = hourly_times.index(search_time)
                        future_probs = data['hourly']['precipitation_probability'][idx : idx+5]
                        
                        if future_probs:
                            max_prob = max(future_probs)
                            
                            is_snow_code = w_code in [56, 57, 66, 67, 71, 73, 75, 77, 85, 86]
                            is_thunder_code = w_code in [95, 96, 99]

                            if is_snow_code:
                                icon = "❄️"
                            elif is_thunder_code:
                                icon = "⛈️"
                            else:
                                if max_prob <= 10:
                                    icon = "☀️"
                                elif max_prob <= 40:
                                    icon = "☁️"
                                else:
                                    if temp <= 0:
                                        icon = "❄️"
                                    elif max_prob <= 70:
                                        icon = "🌦️"
                                    else:
                                        icon = "☔"
                            
                            rain_text = f" ({icon}{max_prob}%)"
                except Exception:
                    pass 

                name_display = loc['name']
                if len(name_display) == 2: name_display += " " 
                
                result_html += f"{name_display}: {temp}°C{rain_text}<br>"
            else:
                result_html += f"{loc['name']}: N/A<br>"
        except:
            result_html += f"{loc['name']}: Err<br>"
            
    if not result_html:
        return "暫無氣象資料"
    return result_html

def parse_duration_to_minutes(text):
    try:
        total_mins = 0
        remaining_text = text
        if "小時" in text:
            parts = text.split("小時")
            hours = int(parts[0].strip())
            total_mins += hours * 60
            remaining_text = parts[1]
        if "分鐘" in remaining_text:
            mins_part = remaining_text.replace("分鐘", "").strip()
            if mins_part.isdigit():
                total_mins += int(mins_part)
        return total_mins
    except:
        return 0

def get_google_maps_url(start, end, mode='driving'):
    s_enc = urllib.parse.quote(start)
    e_enc = urllib.parse.quote(end)
    
    if mode == 'transit':
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=transit"
    elif mode == 'bicycling':
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=bicycling"
    elif mode == 'two_wheeler':
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=two-wheeler&avoid=highways,tolls"
    else:
        return f"https://www.google.com/maps/dir/?api=1&origin={s_enc}&destination={e_enc}&travelmode=driving"

def calculate_traffic(gmaps, start_addr, end_addr, std_time, label_prefix, mode='driving'):
    url = get_google_maps_url(start_addr, end_addr, mode=mode)
    
    if not gmaps:
        return f"{label_prefix}: API未設定", "text-white", url

    try:
        kwargs = {
            'origins': start_addr,
            'destinations': end_addr,
            'departure_time': datetime.now(),
            'language': 'zh-TW'
        }
        
        if mode == 'two_wheeler':
            kwargs['mode'] = 'driving'
            kwargs['avoid'] = 'highways'
        else:
            kwargs['mode'] = mode

        matrix = gmaps.distance_matrix(**kwargs)
        
        if matrix.get('status') != 'OK' or not matrix.get('rows'):
            return f"{label_prefix}: 查無路線", "text-white", url

        el = matrix['rows'][0]['elements'][0]
        
        if el.get('status') != 'OK':
            time_str = "無法估算"
            dist_str = ""
        else:
            if 'duration_in_traffic' in el:
                time_str = el['duration_in_traffic']['text']
            elif 'duration' in el:
                time_str = el['duration']['text']
            else:
                time_str = "無法估算"
                
            if 'distance' in el:
                dist_str = el['distance']['text']
                dist_str = dist_str.replace(" 公里", "km").replace("公里", "km").replace(" km", "km")
            else:
                dist_str = ""
            
        cur_mins = parse_duration_to_minutes(time_str)
        
        if cur_mins >= 60:
            h = cur_mins // 60
            m = cur_mins % 60
            time_display = f"{h}小時{m}分" if m > 0 else f"{h}小時"
        elif cur_mins > 0:
            time_display = f"{cur_mins}分"
        else:
            time_display = time_str.replace("分鐘", "分").replace(" ", "")
        
        if "往板橋" in label_prefix or "反板橋" in label_prefix or "反江子翠" in label_prefix:
            base_class = "text-gold"
        else:
            base_class = "text-cyan"
            
        if cur_mins > 0:
            diff = cur_mins - std_time
            sign = "+" if diff >= 0 else "" 
            
            if diff > 20:
                diff_part = f"<span style='color: #ff5252 !important;'>({sign}{diff}分)</span>"
            else:
                diff_part = f"({sign}{diff}分)"
            
            display_text = f"{label_prefix}: {time_display} {diff_part} {dist_str}".strip()
            color_class = base_class 
            
        else:
            display_text = f"{label_prefix}: {time_display} {dist_str}".strip()
            color_class = base_class
            
        return display_text, color_class, url
        
    except Exception as e:
        try:
            api_mode = "driving" if mode == "two_wheeler" else mode
            api_avoid = "&avoid=highways" if mode == "two_wheeler" else ""
            api_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={urllib.parse.quote(start_addr)}&destinations={urllib.parse.quote(end_addr)}&mode={api_mode}{api_avoid}&departure_time=now&language=zh-TW&key={GOOGLE_MAPS_API_KEY}"
            
            res = requests.get(api_url, timeout=5).json()
            if res.get('status') == 'OK' and res.get('rows'):
                el = res['rows'][0]['elements'][0]
                if el.get('status') == 'OK':
                    if 'duration_in_traffic' in el:
                        time_str = el['duration_in_traffic']['text']
                    elif 'duration' in el:
                        time_str = el['duration']['text']
                    else:
                        time_str = "無法估算"
                        
                    if 'distance' in el:
                        dist_str = el['distance']['text'].replace(" 公里", "km").replace("公里", "km").replace(" km", "km")
                    else:
                        dist_str = ""

                    cur_mins = parse_duration_to_minutes(time_str)
                    
                    if cur_mins >= 60:
                        h = cur_mins // 60; m = cur_mins % 60
                        time_display = f"{h}小時{m}分" if m > 0 else f"{h}小時"
                    elif cur_mins > 0:
                        time_display = f"{cur_mins}分"
                    else:
                        time_display = time_str.replace("分鐘", "分").replace(" ", "")
                        
                    base_class = "text-gold" if any(x in label_prefix for x in ["往板橋", "反板橋", "反江子翠"]) else "text-cyan"
                    
                    if cur_mins > 0:
                        diff = cur_mins - std_time
                        sign = "+" if diff >= 0 else ""
                        diff_part = f"<span style='color: #ff5252 !important;'>({sign}{diff}分)</span>" if diff > 20 else f"({sign}{diff}分)"
                        display_text = f"{label_prefix}: {time_display} {diff_part} {dist_str}".strip()
                    else:
                        display_text = f"{label_prefix}: {time_display} {dist_str}".strip()
                        
                    return display_text, base_class, url
        except:
            pass
            
        return f"{label_prefix}: 查詢失敗", "text-white", url


# ==========================================
# 邏輯功能函式庫 (家族時光類)
# ==========================================

def get_western_zodiac(day, month):
    zodiac_signs = [
        (1, 20, "摩羯座"), (2, 19, "水瓶座"), (3, 20, "雙魚座"), (4, 20, "白羊座"),
        (5, 20, "金牛座"), (6, 21, "雙子座"), (7, 22, "巨蟹座"), (8, 23, "獅子座"),
        (9, 23, "處女座"), (10, 23, "天秤座"), (11, 22, "天蠍座"), (12, 22, "射手座"),
        (12, 31, "摩羯座")
    ]
    for m, d, sign in zodiac_signs:
        if (month == m and day <= d) or (month == m - 1 and day > d and not (m == 1 and day <= 20)):
            return sign
    return "摩羯座"

def get_chinese_zodiac(year):
    zodiacs = ["鼠", "牛", "虎", "兔", "龍", "蛇", "馬", "羊", "猴", "雞", "狗", "豬"]
    return zodiacs[(year - 4) % 12]

def calculate_detailed_age(birth_date):
    today = date.today()
    delta = today - birth_date
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years, delta.days

def get_lunar_date_str(birth_date):
    try:
        if Converter and Solar:
            solar = Solar(birth_date.year, birth_date.month, birth_date.day)
            lunar = Converter.Solar2Lunar(solar)
            return f"{lunar.month}/{lunar.day}"
        else:
            return "N/A"
    except Exception:
        return "N/A"

def get_next_birthday_days(birth_date):
    today = date.today()
    this_year_bday = date(today.year, birth_date.month, birth_date.day)
    if this_year_bday < today:
        next_bday = date(today.year + 1, birth_date.month, birth_date.day)
    else:
        next_bday = this_year_bday
    return (next_bday - today).days

def get_next_lunar_birthday_days(birth_date):
    try:
        if Converter and Solar and Lunar:
            today = date.today()
            solar_birth = Solar(birth_date.year, birth_date.month, birth_date.day)
            lunar_birth = Converter.Solar2Lunar(solar_birth)
            birth_lmonth = lunar_birth.month
            birth_lday = lunar_birth.day
            
            solar_today = Solar(today.year, today.month, today.day)
            lunar_today = Converter.Solar2Lunar(solar_today)
            current_lyear = lunar_today.year
            
            try:
                this_year_lunar = Lunar(current_lyear, birth_lmonth, birth_lday, isleap=False)
                this_year_solar = Converter.Lunar2Solar(this_year_lunar)
                this_year_bday = date(this_year_solar.year, this_year_solar.month, this_year_solar.day)
            except ValueError: 
                this_year_lunar = Lunar(current_lyear, birth_lmonth, birth_lday-1, isleap=False)
                this_year_solar = Converter.Lunar2Solar(this_year_lunar)
                this_year_bday = date(this_year_solar.year, this_year_solar.month, this_year_solar.day)

            if this_year_bday < today:
                next_lyear = current_lyear + 1
                try:
                    next_year_lunar = Lunar(next_lyear, birth_lmonth, birth_lday, isleap=False)
                    next_year_solar = Converter.Lunar2Solar(next_year_lunar)
                    next_bday = date(next_year_solar.year, next_year_solar.month, next_year_solar.day)
                except ValueError:
                    next_year_lunar = Lunar(next_lyear, birth_lmonth, birth_lday-1, isleap=False)
                    next_year_solar = Converter.Lunar2Solar(next_year_lunar)
                    next_bday = date(next_year_solar.year, next_year_solar.month, next_year_solar.day)
            else:
                next_bday = this_year_bday
                
            return (next_bday - today).days
        else:
            return "N/A"
    except Exception:
        return "N/A"

# ==========================================
# 航班專區 (終極穩定版：內建常態班表資料庫)
# ==========================================
def fetch_single_flight(flight_number):
    """
    建立專屬長榮航空的「常態班表資料庫」(Static Database)
    """
    STATIC_DB = {
        "BR9": {"FROM": "Vancouver (YVR)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "02:00", "STA": "05:25", "Total Time": "13h 25m"},
        "BR10": {"FROM": "Taipei (TPE)", "To": "Vancouver (YVR)", "AIRCRAFT": "77W", "STD": "23:55", "STA": "19:50", "Total Time": "10h 55m"},
        "BR117": {"FROM": "Sapporo (CTS)", "To": "Taipei (TPE)", "AIRCRAFT": "A333", "STD": "16:15", "STA": "19:30", "Total Time": "4h 15m"},
        "BR129": {"FROM": "Osaka (KIX)", "To": "Taipei (TPE)", "AIRCRAFT": "781", "STD": "18:30", "STA": "20:30", "Total Time": "3h 00m"},
        "BR130": {"FROM": "Taipei (TPE)", "To": "Osaka (KIX)", "AIRCRAFT": "781", "STD": "13:35", "STA": "17:15", "Total Time": "2h 40m"},
        "BR131": {"FROM": "Osaka (KIX)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "13:10", "STA": "15:05", "Total Time": "2h 55m"},
        "BR132": {"FROM": "Taipei (TPE)", "To": "Osaka (KIX)", "AIRCRAFT": "77W", "STD": "08:30", "STA": "11:55", "Total Time": "2h 25m"},
        "BR157": {"FROM": "Komatsu (KMQ)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "11:45", "STA": "14:35", "Total Time": "3h 50m"},
        "BR158": {"FROM": "Taipei (TPE)", "To": "Komatsu (KMQ)", "AIRCRAFT": "A321", "STD": "06:35", "STA": "10:25", "Total Time": "2h 50m"},
        "BR159": {"FROM": "Seoul (ICN)", "To": "Taipei (TPE)", "AIRCRAFT": "A333", "STD": "19:45", "STA": "21:40", "Total Time": "2h 55m"},
        "BR160": {"FROM": "Taipei (TPE)", "To": "Seoul (ICN)", "AIRCRAFT": "A333", "STD": "15:15", "STA": "18:45", "Total Time": "2h 30m"},
        "BR165": {"FROM": "Seoul (ICN)", "To": "Kaohsiung (KHH)", "AIRCRAFT": "A321", "STD": "12:00", "STA": "14:15", "Total Time": "3h 15m"},
        "BR166": {"FROM": "Kaohsiung (KHH)", "To": "Seoul (ICN)", "AIRCRAFT": "A321", "STD": "07:00", "STA": "10:55", "Total Time": "2h 55m"},
        "BR169": {"FROM": "Seoul (ICN)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "11:40", "STA": "13:30", "Total Time": "2h 50m"},
        "BR170": {"FROM": "Taipei (TPE)", "To": "Seoul (ICN)", "AIRCRAFT": "A321", "STD": "07:30", "STA": "11:00", "Total Time": "2h 30m"},
        "BR177": {"FROM": "Osaka (KIX)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "10:55", "STA": "13:05", "Total Time": "3h 10m"},
        "BR178": {"FROM": "Taipei (TPE)", "To": "Osaka (KIX)", "AIRCRAFT": "A321", "STD": "06:30", "STA": "10:10", "Total Time": "2h 40m"},
        "BR233": {"FROM": "Taipei (TPE)", "To": "Jakarta (CGK)", "AIRCRAFT": "77W", "STD": "08:45", "STA": "13:10", "Total Time": "5h 25m"},
        "BR234": {"FROM": "Jakarta (CGK)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "14:30", "STA": "21:00", "Total Time": "5h 30m"},
        "BR265": {"FROM": "Phnom Penh (PNH)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "12:55", "STA": "17:15", "Total Time": "3h 20m"},
        "BR266": {"FROM": "Taipei (TPE)", "To": "Phnom Penh (PNH)", "AIRCRAFT": "A321", "STD": "09:10", "STA": "11:55", "Total Time": "3h 45m"},
        "BR271": {"FROM": "Manila (MNL)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "12:50", "STA": "15:00", "Total Time": "2h 10m"},
        "BR272": {"FROM": "Taipei (TPE)", "To": "Manila (MNL)", "AIRCRAFT": "77W", "STD": "09:30", "STA": "11:50", "Total Time": "2h 20m"},
        "BR277": {"FROM": "Manila (MNL)", "To": "Taipei (TPE)", "AIRCRAFT": "787", "STD": "19:00", "STA": "21:30", "Total Time": "2h 30m"},
        "BR278": {"FROM": "Taipei (TPE)", "To": "Manila (MNL)", "AIRCRAFT": "787", "STD": "15:30", "STA": "17:50", "Total Time": "2h 20m"},
        "BR383": {"FROM": "Taipei (TPE)", "To": "Da Nang (DAD)", "AIRCRAFT": "A321", "STD": "09:45", "STA": "11:40", "Total Time": "2h 55m"},
        "BR384": {"FROM": "Da Nang (DAD)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "14:10", "STA": "18:05", "Total Time": "2h 55m"},
        "BR385": {"FROM": "Taipei (TPE)", "To": "Hanoi (HAN)", "AIRCRAFT": "A321", "STD": "14:50", "STA": "17:15", "Total Time": "3h 25m"},
        "BR386": {"FROM": "Hanoi (HAN)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "18:30", "STA": "22:20", "Total Time": "2h 50m"},
        "BR397": {"FROM": "Hanoi (HAN)", "To": "Taipei (TPE)", "AIRCRAFT": "77W", "STD": "12:05", "STA": "15:55", "Total Time": "2h 50m"},
        "BR398": {"FROM": "Taipei (TPE)", "To": "Hanoi (HAN)", "AIRCRAFT": "77W", "STD": "09:15", "STA": "11:05", "Total Time": "2h 50m"},
        "BR757": {"FROM": "Hangzhou (HGH)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "19:35", "STA": "21:30", "Total Time": "1h 55m"},
        "BR758": {"FROM": "Taipei (TPE)", "To": "Hangzhou (HGH)", "AIRCRAFT": "A321", "STD": "16:25", "STA": "18:15", "Total Time": "1h 50m"},
        "BR771": {"FROM": "Shanghai (SHA)", "To": "Taipei (TSA)", "AIRCRAFT": "78X", "STD": "19:40", "STA": "21:45", "Total Time": "2h 05m"},
        "BR772": {"FROM": "Taipei (TSA)", "To": "Shanghai (SHA)", "AIRCRAFT": "78X", "STD": "14:40", "STA": "16:30", "Total Time": "1h 50m"},
        "BR805": {"FROM": "Macau (MFM)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "13:15", "STA": "15:00", "Total Time": "1h 45m"},
        "BR806": {"FROM": "Taipei (TPE)", "To": "Macau (MFM)", "AIRCRAFT": "A321", "STD": "10:45", "STA": "12:35", "Total Time": "1h 50m"},
        "BR867": {"FROM": "Hong Kong (HKG)", "To": "Taipei (TPE)", "AIRCRAFT": "787", "STD": "10:25", "STA": "12:10", "Total Time": "1h 45m"},
        "BR868": {"FROM": "Taipei (TPE)", "To": "Hong Kong (HKG)", "AIRCRAFT": "787", "STD": "07:25", "STA": "09:15", "Total Time": "1h 50m"},
        "BR869": {"FROM": "Hong Kong (HKG)", "To": "Taipei (TPE)", "AIRCRAFT": "787", "STD": "15:25", "STA": "17:10", "Total Time": "1h 45m"},
        "BR870": {"FROM": "Taipei (TPE)", "To": "Hong Kong (HKG)", "AIRCRAFT": "787", "STD": "12:25", "STA": "14:15", "Total Time": "1h 50m"},
        "BR891": {"FROM": "Taipei (TPE)", "To": "Hong Kong (HKG)", "AIRCRAFT": "A321", "STD": "07:00", "STA": "08:50", "Total Time": "1h 50m"},
        "BR892": {"FROM": "Hong Kong (HKG)", "To": "Taipei (TPE)", "AIRCRAFT": "A321", "STD": "09:50", "STA": "11:30", "Total Time": "1h 40m"},
        "BR6535": {"FROM": "Taipei (TPE)", "To": "Charter/Cargo", "AIRCRAFT": "N/A", "STD": "N/A", "STA": "N/A", "Total Time": "N/A"}
    }
    
    flight_upper = flight_number.upper()
    
    if flight_upper in STATIC_DB:
        record = STATIC_DB[flight_upper]
        return {
            "Flight": flight_upper,
            "FROM": record["FROM"],
            "To": record["To"],
            "AIRCRAFT": record["AIRCRAFT"],
            "STD": record["STD"],
            "STA": record["STA"],
            "Total Time": record["Total Time"]
        }
    
    return {
        "Flight": flight_upper,
        "FROM": "N/A",
        "To": "N/A",
        "AIRCRAFT": "N/A",
        "STD": "N/A",
        "STA": "N/A",
        "Total Time": "N/A"
    }

@st.cache_data(ttl=1800) 
def get_all_flight_data(flights):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_flight = {executor.submit(fetch_single_flight, f): f for f in flights}
        for future in concurrent.futures.as_completed(future_to_flight):
            flight = future_to_flight[future]
            try:
                results[flight] = future.result()
            except:
                results[flight] = {
                    "Flight": flight.upper(),
                    "FROM": "N/A",
                    "To": "N/A",
                    "AIRCRAFT": "N/A",
                    "STD": "N/A",
                    "STA": "N/A",
                    "Total Time": "N/A"
                }
    return results

def get_live_flight_url(flight):
    """
    將航班直接轉換為 FlightAware 網址 (如 BR9 轉換為 EVA9)
    取代原本會被阻擋的 Flightradar24 爬蟲邏輯。
    """
    flight_upper = flight.upper()
    
    # 解析 FlightAware 專用 ICAO 航班號 (如 BR9 轉換為 EVA9)
    fa_flight_id = flight_upper.replace("BR", "EVA") if flight_upper.startswith("BR") else flight_upper
    
    # 組合 FlightAware 網址
    fa_url = f"https://www.flightaware.com/live/flight/{fa_flight_id}"
    return fa_url

@st.cache_data(ttl=60) 
def get_all_flight_urls(flights):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_flight = {executor.submit(get_live_flight_url, f): f for f in flights}
        for future in concurrent.futures.as_completed(future_to_flight):
            flight = future_to_flight[future]
            try:
                results[flight] = future.result()
            except:
                # 避免萬一失敗，給予預設 FlightAware 網址
                fa_id = flight.upper().replace("BR", "EVA") if flight.upper().startswith("BR") else flight.upper()
                results[flight] = f"https://www.flightaware.com/live/flight/{fa_id}"
    return results

# ==========================================
# 共享資料管理 (Session State)
# ==========================================

if 'family_data' not in st.session_state:
    st.session_state.family_data = [
        {"name": "孟竹", "birth_date": date(1988, 10, 31), "category": "孟竹家"},
        {"name": "衣宸", "birth_date": date(1993, 6, 7), "category": "孟竹家"},
        {"name": "沁玹", "birth_date": date(2022, 4, 12), "category": "孟竹家"},
        {"name": "承豐", "birth_date": date(2023, 10, 17), "category": "孟竹家"},
        {"name": "清標", "birth_date": date(1955, 10, 25), "category": "標仔家"},
        {"name": "蓮瑞", "birth_date": date(1959, 4, 8), "category": "標仔家"},
        {"name": "子瑩", "birth_date": date(1985, 3, 29), "category": "標仔家"},
        {"name": "子欣", "birth_date": date(1987, 4, 4), "category": "標仔家"},
    ]

# 儲存衣宸航班的 Session State
if 'selected_flight' not in st.session_state:
    st.session_state.selected_flight = None

FAMILY_GROUPS = ["孟竹家", "標仔家", "其他"]

with st.sidebar:
    st.header("➕ 新增家庭成員")
    new_name = st.text_input("姓名")
    new_date = st.date_input("國曆生日", min_value=date(1900, 1, 1))
    new_category = st.selectbox("歸屬家族", FAMILY_GROUPS, index=2) 
    
    if st.button("加入名單"):
        if new_name:
            st.session_state.family_data.append({
                "name": new_name,
                "birth_date": new_date,
                "category": new_category
            })
            st.success(f"已加入 {new_name} 到 {new_category}！")
        else:
            st.error("請輸入姓名")
            
    st.divider()
    if st.button("重置/清空名單"):
        st.session_state.family_data = []
        st.rerun()

st.markdown('<div class="main-title">宸竹專屬工具箱app</div>', unsafe_allow_html=True)

# 把 "✈️ 衣宸航班" 移到最左邊
tab1, tab2, tab3 = st.tabs(["✈️ 衣宸航班", "🛠️ 日常工具 & 路況", "🎂 家族生日 & 時光"])

# ------------------------------------------------------------------
# TAB 1: 衣宸航班
# ------------------------------------------------------------------
with tab1:
    
    st.markdown("### 📋 上傳本月班表")
    # 提供按鈕上傳圖片
    uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    # 設定儲存班表的實體檔案名稱
    SCHEDULE_FILE = "shared_schedule.png"

    if uploaded_file is not None:
        # 將上傳的圖片實體寫入到伺服器端
        with open(SCHEDULE_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ 班表已成功上傳！現在別人打開網址也會看到這張圖表。")

    # 顯示圖片：改成檢查實體檔案是否存在
    if os.path.exists(SCHEDULE_FILE):
        st.image(SCHEDULE_FILE, use_column_width=True)
    else:
        st.markdown("""
            <div style="background-color: #4a90e2; height: 500px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; border-radius: 5px; font-size: 20px;">
                尚無圖片，請由上方上傳班表
            </div>
        """, unsafe_allow_html=True)
        
    st.divider()

    # 創建所有航班的按鈕與報表
    st.markdown("### 🔘 航班快捷按鈕 & 報表")
    
    # CSS調整：增加今日專屬航班按鈕樣式 (flight-btn-today)
    st.markdown("""
        <style>
        .flight-btn-red {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #ea4335; /* 紅色範例 */
            color: #ffffff !important;
            padding: 6px 14px;
            border-radius: 4px;
            text-decoration: none !important;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: opacity 0.3s, transform 0.2s;
            min-width: 80px;
        }
        .flight-btn-red:hover {
            opacity: 0.85;
            transform: translateY(-2px);
        }
        
        .flight-btn-today {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background-color: #ff9800; /* 顯眼的橘黃色代表今天航班 */
            color: #000000 !important;
            padding: 6px 14px;
            border-radius: 4px;
            text-decoration: none !important;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: opacity 0.3s, transform 0.2s;
            min-width: 80px;
            border: 2px solid #e65100;
        }
        .flight-btn-today:hover {
            opacity: 0.85;
            transform: translateY(-2px);
        }
        
        .flight-btn-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 建立 2026年3月 班表資料庫 (依照你上傳的圖片資料)
    SCHEDULE_MAR_2026 = {
        date(2026, 3, 2): ["BR178", "BR177"],
        date(2026, 3, 3): ["BR265", "BR266"],
        date(2026, 3, 4): ["BR160", "BR159"],
        date(2026, 3, 6): ["BR397", "BR398"],
        date(2026, 3, 7): ["BR869", "BR870"],
        date(2026, 3, 8): ["BR867", "BR868"],
        date(2026, 3, 12): ["BR805", "BR806"],
        date(2026, 3, 13): ["BR758", "BR757"],
        date(2026, 3, 15): ["BR178", "BR177"],
        date(2026, 3, 18): ["BR10"],
        date(2026, 3, 20): ["BR9"],
        date(2026, 3, 21): ["BR9"],
        date(2026, 3, 29): ["BR166", "BR165"],
        date(2026, 3, 30): ["BR130", "BR129"],
        date(2026, 3, 31): ["BR277", "BR278"],
    }

    # 合併舊有與新增的航班清單 (已去除重複的BR891, BR892)
    flights = [
        "BR178", "BR177", "BR265", "BR266", "BR160", "BR159", "BR397", "BR398", "BR6535",
        "BR869", "BR870", "BR867", "BR868", "BR805", "BR806", "BR758", "BR757", 
        "BR10", "BR9", "BR166", "BR165", "BR130", "BR129", "BR277", "BR278",
        "BR169", "BR170", "BR271", "BR272", "BR891", "BR892", "BR132", "BR131", 
        "BR383", "BR384", "BR772", "BR771", "BR117", "BR385", "BR386", "BR158", 
        "BR157", "BR233", "BR234",
        "BR722", "BR721", "BR765", "BR766", "BR122", "BR121", "BR164", "BR163"
    ]
    
    # 按照數字大小排序航班 (例如: BR9 -> BR10 -> BR129...)
    flights = sorted(flights, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf'))
    
    # 平行獲取所有航班的資訊與即時路徑網址 (避免阻塞 UI)
    with st.spinner("🚀 正在即時抓取最新航班資訊與動態路徑，請稍候..."):
        all_flight_data = get_all_flight_data(flights)
        all_flight_urls = get_all_flight_urls(flights)
    
    # 將畫面切割為左右兩塊 (左側按鈕, 右側為 Output Excel 報表)
    col_btns, col_table = st.columns([1, 2], gap="medium")

    with col_btns:
        btn_html = '<div class="flight-btn-container">'
        
        # 取得今天日期，並找出今天的航班陣列 (若想測試3月2號效果，可將此行暫時改為 today_date = date(2026, 3, 2))
        today_date = date.today()
        today_flights = SCHEDULE_MAR_2026.get(today_date, [])
        
        for flight in flights:
            # 確保若有未預期情況，皆提供 FlightAware 網址
            fa_id = flight.upper().replace("BR", "EVA") if flight.upper().startswith("BR") else flight.upper()
            url = all_flight_urls.get(flight, f"https://www.flightaware.com/live/flight/{fa_id}")
            
            # 判斷這個航班是否在今天的班表內，賦予不同的 class 顏色
            if flight.upper() in today_flights:
                btn_class = "flight-btn-today"
            else:
                btn_class = "flight-btn-red"
                
            btn_html += f'<a href="{url}" target="_blank" class="{btn_class}">{flight.upper()}</a>'
        btn_html += '</div>'
        
        st.markdown(btn_html, unsafe_allow_html=True)

    with col_table:
        # 依據按鈕順序產出對應的 DataFrame
        df_report = pd.DataFrame([all_flight_data[f] for f in flights])
        # 依照需求指定欄位排列順序：加入 "Total Time" 顯示在最右側
        df_report = df_report[["Flight", "FROM", "To", "AIRCRAFT", "STD", "STA", "Total Time"]]
        # 使用 st.dataframe 呈現出類似 Excel 報表的質感
        st.dataframe(df_report, use_container_width=True, hide_index=True)


# ------------------------------------------------------------------
# TAB 2: 日常工具 & 路況
# ------------------------------------------------------------------
with tab2:
    if st.button("🔄 點擊手動更新所有即時資訊 (路況/天氣)", use_container_width=True, key="refresh_tab1"):
        st.cache_data.clear()
        st.rerun()

    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown('<div class="section-title">即時氣溫 & 降雨率</div>', unsafe_allow_html=True)
        weather_html = get_weather_data_html()
        st.markdown(f"""
        <div class="data-box text-cyan">
            {weather_html}
        </div>
        """, unsafe_allow_html=True)

        # 🚌 公車動態區塊
        st.markdown('<div class="section-title">🚌 公車動態</div>', unsafe_allow_html=True)
        bus_col1, bus_col2 = st.columns(2)
        with bus_col1:
            st.link_button("🚌 310", "https://ebus.gov.taipei/EBus/VsSimpleMap?routeid=0100031000&gb=1", use_container_width=True)
        with bus_col2:
            st.link_button("🚌 952", "https://ebus.gov.taipei/EBus/VsSimpleMap?routeid=0400095200&gb=0", use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">即時路況 & 大眾運輸</div>', unsafe_allow_html=True)
        st.markdown('<span style="color:#333; font-size:18px;">※ 點擊下方路況文字可直接開啟 Google 地圖</span>', unsafe_allow_html=True)
        
        base_addr = "新北市板橋區民治街61巷33號"
        
        gmaps_client = None
        if GOOGLE_MAPS_API_KEY and "YOUR_KEY" not in GOOGLE_MAPS_API_KEY:
            try:
                gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
            except:
                pass
        
        # 🚇 捷運 區塊展開 (調整至最上)
        st.markdown('<div class="traffic-section-header">🚇 捷運</div>', unsafe_allow_html=True)
        mrt_target = "捷運中山站"
        txt_go_mrt, cls_go_mrt, url_go_mrt = calculate_traffic(gmaps_client, base_addr, mrt_target, 25, "往中山捷運站", mode='transit')
        txt_back_mrt, cls_back_mrt, url_back_mrt = calculate_traffic(gmaps_client, mrt_target, base_addr, 32, "反江子翠捷運站", mode='transit')
        
        st.markdown(f"""
        <div class="traffic-card">
            <div class="traffic-card-title">中山捷運站 <span style="font-size:16px;">(藍線 > 轉西門綠線 > 中山)</span></div>
            <a href="{url_go_mrt}" target="_blank" class="traffic-row {cls_go_mrt}">{txt_go_mrt}</a>
            <a href="{url_back_mrt}" target="_blank" class="traffic-row {cls_back_mrt}">{txt_back_mrt}</a>
        </div>
        """, unsafe_allow_html=True)

        # 🛵 騎車 區塊展開 (調整至中間)
        st.markdown('<div class="traffic-section-header">🛵 騎車</div>', unsafe_allow_html=True)
        target_locations_bike = [
            ("京樺牛肉麵", "臺北市中山區林森北路259巷9-3號", "反板橋", 15, 15)
        ]
        for name, target_addr, return_label, std_go, std_back in target_locations_bike:
            _, cls_go, url_go = calculate_traffic(gmaps_client, base_addr, target_addr, std_go, "往京樺", mode='two_wheeler')
            _, cls_back, url_back = calculate_traffic(gmaps_client, target_addr, base_addr, std_back, return_label, mode='two_wheeler')
            
            url_go += "&waypoints=" + urllib.parse.quote("台北市民生西路")
            txt_go = "往京樺: 15分 (+0分) 7.9km"
            txt_back = "反板橋: 15分 (+0分) 7.3km"

            st.markdown(f"""
            <div class="traffic-card">
                <div class="traffic-card-title">{name} <span style="font-size:16px;">(途經機慢車專用道和民生西路)</span></div>
                <a href="{url_go}" target="_blank" class="traffic-row {cls_go}">{txt_go}</a>
                <a href="{url_back}" target="_blank" class="traffic-row {cls_back}">{txt_back}</a>
            </div>
            """, unsafe_allow_html=True)
            
        # 🚗 開車 區塊展開 (調整至最下)
        st.markdown('<div class="traffic-section-header">🚗 開車</div>', unsafe_allow_html=True)
        target_locations_car = [
            ("板橋家", "新竹市東區太原路128號", "往新竹", "反板橋", 53, 61),
            ("長榮航空", "桃園縣蘆竹鄉新南路一段376號", "往南崁", "反板橋", 22, 27)
        ]
        for name, target_addr, label_go, label_back, std_go, std_back in target_locations_car:
            txt_go, cls_go, url_go = calculate_traffic(gmaps_client, base_addr, target_addr, std_go, label_go, mode='driving')
            txt_back, cls_back, url_back = calculate_traffic(gmaps_client, target_addr, base_addr, std_back, label_back, mode='driving')
            
            st.markdown(f"""
            <div class="traffic-card">
                <div class="traffic-card-title">{name}</div>
                <a href="{url_go}" target="_blank" class="traffic-row {cls_go}">{txt_go}</a>
                <a href="{url_back}" target="_blank" class="traffic-row {cls_back}">{txt_back}</a>
            </div>
            """, unsafe_allow_html=True)
            
    st.divider()
    col_f1, col_f2 = st.columns([1, 4])
    with col_f1:
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #e74c3c;
                color: white;
                font-size: 18px;
            }
            </style>
        """, unsafe_allow_html=True)
        st.link_button("YouTube 轉 MP3", "https://yt1s.ai/zh-tw/youtube-to-mp3/", use_container_width=True)

    with col_f2:
        st.markdown('<div style="margin-top: 10px; color: #555; font-size: 18px;">← 點擊左側按鈕開啟轉檔</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# TAB 3: 家族時光
# ------------------------------------------------------------------
with tab3:
    st.caption(f"<span style='font-size: 18px;'>今天是 {date.today().strftime('%Y年%m月%d日')}</span>", unsafe_allow_html=True)

    if not st.session_state.family_data:
        st.info("目前沒有資料，請從左側新增成員。")
    else:
        processed_data = []
        for person in st.session_state.family_data:
            b_date = person['birth_date']
            years, total_days = calculate_detailed_age(b_date)
            zodiac_animal = get_chinese_zodiac(b_date.year)
            zodiac_sign = get_western_zodiac(b_date.day, b_date.month)
            lunar_str = get_lunar_date_str(b_date)
            days_to_next = get_next_birthday_days(b_date)
            days_to_next_lunar = get_next_lunar_birthday_days(b_date) 
            
            category = person.get('category', '未分類')

            processed_data.append({
                "姓名": person['name'],
                "家族": category,
                "國曆生日": b_date.strftime("%Y/%m/%d"),
                "農曆": lunar_str,
                "修正農曆": "", 
                "生肖": zodiac_animal,
                "星座": zodiac_sign,
                "歲數": years,
                "總天數": total_days,
                "距離下次生日(天)": days_to_next,
                "距離下次農曆生日(天)": days_to_next_lunar,
                "詳細年齡字串": f"{years} 歲 又 {total_days % 365} 天"
            })

        df = pd.DataFrame(processed_data)
        
        df_birthday_sorted = df.sort_values(by="距離下次生日(天)")
        
        upcoming = df_birthday_sorted.iloc[0]
        
        b_date_obj_upcoming = datetime.strptime(upcoming['國曆生日'], "%Y/%m/%d").date()
        days_mod_upcoming = (date.today() - b_date_obj_upcoming).days % 365
        
        top_col1, top_col2 = st.columns([2, 1])
        
        with top_col1:
            st.markdown('<div class="section-title">🎉 最近的國曆壽星</div>', unsafe_allow_html=True)
            html_card_upcoming = f"""
            <div class="birthday-card top-card-highlight">
                <div class="big-font">
                    {upcoming['姓名']} 
                    <span style="font-size:18px; background-color:#eee; padding:4px 8px; border-radius:4px; margin-left:5px;">{upcoming['家族']}</span>
                    <span style="font-size:16px; color:gray">({upcoming['生肖']})</span>
                </div>
                <hr style="margin: 8px 0;">
                <div class="sub-font">🎂 國曆: {upcoming['國曆生日']}</div>
                <div class="sub-font">🌑 農曆: {upcoming['農曆']}   📝 修正農曆: {upcoming['修正農曆']}</div>
                <div class="sub-font">✨ 星座: {upcoming['星座']}</div>
                <div style="margin-top: 10px;">
                    <span class="highlight">{upcoming['歲數']} 歲</span> 
                    <span style="font-size: 16px; color: #555;">又 {days_mod_upcoming} 天</span>
                </div>
                <div style="margin-top: 10px; font-size: 18px; color: #ff4b4b; font-weight: bold;">
                    ⏳ 距離國曆生日還有: {upcoming['距離下次生日(天)']} 天<br>
                    ⏳ 距離農曆生日還有: {upcoming['距離下次農曆生日(天)']} 天
                </div>
            </div>
            """
            st.markdown(html_card_upcoming, unsafe_allow_html=True)
            
        with top_col2:
            st.write("") 
            st.write("")
            st.metric("👨‍👩‍👧‍👦 家庭成員數", f"{len(df)} 人")

        st.divider()

        st.markdown('<div class="section-title">📋 生日倒數 (下個國曆生日是誰)</div>', unsafe_allow_html=True)
        st.dataframe(
            df_birthday_sorted[["姓名", "家族", "國曆生日", "農曆", "修正農曆", "生肖", "星座", "詳細年齡字串", "距離下次生日(天)", "距離下次農曆生日(天)"]],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.markdown('<div class="section-title">🧓 家族長幼序 (依年齡排序：由上到下)</div>', unsafe_allow_html=True)
        
        df_age_sorted = df.sort_values(by="總天數", ascending=False).reset_index(drop=True)
        sort_order = df_age_sorted['姓名'].tolist()
        
        chart_rendered = False
        
        if alt:
            try:
                domain_colors = ["孟竹家", "標仔家", "其他"]
                range_colors = ["#5DADE2", "#F39C12", "#95A5A6"]

                base = alt.Chart(df_age_sorted).encode(
                    y=alt.Y('姓名:N', sort=sort_order, title=None, axis=alt.Axis(labelFontSize=18, labelFontWeight='bold', labelOverlap=False)), 
                    x=alt.X('歲數:Q', title='年齡 (歲)', axis=alt.Axis(grid=False, labelFontSize=16, titleFontSize=18)), 
                    tooltip=['姓名', '家族', '歲數', '生肖', '國曆生日']
                )

                bars = base.mark_bar(
                    cornerRadiusTopRight=5, 
                    cornerRadiusBottomRight=5,
                    height=30
                ).encode(
                    color=alt.Color('家族:N', 
                                    scale=alt.Scale(domain=domain_colors, range=range_colors), 
                                    legend=alt.Legend(title="家族分類", orient='top', labelFontSize=16, titleFontSize=18))
                )

                text = base.mark_text(
                    align='left',
                    baseline='middle',
                    dx=8,
                    fontSize=18,
                    fontWeight='bold',
                    color='#000000'
                ).encode(
                    text=alt.Text('歲數:Q', format='.0f')
                )
                
                final_chart = (bars + text).properties(
                    title="家族成員年齡分佈",
                    height=len(df_age_sorted) * 55 
                ).configure(
                    background='#ffffff'
                ).configure_title(
                    color='#000000',
                    fontSize=22
                ).configure_axis(
                    labelColor='#000000',
                    titleColor='#000000' 
                ).configure_legend(
                    labelColor='#000000',
                    titleColor='#000000'
                )
                
                st.altair_chart(final_chart, use_container_width=True)
                chart_rendered = True

            except Exception as e:
                st.warning(f"圖表繪製發生錯誤: {e}")
                pass
        else:
             st.warning("未安裝 altair 套件，無法顯示圖表。")

        if not chart_rendered:
            try:
                st.bar_chart(df_age_sorted, x="歲數", y="姓名", color="家族")
            except:
                 st.dataframe(df_age_sorted[["姓名", "家族", "歲數"]])

        st.divider()

        st.markdown('<div class="section-title">📇 詳細資料卡片 (家族分類)</div>', unsafe_allow_html=True)
        
        available_groups = ["全部"] + sorted(list(set(df['家族'].unique())), key=lambda x: FAMILY_GROUPS.index(x) if x in FAMILY_GROUPS else 99)
        
        tabs_family = st.tabs(available_groups)
        
        for i, group_name in enumerate(available_groups):
            with tabs_family[i]:
                if group_name == "全部":
                    current_df = df_birthday_sorted
                else:
                    current_df = df_birthday_sorted[df_birthday_sorted['家族'] == group_name]
                
                if current_df.empty:
                    st.write("此分類尚無成員。")
                else:
                    cols = st.columns(3)
                    for idx, row in current_df.iterrows():
                        loc_idx = current_df.index.get_loc(idx)
                        
                        with cols[loc_idx % 3]:
                            b_date_obj_row = datetime.strptime(row['國曆生日'], "%Y/%m/%d").date()
                            days_mod_row = (date.today() - b_date_obj_row).days % 365

                            html_card = f"""
                            <div class="birthday-card">
                                <div class="big-font">
                                    {row['姓名']} 
                                    <span style="font-size:18px; background-color:#eee; padding:4px 8px; border-radius:4px; margin-left:5px;">{row['家族']}</span>
                                    <span style="font-size:16px; color:gray">({row['生肖']})</span>
                                </div>
                                <hr style="margin: 8px 0;">
                                <div class="sub-font">🎂 國曆: {row['國曆生日']}</div>
                                <div class="sub-font">🌑 農曆: {row['農曆']}   📝 修正農曆: {row['修正農曆']}</div>
                                <div class="sub-font">✨ 星座: {row['星座']}</div>
                                <div style="margin-top: 10px;">
                                    <span class="highlight">{row['歲數']} 歲</span> 
                                    <span style="font-size: 16px; color: #555;">又 {days_mod_row} 天</span>
                                </div>
                                <div style="margin-top: 10px; font-size: 16px; color: #ff4b4b; font-weight: bold;">
                                    距離國曆生日還有: {row['距離下次生日(天)']} 天<br>
                                    距離農曆生日還有: {row['距離下次農曆生日(天)']} 天
                                </div>
                            </div>
                            """
                            st.markdown(html_card, unsafe_allow_html=True)
