# My code is shit.
# Main file for TaiwanBus.
import sys
import argparse
import taiwanbus.exceptions
import taiwanbus.api as api

__version__ = "0.1.0"


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
        api.update_provider(api.Provider(args.provider))
        if not api.DATABASE_ACCESSIBLE:
            raise taiwanbus.exceptions.DatabaseNotFoundError(
                "無法存取資料庫，請檢查資料庫目錄權限。"
            )
        if args.cmd == "updatedb":
            if args.checkonly:
                print("正在檢查更新...")
                updates = api.check_database_update()
                for p in updates.keys():
                    if updates[p]:
                        print(f"資料庫 {p} 有新的更新！版本：{updates[p]}")
                if not any(updates.values()):
                    print("資料庫目前沒有可用的更新。")
            else:
                print("正在更新資料庫...")
                api.update_database(info=True)
                print("資料庫更新成功。")

        elif args.cmd == "showroute":
            data = api.get_complete_bus_info(args.routeid)
            print(api.format_bus_info(data))

        elif args.cmd == "searchroute":
            rs = api.fetch_routes_by_name(args.routename)
            for r in rs:
                print(r["route_key"], r["route_name"], r["description"])

        elif args.cmd == "searchstop":
            stops = api.fetch_stops_by_name(args.stopname)
            for stop in stops:
                route = api.fetch_route(stop["route_key"])[0]
                paths = api.fetch_paths(stop["route_key"])
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
