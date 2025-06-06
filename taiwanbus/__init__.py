# My code is shit.
# Main file for TaiwanBus.
import os
import sys
import requests
import zlib
import math
import xml.etree.ElementTree as et
import aiosqlite
import json
import asyncio
import argparse
import taiwanbus.exceptions
import taiwanbus.cache as cache
from pathlib import Path
from enum import Enum

__version__ = "0.0.9"

DATABASE_ACCESSIBLE = None
home = os.path.join(Path.home(), ".taiwanbus")
try:
    if not os.path.exists(home):
        os.mkdir(home)
    testfile = os.path.join(home, ".tmp")
    with open(testfile, "w") as f:
        f.write("test")
    os.remove(testfile)
    DATABASE_ACCESSIBLE = True
except Exception:
    DATABASE_ACCESSIBLE = False
current = os.path.join(home, "bus_twn.sqlite")


class Provider(Enum):
    TWN = "twn"
    TCC = "tcc"
    TPE = "tpe"


def update_database_dir(path) -> bool:
    global home
    global current
    global DATABASE_ACCESSIBLE
    home = os.path.join(path, ".taiwanbus")
    try:
        if not os.path.exists(home):
            os.mkdir(home)
        testfile = os.path.join(home, ".tmp")
        with open(testfile, "w") as f:
            f.write("test")
        os.remove(testfile)
        DATABASE_ACCESSIBLE = True
    except Exception:
        DATABASE_ACCESSIBLE = False
    provider_file = os.path.basename(current)
    current = os.path.join(home, provider_file)
    return DATABASE_ACCESSIBLE


def update_provider(provider: Provider) -> None:
    global current
    current = os.path.join(home, f"bus_{provider.value}.sqlite")


def check_database_update(path=None) -> dict:
    if not path:
        path = home
    local = {"tcc": 0, "tpe": 0, "twn": 0}
    version_path = os.path.join(path, "version.json")
    if os.path.exists(version_path):
        local = json.loads(open(version_path, "r").read())
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl_tcc.txt"
    ).text
    if local["tcc"] < int(baseurl.split("/")[-2]):
        local["tcc"] = int(baseurl.split("/")[-2])
    else:
        local["tcc"] = False
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl_tpe.txt"
    ).text
    if local["tpe"] < int(baseurl.split("/")[-2]):
        local["tpe"] = int(baseurl.split("/")[-2])
    else:
        local["tpe"] = False
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl.txt"
    ).text
    if local["twn"] < int(baseurl.split("/")[-2]):
        local["twn"] = int(baseurl.split("/")[-2])
    else:
        local["twn"] = False
    return local


def update_database(path=None, info=False):
    if not path:
        path = home
    local = {"tcc": 0, "tpe": 0, "twn": 0}
    version_path = os.path.join(path, "version.json")
    if os.path.exists(version_path):
        try:
            local = json.load(open(version_path, "r"))
        except json.JSONDecodeError:
            local = {"tcc": 0, "tpe": 0, "twn": 0}
    if info:
        print("取得台中版本資訊...")
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl_tcc.txt"
    ).text
    if local["tcc"] < int(baseurl.split("/")[-2]):
        if info:
            print("下載台中版資料庫...")
        r = requests.get(baseurl + "dat_tcc_zh.gz")
        if info:
            print("正在解壓縮...")
        open(os.path.join(path, "bus_tcc.sqlite"), "wb").write(
            zlib.decompress(r.content)
        )
        local["tcc"] = int(baseurl.split("/")[-2])
    if info:
        print("取得台北版本資訊...")
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl_tpe.txt"
    ).text
    if local["tpe"] < int(baseurl.split("/")[-2]):
        if info:
            print("下載台北版資料庫...")
        r = requests.get(baseurl + "dat_tpe_zh.gz")
        if info:
            print("正在解壓縮...")
        open(os.path.join(home, "bus_tpe.sqlite"), "wb").write(
            zlib.decompress(r.content)
        )
        local["tpe"] = int(baseurl.split("/")[-2])
    if info:
        print("取得全台版本資訊...")
    baseurl = requests.get(
        "https://files.bus.yahoo.com/bustracker/data/dataurl.txt"
    ).text
    if local["twn"] < int(baseurl.split("/")[-2]):
        if info:
            print("下載全台版資料庫（無站點資訊）...")
        r = requests.get(baseurl + "dat_twn_zh.gz")
        if info:
            print("正在解壓縮...")
        open(os.path.join(home, "bus_twn.sqlite"), "wb").write(
            zlib.decompress(r.content)
        )
        local["twn"] = int(baseurl.split("/")[-2])
    open(version_path, "w").write(json.dumps(local))


def checkdb(path=None, only_stop=False) -> None:
    if not path:
        path = current
    if not os.path.exists(path):
        raise taiwanbus.exceptions.DatabaseNotFoundError(
            "Cannot find database")
    if "bus_twn.sqlite" in path and only_stop:
        raise taiwanbus.exceptions.UnsupportedDatabaseError(
            "No stops data in twn")


async def fetch_route(id: int) -> list:
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM routes WHERE route_key = ?", (id, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_all_routes() -> list:
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute("SELECT * FROM routes") as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_routes_by_name(name: str) -> list:
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM routes WHERE route_name LIKE ?",
                ('%' + name + '%', )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stops_by_name(name: str) -> list:
    checkdb(only_stop=True)
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE stop_name LIKE ?", ('%' + name + '%', )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stop(id: int) -> list:
    checkdb(only_stop=True)
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE stop_id = ?", (id, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_paths(id: int) -> list:
    checkdb()
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM paths WHERE route_key = ?", (id, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_path_by_stop(id: int) -> list:
    checkdb()
    stop = await fetch_stop(id)
    pathid = stop[0]["path_id"]
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM paths WHERE route_key = ? and path_id = ?",
            (stop[0]["route_key"], pathid, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stops_by_route(route_key: int) -> list:
    checkdb()
    if "bus_twn.sqlite" in current:
        r = requests.get(
            f"https://files.bus.yahoo.com/bustracker/routes/{route_key}_zh.dat"
        )
        d = zlib.decompress(r.content).decode()
        x = et.XML(d)
        ss = []
        for r in x:
            rk = 0
            for ri in r.items():
                if ri[0] == "key":
                    rk = int(ri[1])
            for p in r:
                pid = 0
                for pi in p.items():
                    if pi[0] == "id":
                        pid = int(pi[1])
                for s in p:
                    j = {}
                    j["route_key"] = rk
                    j["path_id"] = pid
                    for si in s.items():
                        if si[0] == "id":
                            j["stop_id"] = int(si[1])
                        elif si[0] == "nm":
                            j["stop_name"] = si[1]
                        elif si[0] == "seq":
                            j["sequence"] = int(si[1])
                        else:
                            j[si[0]] = si[1]
                    ss.append(j)
        return ss
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE route_key = ?", (route_key, )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stops_nearby(
        lat: float,
        lon: float,
        radius: int = 100
) -> list:
    checkdb(only_stop=True)
    async with aiosqlite.connect(current) as db:
        async with db.execute(
            "SELECT * FROM stops WHERE "
            "ABS(latitude - ?) <= ? AND "
            "ABS(longitude - ?) <= ?",
            (lat,
             radius / 111320,
             lon,
             radius / (111320 * abs(math.cos(math.radians(lat))))
             )
        ) as cursor:
            columns = [description[0] for description in cursor.description]
            result = []
            async for row in cursor:
                row_dict = dict(zip(columns, row))
                result.append(row_dict)
            return result


async def fetch_stops_passby(stop_id: int, radius: int = 100) -> list:
    checkdb(only_stop=True)
    stop = await fetch_stop(stop_id)
    if not stop:
        return []
    lat = stop[0]['latitude']
    lon = stop[0]['longitude']
    return await fetch_stops_nearby(lat, lon, radius)


def getbus(id) -> list:
    if cache.get_cache("API" + id):
        return cache.get_cache("API" + id)
    else:
        r = requests.get(f"https://busserver.bus.yahoo.com/api/route/{id}")
        d = zlib.decompress(r.content).decode()
        x = et.XML(d)
        j = []
        for e in x:
            t = {}
            for a in e.items():
                t[a[0]] = a[1]
            t["bus"] = []
            for ec in e:
                b = {}
                for a in ec.items():
                    b[a[0]] = a[1]
                t["bus"].append(b)
            j.append(t)
        cache.set_cache("API" + id, j, expire_time=1)
        return j


async def get_complete_bus_info(route_key) -> dict:
    # route_info = await fetch_route(route_key)
    if cache.get_cache(route_key):
        paths, stops = cache.get_cache(route_key)
    else:
        paths = await fetch_paths(route_key)
        stops = await fetch_stops_by_route(route_key)
        cache.set_cache(route_key, (paths, stops), expire_time=600)
    try:
        buses = getbus(route_key)
    except Exception as e:
        print("[WARN]無法取得公車資訊，可能是網路問題或API服務異常。", e)
        buses = []
    result = {}

    for path in paths:
        path_id = int(path['path_id'])
        path_name = path['path_name']
        path_stops = []
        for stop in stops:
            if path_id == stop["path_id"]:
                stop_id = str(stop['stop_id'])
                if buses:
                    matching_buses = [
                        bus for bus in buses if bus['id'] == stop_id
                    ]
                if matching_buses:
                    bus_info = matching_buses[0]
                    stop.update({
                        "sec": int(bus_info["sec"]),
                        "msg": bus_info["msg"],
                        "t": bus_info["t"],
                        "lon": bus_info["lon"],
                        "lat": bus_info["lat"],
                        "bus": bus_info["bus"]
                    })
                path_stops.append(stop)
        result[path_id] = {
            "route_key": route_key,
            "name": path_name,
            "stops": path_stops
        }

    for path_id, path_data in result.items():
        path_data['stops'] = sorted(
            path_data['stops'],
            key=lambda x: x['sequence'])

    return result


def format_bus_info(json_data: dict) -> str:
    result = ""

    for path_id, path_data in json_data.items():
        route_name = path_data["name"]
        result += f"{route_name}\n"

        stops = path_data["stops"]
        for i, stop in enumerate(stops):
            stop_name = stop["stop_name"].strip()
            msg = stop["msg"]
            sec = stop["sec"]
            buses = stop["bus"]

            if msg:
                stop_info = f"{stop_name} {msg}\n"
            elif sec and int(sec) > 0:
                minutes = int(sec) // 60
                seconds = int(sec) % 60
                stop_info = f"{stop_name} 還有{minutes}分{seconds}秒\n"
            else:
                stop_info = f"{stop_name} 進站中\n"

            # 添加公車資訊
            if buses:
                for bus in buses:
                    bus_id = bus["id"]
                    bus_full = "已滿" if bus["full"] == "1" else "未滿"
                    stop_info += f" │  └── {bus_id} {bus_full}\n"

            # 使用適當的分隔符顯示站點結構
            if i == len(stops) - 1:
                result += f" └──{stop_info}"
            else:
                result += f" ├──{stop_info}"

    return result


def main():
    parser = argparse.ArgumentParser(description="TaiwanBus")
    subparsers = parser.add_subparsers(
        dest="cmd", required=True
    )
    parser.add_argument(
        "-p", "--provider",
        help="區域資料庫",
        dest="provider",
        default="twn",
        type=str
    )
    parser_updatedb = subparsers.add_parser("updatedb", help="更新公車資料庫")
    parser_updatedb.add_argument(
        "-c",
        "--check-only",
        dest="checkonly",
        action='store_true',
        default=False
    )
    parser_showroute = subparsers.add_parser("showroute", help="顯示公車路線狀態")
    parser_searchroute = subparsers.add_parser("searchroute", help="查詢路線")
    parser_searchstop = subparsers.add_parser("searchstop", help="查詢站點")
    parser_showroute.add_argument("routeid", help="路線ID", type=int)
    parser_searchroute.add_argument("routename", help="路線名", type=str)
    parser_searchstop.add_argument("stopname", help="站點名", type=str)
    args = parser.parse_args()

    try:
        update_provider(Provider(args.provider))
        if not DATABASE_ACCESSIBLE:
            raise taiwanbus.exceptions.DatabaseNotFoundError(
                "無法存取資料庫，請檢查資料庫目錄權限。"
            )
        if args.cmd == "updatedb":
            if args.checkonly:
                print("正在檢查更新...")
                updates = check_database_update()
                for p in updates.keys():
                    if updates[p]:
                        print(f"資料庫 {p} 有新的更新！版本：{updates[p]}")
                if not any(updates.values()):
                    print("資料庫目前沒有可用的更新。")
            else:
                print("正在更新資料庫...")
                update_database(info=True)
                print("資料庫更新成功。")

        elif args.cmd == "showroute":
            data = asyncio.run(get_complete_bus_info(args.routeid))
            print(format_bus_info(data))

        elif args.cmd == "searchroute":
            rs = asyncio.run(fetch_routes_by_name(args.routename))
            for r in rs:
                print(r["route_key"], r["route_name"], r["description"])

        elif args.cmd == "searchstop":
            stops = asyncio.run(fetch_stops_by_name(args.stopname))
            for stop in stops:
                route = asyncio.run(fetch_route(stop["route_key"]))[0]
                paths = asyncio.run(fetch_paths(stop["route_key"]))
                cpath = None
                for p in paths:
                    if stop["path_id"] == p["path_id"]:
                        cpath = p
                print(
                    f"{route['provider']} "
                    f"{route['route_name']}[{route['route_key']}] "
                    f"{cpath['path_name']}[{cpath['path_id']}] "
                    f"{stop['stop_name']}[{stop['stop_id']}]"
                )

        else:
            print("使用", sys.argv[0], "來取得幫助。")

    except Exception as e:
        print("錯誤！")
        print(e)
