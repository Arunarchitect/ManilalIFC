"""
Append IFC elements from a library file (A.ifc) into the IFC project
currently open in Bonsai (B.ifc), skipping any element that triggers
the known ifcopenshell SafeRemovalContext AssertionError instead of
crashing the whole batch.

USAGE
1. Paste this into Blender's Text Editor (Scripting workspace) while
   B.ifc is the active Bonsai project.
2. Set LIBRARY_PATH below to A.ifc.
3. Paste GlobalIds into GLOBAL_IDS_RAW as a plain comma-separated
   string -- no quotes needed, just paste them as-is.
   Leave GLOBAL_IDS_RAW empty and set ELEMENT_CLASSES instead to
   append by class, or leave both empty to attempt every IfcProduct.
4. Run (Alt+P). A log opens automatically in a NEW window as a
   Text Editor showing what was appended / skipped / failed.
"""

import bpy
import ifcopenshell
import ifcopenshell.api
import bonsai.tool as tool

# ---------------- CONFIG ----------------
LIBRARY_PATH = r"D:\BIM\IFCdraft\JailaniIFC\Jailani.ifc"   # file A (source)

# Paste GlobalIds here as plain comma-separated text -- no quotes needed.
GLOBAL_IDS_RAW = """
1KVgXehG12NuuPUw6p3DTo,0GLarNUov1VeVl3fZ9q7UC,0BTi8epxf9RO8JCT6ZCY8o,2cDnyHeJX7fA7Imk3Iyk8L,2o$g85k7P0xeZo_jus001h,2WrF2PKrzDJ8fhsIL077S_,1yKhzPTSf6zPGFGzpUR2TF,2Ovcx8IZ1EKehSgxTznwf3,1ix6nRgZ52ohZzSN3cS_pg,0bUrJ1nQ1DxvfaksnMBKAb,0nU2nC6NL9vwl8JxfDqm8z,3T6ceO021Eie9xeMkf$5m$,1oE9kj3GHDV9msKO54AIMy,2gGFa_YsDBzvWdus98DlVJ,1KlD1fzKH7N9EzTcy_mpLg,3apIKERcTDD8lqwdmy74XB,1WcbdTcOH2QBA2kykCd4ee,0PGtUg1Sj02uJYpcVJ9C$A,23jQO982DDIBCZbF13RLjW,00MvRCrSv63O0wx1Bmw6do,2rA76Y8arEZuqO4btIGNQG,0t4q49QfX5NPetOlLc4BRK,1O_4NFNw1C0ue$ia7M6F$X,1inxOPZ6jBpQKscaGLOnNw,39jBbOfU5FZub2nlHJY41J,0q6swJxZf849iYym2hmy77,1jmg2_y01BTBdp9MkgGy7c,0sCnFyGnvCk8iaIZYQkQFq,1OPK7H_Ij6nQHKh1GXPYLh,2nKCWWunjBOe3EpfeONnxU,0lT4F4vxT90RLOoAeYalj2,3lTV6iICT0qeANfWctUB9Q,242h7U6OfFrxFBTJmjH2k5,25jv2_$THBIgsHefdbYP8A,2ub9BlFSb4seEUaULfYquA,0nRuhD_m56exN$5XvDId$g,01HONCZuf88g8ryR2U00no,3asoLGcLfCCwXuXElLs7LD,1etd2cWEHDOfjFz3bFlwSz,2sjnULEabAjwhfcTvt2Hg3,2tgzu0qPn0bu6lo4TZxvzl,2aicgLxivBx8IBvwytWrsb,3snr29qDPBVwAd3qmOci7U
"""

ELEMENT_CLASSES = []   # e.g. ["IfcFurniture", "IfcDoorType"] - by class
# If GLOBAL_IDS_RAW and ELEMENT_CLASSES are both empty, every
# IfcProduct in the library is attempted.
# -----------------------------------------


def parse_global_ids(raw):
    # Splits on commas/whitespace/newlines, drops empties, dedupes while
    # preserving order.
    parts = [p.strip() for p in raw.replace("\n", ",").split(",")]
    seen = set()
    out = []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def get_target_elements(library_file):
    guids = parse_global_ids(GLOBAL_IDS_RAW)
    if guids:
        out = []
        for g in guids:
            try:
                out.append(library_file.by_guid(g))
            except RuntimeError:
                print(f"GlobalId not found in library: {g}")
        return out
    if ELEMENT_CLASSES:
        out = []
        for cls in ELEMENT_CLASSES:
            out.extend(library_file.by_type(cls))
        return out
    return library_file.by_type("IfcProduct")


def open_log_in_new_text_editor(text_block):
    bpy.ops.wm.window_new()
    new_window = bpy.context.window_manager.windows[-1]
    area = new_window.screen.areas[0]
    area.type = 'TEXT_EDITOR'
    area.spaces[0].text = text_block


def main():
    file_b = tool.Ifc.get()
    if file_b is None:
        raise Exception("No IFC project is currently loaded in Bonsai (file B).")

    library_file = ifcopenshell.open(LIBRARY_PATH)
    elements = get_target_elements(library_file)

    log = []
    log.append(f"Append run: {len(elements)} candidate elements from {LIBRARY_PATH}")
    log.append(f"Target project: {tool.Ifc.get_path() or '(unsaved)'}")
    log.append("-" * 70)

    appended, skipped = 0, 0

    for el in elements:
        name = getattr(el, "Name", None) or "Unnamed"
        guid = getattr(el, "GlobalId", "no-guid")
        label = f"{el.is_a():20s} {name:30s} {guid}"
        try:
            ifcopenshell.api.run(
                "project.append_asset",
                file_b,
                library=library_file,
                element=el,
                assume_asset_uniqueness_by_name=False,
            )
            appended += 1
            log.append(f"OK    {label}")
        except AssertionError:
            skipped += 1
            log.append(f"SKIP  {label}  -- SafeRemovalContext assertion failed")
        except Exception as e:
            skipped += 1
            log.append(f"FAIL  {label}  -- {type(e).__name__}: {e}")

    log.append("-" * 70)
    log.append(f"Appended: {appended}   Skipped/Failed: {skipped}")
    log.append("")
    log.append("NOTE: newly appended elements exist in the IFC model now.")
    log.append("If they don't show in the viewport, save the project and")
    log.append("reopen it in Bonsai (File > Open) to force a full resync,")
    log.append("or use Bonsai's own 'Reload' if your version has it.")

    text_name = "append_log.txt"
    if text_name in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts[text_name])
    text_block = bpy.data.texts.new(text_name)
    text_block.write("\n".join(log))

    open_log_in_new_text_editor(text_block)
    print("\n".join(log))


main()