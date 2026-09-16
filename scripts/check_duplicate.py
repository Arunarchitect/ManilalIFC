"""
Check a list of IFC GlobalIds for:
  1. Real geometry (has a Representation that actually produces a
     mesh, not an empty/degenerate shape)
  2. Overlapping position -- elements whose geometric centers land
     within a tolerance of each other (e.g. duplicates stacked on
     top of one another)

USAGE
- If the file is currently open in Bonsai: just run this in Blender's
  Text Editor, it uses the live model.
- Otherwise set SOURCE_PATH below and run as a plain script.
- Paste GlobalIds into GLOBAL_IDS_RAW as plain comma-separated text
  (no quotes needed), OR set CSV_PATH to a .csv file with a column
  of GlobalIds (set CSV_COLUMN to the column name or index).
- Adjust POSITION_TOLERANCE (meters) to control how close two
  centers must be to count as "on top of each other".

Log prints to console; if run inside Blender it also opens in a new
Text Editor window.
"""

import collections
import csv

SOURCE_PATH = r""   # only used when not running inside Bonsai

# Option A: paste GlobalIds directly, comma/newline separated, no quotes.
GLOBAL_IDS_RAW = """
3vRSHD2T9AM8gZzgZsMvA2,0F8rjSor14AvP6b_oX77FF,2niFQd8cz689rC3yPADnD9,2_ogrHrQ16wQszzZQ4$1Js,1i8egTi9j6RwJAWc8wVS85,0OuT1jbUz46xk4hUQSKXnh,36qXah_Xj8r84Tdfd7AsFh,3aT02EmLf0hBae7r_s0agw,3lKDDAQDT6gerYdKa7axVW,0ddXiuRnLAJe_5wmjnMdM7,29PWW3qgDBDhQqLg2SzK40,2FQucbqhv8AhQbn$lqQ_T_
"""

# Option B: read GlobalIds from a CSV file instead. Leave CSV_PATH empty
# to use GLOBAL_IDS_RAW above.
CSV_PATH = r""
CSV_COLUMN = "GlobalId"   # column header name, or an integer index like 0

POSITION_TOLERANCE = 0.05   # meters -- centers within this distance are "same position"


def get_file():
    try:
        import bpy
        import bonsai.tool as tool
        f = tool.Ifc.get()
        if f is not None:
            return f, True
    except Exception:
        pass
    import ifcopenshell
    return ifcopenshell.open(SOURCE_PATH), False


def parse_global_ids_raw(raw):
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    seen = set()
    out = []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def parse_global_ids_csv(path, column):
    out = []
    seen = set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return out
    start = 0
    col_index = column
    if isinstance(column, str):
        header = rows[0]
        if column in header:
            col_index = header.index(column)
            start = 1
        else:
            # no matching header, assume column 0 and no header row
            col_index = 0
            start = 0
    for row in rows[start:]:
        if col_index < len(row):
            val = row[col_index].strip()
            if val and val not in seen:
                seen.add(val)
                out.append(val)
    return out


def get_shape_data(product):
    """Returns (has_geometry, center_xyz, vert_count, face_count) or
    (False, None, 0, 0) if no usable geometry."""
    import ifcopenshell.geom
    if not getattr(product, "Representation", None):
        return False, None, 0, 0
    try:
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)
        shape = ifcopenshell.geom.create_shape(settings, product)
    except Exception:
        return False, None, 0, 0
    verts = shape.geometry.verts
    faces = shape.geometry.faces
    if not verts:
        return False, None, 0, 0
    xs, ys, zs = verts[0::3], verts[1::3], verts[2::3]
    center = (
        (min(xs) + max(xs)) / 2,
        (min(ys) + max(ys)) / 2,
        (min(zs) + max(zs)) / 2,
    )
    return True, center, len(verts) // 3, len(faces) // 3


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def cluster_by_position(items, tolerance):
    """items: list of (guid, center). Returns list of clusters (each a
    list of guids) where every member is within `tolerance` of at
    least one other member (simple union-find style clustering)."""
    n = len(items)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if distance(items[i][1], items[j][1]) <= tolerance:
                union(i, j)

    groups = collections.defaultdict(list)
    for i in range(n):
        groups[find(i)].append(items[i][0])

    return [g for g in groups.values() if len(g) > 1]


def main():
    f, in_bonsai = get_file()

    if CSV_PATH:
        guids = parse_global_ids_csv(CSV_PATH, CSV_COLUMN)
        source_desc = f"CSV: {CSV_PATH}"
    else:
        guids = parse_global_ids_raw(GLOBAL_IDS_RAW)
        source_desc = "pasted list"

    log = []
    log.append("IFC geometry + overlap check")
    log.append(f"Source model: {'(live Bonsai file)' if in_bonsai else SOURCE_PATH}")
    log.append(f"GlobalId source: {source_desc}")
    log.append(f"GlobalIds provided: {len(guids)}")
    log.append(f"Position tolerance: {POSITION_TOLERANCE} m")
    log.append("=" * 70)
    log.append("")

    no_geom = []
    has_geom_items = []   # (guid, center)
    not_found = []

    log.append("== Per-element geometry check ==")
    for g in guids:
        try:
            el = f.by_guid(g)
        except RuntimeError:
            not_found.append(g)
            log.append(f"NOT FOUND  {g}")
            continue

        name = getattr(el, "Name", None) or "Unnamed"
        ok, center, vcount, fcount = get_shape_data(el)
        if not ok:
            no_geom.append(g)
            log.append(f"NO GEOM    {el.is_a():20s} {name:25s} {g}")
        else:
            has_geom_items.append((g, center))
            cx, cy, cz = center
            log.append(
                f"OK         {el.is_a():20s} {name:25s} {g}  "
                f"verts={vcount} faces={fcount}  center=({cx:.3f}, {cy:.3f}, {cz:.3f})"
            )

    log.append("")
    log.append(f"Elements with real geometry: {len(has_geom_items)}")
    log.append(f"Elements with no/empty geometry: {len(no_geom)}")
    log.append(f"GlobalIds not found in model: {len(not_found)}")
    log.append("")

    log.append("== Overlapping position groups (possible duplicates on top of each other) ==")
    clusters = cluster_by_position(has_geom_items, POSITION_TOLERANCE)
    if not clusters:
        log.append("None found -- all elements with geometry occupy distinct positions.")
    else:
        for idx, cluster in enumerate(clusters, start=1):
            log.append(f"Group {idx}: {len(cluster)} elements at roughly the same position:")
            for g in cluster:
                el = f.by_guid(g)
                name = getattr(el, "Name", None) or "Unnamed"
                log.append(f"    {el.is_a():20s} {name:25s} {g}")
    log.append("")

    text = "\n".join(log)
    print(text)

    try:
        import bpy
        text_name = "geom_overlap_check_log.txt"
        if text_name in bpy.data.texts:
            bpy.data.texts.remove(bpy.data.texts[text_name])
        tb = bpy.data.texts.new(text_name)
        tb.write(text)
        bpy.ops.wm.window_new()
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = 'TEXT_EDITOR'
        area.spaces[0].text = tb
    except Exception:
        pass


main()