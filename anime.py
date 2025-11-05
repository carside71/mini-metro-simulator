import argparse
import math
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
from matplotlib import patches, transforms


SHAPE_TO_MARKER = {
    "circle": "o",
    "triangle": "^",
    "square": "s",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Simple CLI example")
    # 位置引数：メッセージ（省略時は既定文言）
    parser.add_argument("path", type=str, help="the output dir path of python main.py")
    parser.add_argument("--fps", type=int, default=10, help="animation frame per seconds")
    # parser.add_argument("--fps", type=int, default=24, help="animation frame per seconds")
    return parser.parse_args()


def load_records(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]
    return [json.loads(ln) for ln in lines]


def draw_frame(ax, rec):
    ax.cla()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"clock = {rec.get('clock')}")

    stations = rec.get("stations", {})
    trains = rec.get("trains", {})
    lines = rec.get("lines", {})
    passengers = rec.get("passengers", {})

    # 路線（駅座標を結ぶ）
    for _, line in lines.items():
        route = line.get("route", [])
        xs, ys = [], []
        for sid in route:
            st = stations.get(sid)
            if st is None:
                continue
            xs.append(st["x"])
            ys.append(st["y"])
        if len(xs) >= 2:
            # 環状路線は最初の駅を末尾に追加
            xs.append(xs[0])
            ys.append(ys[0])
            # 描画
            ax.plot(xs, ys, color='gray', linewidth=4)

    # 駅（形状別にマーカーを変える）
    # 形状が未知のものは丸にする
    buckets = {}
    for sid, st in stations.items():
        marker = SHAPE_TO_MARKER.get(st.get("shape_type"), "o")
        buckets.setdefault(marker, {"x": [], "y": []})
        buckets[marker]["x"].append(st["x"])
        buckets[marker]["y"].append(st["y"])
    for marker, pts in buckets.items():
        ax.scatter(pts["x"], pts["y"], marker=marker, s=100, zorder=3)

    # 列車：進行方向を向いた長方形で描画
    # JSON想定フィールド: x, y, dist_vector_x, dist_vector_y
    # 単位はキャンバス(0..1)。サイズは見やすいように固定値。
    train_len = 0.05   # 長辺（進行方向）
    train_wid = 0.02   # 短辺（車幅）
    for _, t in trains.items():
        x = t.get("x"); y = t.get("y")
        dx = t.get("dist_vector_x", 0.0)
        dy = t.get("dist_vector_y", 0.0)

        if x is None or y is None:
            continue

        # 角度（ラジアン→度）。ベクトルがゼロなら角度0にフォールバック。
        if dx == 0 and dy == 0:
            theta_deg = 0.0
        else:
            theta_deg = math.degrees(math.atan2(dy, dx))

        # 中心(x,y)に置くため、左下基準の矩形を一旦配置してから回転
        rect = patches.Rectangle(
            (x - train_len/2, y - train_wid/2),
            train_len, train_wid,
            linewidth=0, facecolor="black", zorder=4
        )
        trans = transforms.Affine2D().rotate_deg_around(x, y, theta_deg) + ax.transData
        rect.set_transform(trans)
        ax.add_patch(rect)

    # 乗客：駅か電車のそばに描画
    # current_location が station_* か train_* かで分ける
    pax_by_station = {}
    pax_by_train = {}
    for pid, p in passengers.items():
        loc = p.get("current_location")
        if loc in stations:
            pax_by_station.setdefault(loc, []).append(p)
        elif loc in trains:
            pax_by_train.setdefault(loc, []).append(p)
        # else:
        #     raise RuntimeError

    # 駅にいる乗客：駅の周囲にリング状に配置（重なり回避）
    ring_r = 0.02  # 駅から少し離した半径
    for sid, plist in pax_by_station.items():
        st = stations.get(sid)
        if st is None:
            continue
        sx, sy = st["x"], st["y"]
        n = len(plist)
        for k, p in enumerate(plist):
            ang = 2 * math.pi * (k / max(n, 1))
            px = sx + ring_r * math.cos(ang)
            py = sy + ring_r * math.sin(ang)
            marker = SHAPE_TO_MARKER.get(p.get("shape_type"), "o")
            # 駅まわりの乗客は青い縁取り・中抜きで
            ax.scatter([px], [py], marker=marker, s=40,
                       facecolors="none", edgecolors="tab:blue",
                       linewidths=1.5, zorder=6)

    # 列車に乗っている乗客：車体中心の左右（進行方向に直交）へ配置
    side_offset = 0.015  # 1段あたりのオフセット
    for tid, plist in pax_by_train.items():
        t = trains.get(tid)
        if t is None:
            continue
        tx, ty = t.get("x"), t.get("y")
        dx, dy = t.get("dist_vector_x", 0.0), t.get("dist_vector_y", 0.0)

        # 進行方向に直交する単位ベクトル（dx,dy が0の場合は上方向を仮定）
        if dx == 0 and dy == 0:
            ux, uy = 0.0, 1.0
        else:
            L = math.hypot(dx, dy)
            ux, uy = -dy / L, dx / L  # 直交方向

        for k, p in enumerate(plist):
            # 左右に交互配置、段ごとに少しずつ離す
            side = -1 if (k % 2) == 0 else 1
            layer = (k // 2) + 1
            off = side * layer * side_offset
            px = tx + off * ux
            py = ty + off * uy
            marker = SHAPE_TO_MARKER.get(p.get("shape_type"), "o")
            # 列車内の乗客は白塗り＋緑縁で区別
            ax.scatter([px], [py], marker=marker, s=30,
                       facecolors="white", edgecolors="tab:green",
                       linewidths=1.5, zorder=7)


def main(args):
    records = load_records(f'{args.path}/log.json')
    print(f"Loaded: {args.path}/log.json")
    if not records:
        raise SystemExit("no records")

    fig, ax = plt.subplots(figsize=(6, 6))

    def update(i):
        draw_frame(ax, records[i])
        if i % 100 == 0:
            print(f'Draw: {i}-th Frame')
        return []

    anim = FuncAnimation(fig, update, frames=len(records), interval=1000/args.fps, blit=False)

    out_path = Path(f'{args.path}/animation.gif')
    if out_path.suffix.lower() == ".mp4":
        writer = FFMpegWriter(fps=args.fps)
    elif out_path.suffix.lower() == ".gif":
        writer = PillowWriter(fps=args.fps)
    else:
        raise SystemExit("出力拡張子は .mp4 か .gif を指定してください")
    anim.save(str(out_path), writer=writer)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    args = parse_args()
    main(args)
