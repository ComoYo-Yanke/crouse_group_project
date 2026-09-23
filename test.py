import http.server
import socketserver
import webbrowser
import threading
import json
import os
import requests
import time
from collections import Counter

# ===================== 配置区 =====================
with open("test.config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

AMAP_WEB_KEY = config[0]["web_key"]
AMAP_JS_KEY = config[0]["js_key"]
AMAP_JS_SECURITY = config[0]["js_security"]

PORT = 8000
DATA_FILE = "chargers.json"
# =================================================

DISTRICTS = [
    "江阳区", "龙马潭区", "纳溪区",
    "泸县", "合江县", "叙永县", "古蔺县",
    "泸州市",
]

KEYWORDS_LIST = [
    "充电站", "充电桩", "快充站", "充电",
    "特来电", "国家电网充电", "星星充电", "小桔充电",
    "蔚来充电", "特斯拉充电", "云快充", "依威能源",
]


def search_poi(keyword, city, page_limit=10):
    url = "https://restapi.amap.com/v3/place/text"
    results = []
    for page in range(1, page_limit + 1):
        params = {
            "key": AMAP_WEB_KEY,
            "keywords": keyword,
            "city": city,
            "citylimit": "true",
            "offset": 20,
            "page": page,
            "extensions": "base",
        }
        try:
            r = requests.get(url, params=params, timeout=10).json()
        except Exception as e:
            print(f"  [请求异常] {city}/{keyword}/p{page}: {e}")
            break
        if r.get("status") != "1":
            print(f"  [API错误] {city}/{keyword}: {r.get('info')}")
            break
        pois = r.get("pois", [])
        if not pois:
            break
        results.extend(pois)
        if len(pois) < 20:
            break
        time.sleep(0.2)
    return results


def fetch_all_chargers():
    all_pois = []
    seen_ids = set()
    for city in DISTRICTS:
        for kw in KEYWORDS_LIST:
            pois = search_poi(kw, city)
            new = 0
            for p in pois:
                pid = p.get("id", "")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    all_pois.append(p)
                    new += 1
            if new:
                print(f"{city}/{kw}: 新增 {new}（累计 {len(all_pois)}）")
            time.sleep(0.3)

    chargers = []
    for p in all_pois:
        loc = p.get("location", "")
        name = p.get("name", "未知")
        address = p.get("address", "")
        district = p.get("adname", "") or "未知区域"
        if "," in loc:
            lng, lat = loc.split(",")
            try:
                chargers.append({
                    "name": name,
                    "address": address,
                    "district": district,
                    "lng": float(lng),
                    "lat": float(lat),
                })
            except ValueError:
                continue

    print(f"\n总计 {len(chargers)} 个充电站")
    return chargers


def load_or_fetch():
    """有本地缓存就直接读，没有才去抓"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            chargers = json.load(f)
        print(f"从本地 {DATA_FILE} 读取到 {len(chargers)} 个充电站")
        return chargers
    print("本地无缓存，开始抓取……\n")
    chargers = fetch_all_chargers()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chargers, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {DATA_FILE}")
    return chargers


def build_html(chargers):
    points_json = json.dumps(
        [{"name": c["name"], "addr": c["address"], "d": c["district"],
          "lnglat": [c["lng"], c["lat"]]} for c in chargers],
        ensure_ascii=False
    )

    district_counter = Counter(c["district"] for c in chargers)
    district_labels_js = json.dumps(list(district_counter.keys()), ensure_ascii=False)
    district_values_js = json.dumps(list(district_counter.values()))

    fast_kw = ["快充", "特来电", "星星充电", "小桔", "云快充", "特斯拉", "蔚来"]
    slow_kw = ["慢充", "小区", "物业"]
    fast = sum(1 for c in chargers if any(k in c["name"] for k in fast_kw))
    slow = sum(1 for c in chargers if any(k in c["name"] for k in slow_kw))
    other = len(chargers) - fast - slow

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>泸州充电站分布</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        html, body {{ margin:0; height:100%; font-family: -apple-system, "Microsoft YaHei", sans-serif; }}
        #app {{ display:flex; height:100%; }}
        #panel {{
            width: 360px; min-width: 320px; height:100%;
            overflow-y:auto; background:#f7f9fc;
            border-right:1px solid #e0e6ed; padding:16px;
        }}
        #panel h2 {{ font-size:17px; margin:0 0 12px; color:#1a2b4a; }}
        #refreshBtn {{
            width:100%; padding:10px; margin-bottom:16px;
            background:#007bff; color:#fff; border:none; border-radius:8px;
            font-size:14px; cursor:pointer; transition:background .2s;
        }}
        #refreshBtn:hover {{ background:#0069d9; }}
        #refreshBtn:disabled {{ background:#9aa8bd; cursor:not-allowed; }}
        .cards {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:18px; }}
        .card {{
            background:#fff; border-radius:10px; padding:12px 14px;
            box-shadow:0 1px 4px rgba(0,0,0,.06);
        }}
        .card .num {{ font-size:24px; font-weight:700; color:#007bff; }}
        .card .label {{ font-size:12px; color:#7a8ba6; margin-top:4px; }}
        .chart-box {{
            background:#fff; border-radius:10px; padding:12px;
            box-shadow:0 1px 4px rgba(0,0,0,.06); margin-bottom:16px;
        }}
        .chart-box h3 {{ font-size:13px; margin:0 0 8px; color:#4a5a72; font-weight:600; }}
        .chart-box canvas {{ width:100% !important; }}
        .note {{ font-size:11px; color:#9aa8bd; line-height:1.6; }}
        #map-wrap {{ flex:1; position:relative; }}
        #container {{ width:100%; height:100%; }}
    </style>
</head>
<body>
<div id="app">
    <div id="panel">
        <h2>泸州充电站统计</h2>
        <button id="refreshBtn" onclick="refreshData()">🔄 重新获取数据</button>

        <div class="cards">
            <div class="card">
                <div class="num">{len(chargers)}</div>
                <div class="label">充电站总数（个）</div>
            </div>
            <div class="card">
                <div class="num">{len(district_counter)}</div>
                <div class="label">覆盖区县数</div>
            </div>
            <div class="card">
                <div class="num">{fast}</div>
                <div class="label">快充相关站点</div>
            </div>
            <div class="card">
                <div class="num">{other}</div>
                <div class="label">其他/未分类</div>
            </div>
        </div>
        <div class="chart-box">
            <h3>各区县充电站数量</h3>
            <canvas id="pieChart" height="220"></canvas>
        </div>
        <div class="chart-box">
            <h3>站点类型分布（按名称粗分）</h3>
            <canvas id="barChart" height="180"></canvas>
        </div>
        <div class="note">
            注：高德 POI 接口返回的是“充电站”点位，不含站内充电桩数量。
            桩级数据需接入运营商开放平台。
        </div>
    </div>
    <div id="map-wrap">
        <div id="container"></div>
    </div>
</div>

<script>
    window._AMapSecurityConfig = {{ securityJsCode: "{AMAP_JS_SECURITY}" }};
</script>
<script src="https://webapi.amap.com/maps?v=2.0&key={AMAP_JS_KEY}"></script>
<script>
    var points = {points_json};
    var map = new AMap.Map("container", {{
        zoom: 10,
        center: [105.443, 28.871],
        mapStyle: "amap://styles/whitesmoke"
    }});
    map.plugin(["AMap.MarkerCluster"], function () {{
        new AMap.MarkerCluster(map, points, {{
            gridSize: 80,
            renderClusterMarker: function (ctx) {{
                ctx.marker.setContent(
                    '<div style="background:#007bff;color:#fff;border-radius:50%;' +
                    'width:40px;height:40px;line-height:40px;text-align:center;' +
                    'font:bold 14px sans-serif;box-shadow:0 2px 6px rgba(0,0,0,.3);">' +
                    ctx.count + '</div>');
                ctx.marker.setOffset(new AMap.Pixel(-20, -20));
            }},
            renderMarker: function (ctx) {{
                ctx.marker.setContent(
                    '<div style="background:#28a745;color:#fff;border-radius:50%;' +
                    'width:26px;height:26px;line-height:26px;text-align:center;' +
                    'font:bold 13px sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.3);">⚡</div>');
                ctx.marker.setOffset(new AMap.Pixel(-13, -13));
                ctx.marker.on('click', function () {{
                    var p = ctx.data.data;
                    var info = new AMap.InfoWindow({{
                        content: '<b>' + p.name + '</b><br>' +
                                 '<span style="color:#888;font-size:12px;">' +
                                 (p.d || '') + ' ' + (p.addr || '') + '</span>',
                        offset: new AMap.Pixel(0, -22)
                    }});
                    info.open(map, ctx.marker.getPosition());
                }});
            }}
        }});
    }});

    var dLabels = {district_labels_js};
    var dValues = {district_values_js};
    new Chart(document.getElementById('pieChart'), {{
        type: 'pie',
        data: {{
            labels: dLabels,
            datasets: [{{
                data: dValues,
                backgroundColor: [
                    '#007bff','#28a745','#ffc107','#dc3545','#6f42c1',
                    '#17a2b8','#fd7e14','#20c997','#e83e8c'
                ]
            }}]
        }},
        options: {{
            plugins: {{
                legend: {{ position: 'bottom', labels: {{ font: {{ size: 11 }} }} }}
            }}
        }}
    }});

    new Chart(document.getElementById('barChart'), {{
        type: 'bar',
        data: {{
            labels: ['快充相关', '慢充相关', '其他/未分类'],
            datasets: [{{
                data: [{fast}, {slow}, {other}],
                backgroundColor: ['#28a745', '#ffc107', '#adb5bd']
            }}]
        }},
        options: {{
            indexAxis: 'y',
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
                x: {{ beginAtZero: true, ticks: {{ precision: 0 }} }}
            }}
        }}
    }});

    // ===== 重新获取按钮 =====
    function refreshData() {{
        var btn = document.getElementById('refreshBtn');
        btn.disabled = true;
        btn.textContent = '⏳ 正在获取，请稍候…';
        fetch('/refresh')
            .then(function (r) {{ return r.json(); }})
            .then(function (data) {{
                if (data.ok) {{
                    btn.textContent = '✅ 获取完成，刷新中…';
                    location.reload();
                }} else {{
                    alert('获取失败：' + (data.msg || '未知错误'));
                    btn.disabled = false;
                    btn.textContent = '🔄 重新获取数据';
                }}
            }})
            .catch(function (e) {{
                alert('请求出错：' + e);
                btn.disabled = false;
                btn.textContent = '🔄 重新获取数据';
            }});
    }}
</script>
</body>
</html>"""
    return html


# 全局缓存，供 Handler 使用
CURRENT_CHARGERS = []


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global CURRENT_CHARGERS

        if self.path in ("/", "/index.html"):
            content = build_html(CURRENT_CHARGERS).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == "/refresh":
            # 触发重新抓取
            try:
                print("\n手动触发重新获取……")
                chargers = fetch_all_chargers()
                if chargers:
                    CURRENT_CHARGERS = chargers
                    with open(DATA_FILE, "w", encoding="utf-8") as f:
                        json.dump(chargers, f, ensure_ascii=False, indent=2)
                    resp = json.dumps({"ok": True, "count": len(chargers)}).encode()
                else:
                    resp = json.dumps({"ok": False, "msg": "未获取到数据"}).encode()
            except Exception as e:
                resp = json.dumps({"ok": False, "msg": str(e)}).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resp)))
            self.end_headers()
            self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    global CURRENT_CHARGERS
    CURRENT_CHARGERS = load_or_fetch()

    if not CURRENT_CHARGERS:
        print("没有数据，程序退出。")
        return

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n地图已启动：{url}")
        print("点击页面上的「重新获取数据」可手动刷新")
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        httpd.serve_forever()


if __name__ == "__main__":
    main()