"""
Drawing module for JSONL visualization.

Converts partial unfolding records (raw/noniso/exact) to SVG files for visual inspection.
部分展開図レコード（raw/noniso/exact）を視覚検査用の SVG ファイルに変換します。

Based on scripts/draw_partial_unfolding.py (legacy implementation).
"""

import json
import math
from pathlib import Path


def compute_vertices(face):
    """
    Computes polygon vertices from a face record.
    
    face レコードから多角形の頂点を計算します。
    
    Args:
        face (dict): Face record with gon, x, y, angle_deg
    
    Returns:
        list: List of (x, y) tuples representing vertices
    """
    gon = face["gon"]
    x_center = face["x"]
    y_center = face["y"]
    angle_deg = face["angle_deg"]
    
    # Step angle between vertices
    # 頂点間の角度ステップ
    rot = 360.0 / float(gon)
    
    # angle_deg is the direction of the edge normal;
    # shift by half step to point to the vertex
    # angle_deg は辺法線の向き。頂点を向くように半角ずらす
    d = angle_deg - rot / 2.0
    
    # Circumradius of the n-gon
    # n 角形の外接円の半径
    radius = 1.0 / (2.0 * math.sin(math.pi / float(gon)))
    
    vertices = []
    for _ in range(gon):
        vx = x_center + radius * math.cos(math.pi * d / 180.0)
        vy = y_center + radius * math.sin(math.pi * d / 180.0)
        vertices.append((vx, vy))
        d -= rot
    
    return vertices


def compute_viewbox(all_vertices, margin_factor=0.05):
    """
    Computes the SVG viewBox from all vertices.
    
    すべての頂点から SVG viewBox を計算します。
    
    Args:
        all_vertices (list): List of vertex lists
        margin_factor (float): Margin factor (default: 0.05 = 5%)
    
    Returns:
        tuple: (x_min, y_min, width, height)
    """
    x_coords = [vx for face_verts in all_vertices for (vx, vy) in face_verts]
    y_coords = [vy for face_verts in all_vertices for (vx, vy) in face_verts]
    
    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    # Add margin
    # マージンを追加
    x_margin = (x_max - x_min) * margin_factor
    y_margin = (y_max - y_min) * margin_factor
    
    x_min -= x_margin
    x_max += x_margin
    y_min -= y_margin
    y_max += y_margin
    
    width = x_max - x_min
    height = y_max - y_min
    
    return x_min, y_min, width, height


def write_svg(output_path, record, show_labels=True):
    """
    Writes a single partial unfolding record as an SVG file.
    
    1つの部分展開図レコードを SVG ファイルとして書き出します。
    
    Args:
        output_path (Path): Output SVG file path
        record (dict): Partial unfolding record from raw.jsonl
        show_labels (bool): If True, draw face_id and edge_id labels.
                            If False, draw polygons only (no text).
                            Default: True.
    
    SVG specification (fixed for consistency):
    - Coordinate system: raw.jsonl x, y coordinates as-is
    - Angle interpretation: angle_deg as edge normal direction
    - Scale: Regular polygon edge length = 1, circumradius-based
    - Visual elements:
      - Faces: Black stroke, no fill
      - Face IDs: Black text at face center (when show_labels=True)
      - Edge IDs: Red text on shared edge (when show_labels=True)
    
    SVG 仕様（一貫性のため固定）:
    - 座標系: raw.jsonl の x, y 座標をそのまま使用
    - 角度解釈: angle_deg を辺法線の向きとして使用
    - スケール: 正多角形の辺長=1、circumradius ベース
    - 視覚要素:
      - 面: 黒枠、塗りなし
      - 面番号: 中心に黒字（show_labels=True の場合）
      - 辺番号: 共有辺上に赤字（show_labels=True の場合）
    """
    faces = record["faces"]
    
    # Compute vertices for all faces
    # すべての面の頂点を計算
    all_vertices = [compute_vertices(face) for face in faces]
    
    # Compute viewBox
    vb_x, vb_y, vb_w, vb_h = compute_viewbox(all_vertices)
    
    # Compute font size relative to viewBox (0.2% of smallest dimension)
    # フォントサイズを viewBox に対して相対的に計算（最小次元の 0.2%）
    ref_size = max(1e-6, min(vb_w, vb_h))
    font_scale = 0.002 * ref_size
    edge_bg_pad = 0.02 * ref_size
    
    # Write SVG
    with open(output_path, "w", encoding="utf-8") as out:
        # Header
        out.write('<?xml version="1.0" encoding="utf-8"?>\n')
        out.write(
            f'<svg version="1.1" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{vb_x} {vb_y} {vb_w} {vb_h}" '
            f'style="enable-background:new {vb_x} {vb_y} {vb_w} {vb_h};">\n'
        )
        out.write('<style type="text/css">\n')
        out.write('  .face_stroke {fill:none; stroke:#000000; stroke-width:0.02; stroke-miterlimit:10;}\n')
        out.write('  .face_text {fill:#000000; font-family:monospace;}\n')
        out.write('  .edge_text {fill:#ff0000; font-family:monospace;}\n')
        out.write('  .edge_bg {fill:#f3f3f3; stroke:#606060; stroke-width:0.01;}\n')
        out.write('</style>\n')
        
        # Draw polygons
        # 多角形を描画
        for verts in all_vertices:
            pts = " ".join(f"{vx},{vy}" for (vx, vy) in verts)
            out.write(f'<polygon class="face_stroke" points="{pts}"/>\n')
        
        # Draw face IDs and edge IDs (skipped when show_labels=False)
        # 面番号と辺番号を描画（show_labels=False の場合はスキップ）
        if show_labels:
            # Draw face IDs at face centers
            # 面番号を中心に描画
            for face in faces:
                x_center = face["x"]
                y_center = face["y"]
                face_id = face["face_id"]
                out.write(
                    f'<text class="face_text" text-anchor="middle" dominant-baseline="middle" '
                    f'transform="matrix({font_scale} 0 0 {font_scale} {x_center} {y_center})">'
                    f'{face_id}</text>\n'
                )
            
            # Draw edge IDs on shared edges (skip first face, which has no shared edge)
            # 共有辺上に辺番号を描画（最初の面はスキップ、共有辺なし）
            for i in range(1, len(faces)):
                face = faces[i]
                gon = face["gon"]
                x_center = face["x"]
                y_center = face["y"]
                angle_deg = face["angle_deg"]
                edge_id = face["edge_id"]
                
                # Place label along the edge-normal direction at inradius distance
                # 辺法線方向に内接円半径だけオフセットした位置に描画
                inradius = 1.0 / (2.0 * math.tan(math.pi / float(gon)))
                theta_rad = math.pi * angle_deg / 180.0
                ex = x_center + inradius * math.cos(theta_rad)
                ey = y_center + inradius * math.sin(theta_rad)
                
                # Draw background rectangle for edge ID
                # 辺番号の背景矩形を描画
                out.write(
                    f'<rect class="edge_bg" '
                    f'x="{ex - edge_bg_pad}" y="{ey - edge_bg_pad}" '
                    f'width="{2 * edge_bg_pad}" height="{2 * edge_bg_pad}"/>\n'
                )
                out.write(
                    f'<text class="edge_text" text-anchor="middle" dominant-baseline="middle" '
                    f'transform="matrix({font_scale} 0 0 {font_scale} {ex} {ey})">'
                    f'{edge_id}</text>\n'
                )
        
        # Footer
        out.write('</svg>\n')


def draw_raw_jsonl(raw_jsonl_path, output_dir, show_labels=True):
    """
    Draws all records in a raw.jsonl file as individual SVG files.
    
    raw.jsonl ファイルのすべてのレコードを個別の SVG ファイルとして描画します。
    
    Args:
        raw_jsonl_path (Path): Path to raw.jsonl
        output_dir (Path): Output directory for SVG files
        show_labels (bool): If True, draw face_id and edge_id labels.
                            If False, draw polygons only. Default: True.
    
    Returns:
        int: Number of SVG files generated
    
    Output structure:
        output_dir/000000.svg (6-digit zero-padded, 0-based index)
        output_dir/000001.svg
        ...
    
    出力構造:
        output_dir/000000.svg（6桁ゼロ埋め、0-based インデックス）
        output_dir/000001.svg
        ...
    """
    # Read all records from raw.jsonl
    # raw.jsonl からすべてのレコードを読み込む
    records = []
    with open(raw_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    
    if not records:
        print(f"Warning: No records found in {raw_jsonl_path}")
        return 0
    
    # Create output directory
    # 出力ディレクトリを作成
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Compute zero-padding width based on total record count (0-based indexing)
    # 総レコード数に基づいて0埋め桁数を計算（0-based インデックス）
    width = len(str(len(records) - 1))
    
    # Draw each record
    # 各レコードを描画
    for idx, record in enumerate(records):
        svg_filename = f"{str(idx).zfill(width)}.svg"
        svg_path = output_dir / svg_filename
        write_svg(svg_path, record, show_labels=show_labels)
    
    return len(records)
