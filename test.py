import http.server
import socketserver
import webbrowser
import threading
import json
import requests
import time

# ===================== 配置区 =====================
AMAP_WEB_KEY = ""
AMAP_JS_KEY = ""
AMAP_JS_SECURITY = ""

PORT = 8000
# =================================================

# 泸州区县列表
DISTRICTS = [
    "江阳区", "龙马潭区", "纳溪区",
    "泸县", "合江县", "叙永县", "古蔺县",
    "泸州市",
]

# 关键词变体：覆盖不同运营商和叫法
KEYWORDS_LIST = [
    "充电站", "充电桩", "快充站", "充电",
    "特来电", "国家电网充电", "星星充电", "小桔充电",
    "蔚来充电", "特斯拉充电", "云快充", "依威能源",
]


def search_poi(keyword, city, page_limit=10):
    """单个关键词+城市搜索，最多翻 page_limit 页（每页20条）"""
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
            print(f"  [请求异常] {city} / {keyword} / 第{page}页: {e}")
            break

        if r.get("status") != "1":
            print(f"  [API错误] {city} / {keyword}: {r.get('info')}")
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
    """遍历区县 × 关键词，合并去重"""
    all_pois = []
    seen_ids = set()

    for city in DISTRICTS:
        for kw in KEYWORDS_LIST:
            pois = search_poi(kw, city)
            new_count = 0
            for p in pois:
                pid = p.get("id", "")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    all_pois.append(p)
                    new_count += 1
            if new_count:
                print(f"{city} / {kw}: 新增 {new_count} 条（累计 {len(all_pois)}）")
            time.sleep(0.3)  # 控制频率

    # 提取名称和经纬度
    chargers = []
    for p in all_pois:
        loc = p.get("location", "")
        name = p.get("name", "未知")
        address = p.get("address", "")
        if "," in loc:
            lng, lat = loc.split(",")
            try:
                chargers.append({
                    "name": name,
                    "address": address,
                    "lng": float(lng),
                    "lat": float(lat),
                })
            except ValueError:
                continue

    print(f"\n总计获取到 {len(chargers)} 个充电站/桩")
    return chargers


def build_html(chargers):
    points_json = json.dumps(
        [{"name": c["name"], "addr": c["address"], "lnglat": [c["lng"], c["lat"]]}
         for c in chargers],
        ensure_ascii=False
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>泸州充电桩分布</title>
    <style>
        html, body, #container {{ width:100%; height:100%; margin:0; }}
        #info {{ position:absolute; top:10px; left:10px; background:#fff; padding:10px 16px;
                border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,.25); font:14px sans-serif; z-index:10; }}
        #info b {{ color:#007bff; font-size:18px; }}
    </style>
</head>
<body>
    <div id="info">泸州充电站总数：<b>{len(chargers)}</b></div>
    <div id="container"></div>
    <script>
        window._AMapSecurityConfig = {{ securityJsCode: "{AMAP_JS_SECURITY}" }};
    </script>
    <script src="https://webapi.amap.com/maps?v=2.0&key={AMAP_JS_KEY}"></script>
    <script>
        var map = new AMap.Map("container", {{
            zoom: 10,
            center: [105.443, 28.871],
            mapStyle: "amap://styles/whitesmoke"
        }});
        var points = {points_json};

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
                    // 点击弹窗
                    ctx.marker.on('click', function () {{
                        var p = ctx.data.data;
                        var info = new AMap.InfoWindow({{
                            content: '<b>' + p.name + '</b><br>' + (p.addr || ''),
                            offset: new AMap.Pixel(0, -20)
                        }});
                        info.open(map, ctx.marker.getPosition());
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>"""
    return html


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.chargers = kwargs.pop("chargers")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            content = build_html(self.chargers).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


def main():
    print("开始抓取泸州充电桩数据……\n")
    chargers = fetch_all_chargers()
    if not chargers:
        print("未获取到数据，请检查 Web 服务 Key。")
        return

    # 同时存一份 JSON，方便后续用
    with open("chargers.json", "w", encoding="utf-8") as f:
        json.dump(chargers, f, ensure_ascii=False, indent=2)
    print("数据已保存到 chargers.json")

    handler = lambda *a, **kw: Handler(*a, chargers=chargers, **kw)
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"\n地图已启动：{url}")
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        httpd.serve_forever()


if __name__ == "__main__":
    main()