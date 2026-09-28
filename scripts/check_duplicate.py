"""
Check a list of IFC GlobalIds for:
  1. Real geometry (has a Representation that actually produces a
     mesh, not an empty/degenerate shape)
  2. Overlapping position -- elements whose geometric centers land
     within a tolerance of each other (e.g. duplicates stacked on
     top of one another)

If duplicates are found, they are also printed as comma-separated
SETS: Set 1 = first element of every group, Set 2 = second element
of every group, Set 3 = third (only if some group has 3+), etc.
Keep Set 1, search/select Set 2+ (paste into Bonsai search) and delete.

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
21_FAYvFn2QuKOx4DDUf14,09yAaysE9C6xFoLihGC_Lz,1Be7idW3DABgHhmMYnb9O0,1ymLnESJjCsxv3KKBMJ3ws,3A9aD_O5f6dfVNNP1tID46,1Wy0bQM49Fw8G_YkyDFELP,3QR8$yxojExwa8n6djK9AB,2EXcxQf11EZBeKX9ehYbBv,2i4J_L$ZDBNu1umtLweo2p,1dttmt$9n1mvnVlE_txV53,3U$LRKxMj638rGqSfGuUEU,1YxII43b1A9OWf7_2uK0iw,21biRJfN9AX9hyPHaGi$HS,2B3GxNyzT6wACAu_CPhawi,2w_ar_H9jFV9mxJu9U5vmA,2NUSmSEYv60hlLM05J7NqX,3v6HnNffDARBR_sYZcofaf,2izN1SjAz9xBhJcgcNr1yb,2khXPqZ7zDOese_G_LW_kA,3MS8erpO57iBFi_1gF4Iyi,19NIVNPKbFbBO7hvKiEnx7,0_H6H2Xor3Sh5qXXGvgb6q,3ZwouuEsLAk8yO4x2IZIDX,1KCQ2nS6P77vitdAxsghW7,2Tz5_RK1v6V8m4bOQNHTSY,3z$$5J_bvFEwi$r5QCfGRD,3mVODSgsr9VemIjhxiu5KN,2j0f0x3xPEEukhkSys5_9D,09AJdfErL9DBvywIgVFG8f,0bo3mAE0vEQhyjpstQ4oA_,2ko5m26pL2pRGm$ZrCd$mW,0PJaY_S3X7buPWqthRGYUJ,0BbN2HobL4$wTygu2gJB8i,0HwPmIIXvDAfpe2_8eUHqj,13sSC40BD4VgCh3AGDsXfw,3VU$Cbio560h44XEHdUyWe,3_RAL6qGXA6whuCOkq3Kl0,0gokfD7unEzP1EBdvkLQ6d,36YPWYkUvBx8fZrGKndkwg,2NhLdKK2j5JRjpzUK9RVC2,1ExkOAiXT0LwdQvYQ8CX9E,1n9FcksfjE1A7jn0VYEIeg,1VbH1N3iX83h5IEk6gQKhC,1usdRDcuvFngB3PPGs8imB,1Bu_TqoKb1fxyTN52My23_,0SkYwQJpn2Dhp2IgABbwOt,2rSOLRlaH4nuxlWEMvN$cV,28ryNvR3H1kwji4YJmXn_g,2xbrB7TiP2x9E_2yfiWTSM,3bSK4hGDjEUuxsN0OqMTwY,01APXtiyfCFRKvjdBDy7lq,18rxADAfb4px$WtLHdoKlW,18yBDHGYv2Nxq2bxHzCizB,2IvrN3M3v5uOHUC3TQlYZh,2kZ6Pog4r91QcC3oR$TOmi,22qfNW6qD1Iwdy_ve74Z9v,0IkDNPYdr3ZQZXZoCvdRdY,1gFCS$MMn8fxFzvcG5EZ79,2CHghC$If8oPnLFJ59pElz,0MwzwkBPTBr9fA7FWG$XcQ,0KL_bjiYrDRfLeb$No44rf,0Iy3lnEFX1mBmn0$opb546,0OnSfqN8bEbhPPjyH$ShHc,2Gs4_eEX54Aff8lgTGUy1b,2PZQMEUITB0ufd5taMWKEg,2Aa7xTpHTCoxkUxRoRdQm7,1FfW_bR3T56R9NyB5gukP2,1$PMItK$nC3hskWCJugbrg,0fjG3kXj9AcRrwM3kVVqq0,1zJmrjMnH4dhynFpaGceP0,1OPtJDNk10TgyScs8wOP$f,1ATG5ci759hQcZZNXBoNaF,0O9ceujyj5jxd_4YNV$ZVA,3eq0$8dILDWRu3YylNoBlt,20kHt5yEzCQeEhS5NMJjhy,14nRP3h75CSRCDjUshOno$,1vR3CvfPzFl8RXAzhdCoPV,3O2yqCm5P06wG75GbBe3KR,19z3iwGlr0iPqK7JOWJbtm,1Lydic6zT6HOlDixNG0$8X,128oujVLX4F8CgmOvnqpmc,3lgchz6c564RBt8RnuuIku,1WPdcsBoDF3fF6r8uam7Qa,3xZKVs3HbCxeb2OX6E1I4E,3BSl5WDh19X9H66awf9v8K,3PBi_0jJ9AEfdPnMB67Ky8,1vgHDf81P9FfgcwqUDnLfU,3kr$wVi0D3z83I7fHPUb5P,2rde46g_TEoQ7kIVfO36A8,0tblaJBe15Tep3EnXXsiqn,19WWyfqAb5dhvEuHX5fgGn,2oXnIH59z4tx1hutMfs6dk,2nCtH7cQH5memELJL2_wVB,1wCHTM7CTF68_pvstRMXBs,09p_02D8H0le$$AbIGsxTp,3cULKomMjASRez$NvmgCeb,0ebIe$MiHCrvhukJIlU26o,2ai9c_Lln3X9Pj$vkheP17,1TMgziKrX1sBnGJiXhei55,1i8gvdh5j3nuSFrm1dHPMY,0DA5xhiVr9CgaPEud8tnFi,1gTgFqPZbBMuJnDjhY4JuR,0XxhQpxHf8VB6kq6Q8d5I6,3Y1xB96NrFF8lRDQ7NWsXv,3OPRC1D6T4uuyYSBTeRPHZ,3GIcW1jL99jPj7Kqg$nMNA,2u2Bm7GZjBKwHL279UzZx2,0NcsfJeAv0Rue2rpYZfle2,2CPCD3H7rF5w7Mx$kpo5Pc,2tnSvZm9fCvRYXMDAPY4f1,0kvp3TwCz5nfuAsGvAzneK,0ASMUVHOb3EByRNDylL69W,2j1ZYqTvTDd8KhtsxM3UbG,2Y292tnfnEWO97xFYuvUCe,07ak4$f4bEKR25b2s0qMZg,1vYxbiJCv6aOyiVGzm0aoG,1iRAELgpD27hATQ3LgR4oq,2YfPIzdwXAD9GbGABIYSZU,13t467EwfFIfXgdBVMbQoJ,1YGEf0myDFDv$2sCNSwWBI,2kiIocktDDUee6qQhUzSBU,2xNCLUcb1EGe_L2YAEfi1M,0fNRAT8T59rQoShUnIXn8C,1UJ6RZHkD2GPqxmBDIj3zC,0rzmLRET9BwAU4WWt_040J,2aE0mxziv14RiNQXw8b3kA,0naDoJjSb6Awa_HQ$6fxWh,111fTngJ17ugeAhdztWKS6,0JJhV7eIv0c8ywA1hamS2C,2qdytyaknCz9GGQi7piZCV,3NbUBiUur6nv4QZJ1kHgds,3QzBqPNYH9nxcbKnfNwov4,1Q7zcAz8L3LR$v_xJdF9bX,3kPvCP_Gv2dfb1jru2NF_u,32CjWEfXn2nRV2IvcfZ857,0jsS30bCLDz85i$ZJ0pdbr,1Z9DF24VD7hOGuFgpzFTaL,0gEanLE7LEUQ4WhHtnjqAp,3c0_CDVYv1Qef4PSnp2uJk,2OEDtBwIr55gNJRWU3ivl_
"""

# Option B: read GlobalIds from a CSV file instead. Leave CSV_PATH empty
# to use GLOBAL_IDS_RAW above.
CSV_PATH = r""
CSV_COLUMN = "GlobalId"   # column header name, or an integer index like 0

POSITION_TOLERANCE = 0.0001   # meters -- centers within this distance are "same position"


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
    least one other member (simple union-find style clustering).
    Member order inside a cluster follows the input order."""
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


def build_duplicate_sets(clusters):
    """Set k = k-th member of every cluster that has at least k members.
    Set 1 = the ones to keep, Set 2+ = the ones to delete."""
    if not clusters:
        return []
    max_n = max(len(c) for c in clusters)
    sets = []
    for k in range(max_n):
        sets.append([c[k] for c in clusters if len(c) > k])
    return sets


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

    # ---- Comma-separated duplicate sets (copy -> search -> delete) ----
    if clusters:
        dup_sets = build_duplicate_sets(clusters)
        log.append("== Duplicate sets (comma-separated, copy & search) ==")
        log.append("Set 1 = keep.  Set 2+ = delete (one of each duplicate group).")
        log.append("")
        for k, s in enumerate(dup_sets, start=1):
            role = "KEEP" if k == 1 else "DELETE"
            log.append(f"Set {k} [{role}] ({len(s)} ids):")
            log.append(",".join(s))
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