from math import hypot
from typing import Dict, List, Tuple, Any


# ---- ユーティリティ ----
def _dist_xy(ax: float, ay: float, bx: float, by: float) -> float:
    return hypot(ax - bx, ay - by)

def _pair_dist(stations_xy: List[Tuple[float, float]], i: int, j: int) -> float:
    (xi, yi), (xj, yj) = stations_xy[i], stations_xy[j]
    return _dist_xy(xi, yi, xj, yj)

# ---- 最近傍初期化 ----
def _nearest_neighbor_order(stations_xy: List[Tuple[float, float]], start: int = 0) -> List[int]:
    n = len(stations_xy)
    unvis = set(range(n))
    tour = [start]
    unvis.remove(start)
    while unvis:
        v = tour[-1]
        nxt = min(unvis, key=lambda u: _pair_dist(stations_xy, v, u))
        tour.append(nxt)
        unvis.remove(nxt)
    return tour  # 閉路は暗黙（最後→最初を結ぶ）

# ---- 2-opt ----
def _two_opt(stations_xy: List[Tuple[float, float]], tour: List[int], eps: float = 1e-12) -> List[int]:
    n = len(tour)
    if n <= 3:
        return tour
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            a, b = tour[i], tour[(i + 1) % n]
            # i==0 のとき最終辺との重複を避けるため k の上限を n-1 に
            k_max = n if i > 0 else n - 1
            for k in range(i + 2, k_max):
                c, d = tour[k], tour[(k + 1) % n]
                old = _pair_dist(stations_xy, a, b) + _pair_dist(stations_xy, c, d)
                new = _pair_dist(stations_xy, a, c) + _pair_dist(stations_xy, b, d)
                if new + eps < old:
                    # 区間 [i+1, k] を反転（2-opt スワップ）
                    tour[i + 1 : k + 1] = reversed(tour[i + 1 : k + 1])
                    improved = True
    return tour

# ---- 公開関数：辞書 {key: station} を入力にして、キー順の巡回を返す ----
def solve_tsp_cycle(stations: Dict[str, Any], start_key: str = None):
    """
    stations: {'staion_i': station, ...}  （station は .x, .y を持つ）
    start_key: 開始ノードのキー（省略時は辞書の最初のキー）
    返り値: (tour_keys: List[str], tour_length: float)
            tour_keys は閉路順。描画時は最後と最初を結んで輪にする。
    """
    if not stations:
        return [], 0.0

    keys: List[str] = list(stations.keys())
    key_to_idx = {k: i for i, k in enumerate(keys)}

    # (x,y) の配列に投影
    xy: List[Tuple[float, float]] = [(stations[k].x, stations[k].y) for k in keys]

    # 開始インデックス
    start_idx = 0 if start_key is None else key_to_idx[start_key]

    # 初期解 → 2-opt で改良
    order_idx = _nearest_neighbor_order(xy, start=start_idx)
    order_idx = _two_opt(xy, order_idx)

    # 距離の計算（閉路）
    n = len(order_idx)
    tour_len = 0.0
    for i in range(n):
        a, b = order_idx[i], order_idx[(i + 1) % n]
        tour_len += _pair_dist(xy, a, b)

    # インデックス順をキー順に変換
    tour_keys: List[str] = [keys[i] for i in order_idx]
    return tour_keys, tour_len

# ---- 使い方例（Stationは .x, .y を持つ想定）----
if __name__ == "__main__":
    from main import Station
    stations = {
        'staion_a': Station('station_a', 'circle', 0.1, 0.3),
        'staion_b': Station('station_b', 'circle', 0.9, 0.2),
        'staion_c': Station('station_c', 'circle', 0.2, 0.9),
        'staion_d': Station('station_d', 'circle', 0.7, 0.8),
    }
    tour_keys, length = solve_tsp_cycle(stations, start_key='staion_a')
    print("order keys:", tour_keys)
    print("tour length:", length)
    # 可視化や線の描画は tour_keys をこの順で結び、最後→最初をつなげばOK
