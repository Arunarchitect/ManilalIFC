import bpy
import ifcopenshell

# ========== CONFIGURATION ==========
GLOBAL_IDS = """
32cZLEI$X6EPd2kfcqcZIs,2VK5OGJf58Zxz1lkZ836iV,27IdAHymH7pfdNnP37q8IU,2SBvWWuib1y9us92wpXxg6,2JZlOvyNTCTRvs_$d_eb_J,3kGTb$G6P6ZvOPWJhq5OiK,1HtZ9BNiX2nRuDNk8xxq9f,03PPf$qkT44QteCsd7bRRf,28uVh7XAj3khXTMKC_um5p,3alNGx3bf3NQ2FIOd6cb5v,1WUry1fgH9KPHBtVCMMFwr,2DJMjTYTP5NfVV9adh2rKf,0WgEfcj4LA8eDwBtdBqgds,3zFOV$SQv8awn0z99J3enp,20xVbn1ND4i8XMvUhxXznn,1TFAKfufj7_u3eMMbIjLwA,0V7YM0wrzCAwvQX_x60_r3,3u23$6r0r8shdcm7jX6qUD,0QkmgZR85CSA51tNtMWdq$,0z$ZKVnKXCohPZwZAa0dAL,0EqSEa5xr1uBMW2abWyNQA
"""

OUTPUT_TEXT_NAME = "IFC_Fix_Report"
# ====================================

def get_output_text_block():
    if OUTPUT_TEXT_NAME in bpy.data.texts:
        text_block = bpy.data.texts[OUTPUT_TEXT_NAME]
        text_block.clear()
    else:
        text_block = bpy.data.texts.new(OUTPUT_TEXT_NAME)
    for area in bpy.context.screen.areas:
        if area.type == 'TEXT_EDITOR':
            area.spaces.active.text = text_block
            break
    return text_block


def fix_rel(rel, fixes, indent):
    try:
        if isinstance(rel.RelatingPriorities, tuple) and len(rel.RelatingPriorities) == 0:
            rel.RelatingPriorities = (0,)
            fixes.append(f"{indent}✅ Fixed: IfcRelConnectsPathElements (ID: {rel.id()}) RelatingPriorities: () → (0,)")
    except Exception as e:
        fixes.append(f"{indent}⚠️ Could not fix RelatingPriorities on ID {rel.id()}: {e}")

    try:
        if isinstance(rel.RelatedPriorities, tuple) and len(rel.RelatedPriorities) == 0:
            rel.RelatedPriorities = (0,)
            fixes.append(f"{indent}✅ Fixed: IfcRelConnectsPathElements (ID: {rel.id()}) RelatedPriorities: () → (0,)")
    except Exception as e:
        fixes.append(f"{indent}⚠️ Could not fix RelatedPriorities on ID {rel.id()}: {e}")


def fix_element_issues(element, ifc_file, indent="  "):
    fixes = []

    for attr_name in ('ConnectedTo', 'ConnectedFrom'):
        if hasattr(element, attr_name):
            for rel in getattr(element, attr_name):
                if rel.is_a() == 'IfcRelConnectsPathElements':
                    fix_rel(rel, fixes, indent)

    if hasattr(element, 'IsDefinedBy'):
        for rel in element.IsDefinedBy:
            if rel.is_a() != 'IfcRelDefinesByProperties':
                continue
            pset = rel.RelatingPropertyDefinition
            if pset and pset.is_a() == 'IfcElementQuantity':
                try:
                    if isinstance(pset.Quantities, tuple) and len(pset.Quantities) == 0:
                        dummy = ifc_file.create_entity(
                            "IfcQuantityCount",
                            Name="Placeholder",
                            CountValue=0
                        )
                        pset.Quantities = (dummy,)
                        fixes.append(
                            f"{indent}✅ Fixed: IfcElementQuantity (ID: {pset.id()}) "
                            f"Quantities: () → (IfcQuantityCount placeholder, ID: {dummy.id()})"
                        )
                except Exception as e:
                    fixes.append(f"{indent}⚠️ Could not fix Quantities on ID {pset.id()}: {e}")

    return fixes


def main():
    from bonsai.bim.ifc import IfcStore
    ifc_file = IfcStore.get_file()
    if ifc_file is None:
        raise Exception("No IFC file is currently open — open the SOURCE file "
                         "(D:\\ARUN\\Blender\\IFC draft\\ManilalIFC\\Manilal.ifc)")

    global_ids = [gid.strip() for gid in GLOBAL_IDS.split(',') if gid.strip()]

    report_lines = []
    report_lines.append("IFC FIX REPORT - Fixing Mandatory Empty Lists (re-run after reset)")
    report_lines.append(f"Total elements to fix: {len(global_ids)}")
    report_lines.append(f"{'='*60}")

    total_fixes = 0
    elements_fixed = 0
    elements_errored = 0

    for idx, gid in enumerate(global_ids, 1):
        element = ifc_file.by_guid(gid)

        if element is None:
            report_lines.append(f"\n[{idx}/{len(global_ids)}] ❌ NOT FOUND: {gid}")
            continue

        report_lines.append(f"\n[{idx}/{len(global_ids)}] {element.is_a()} - {element.Name}")
        report_lines.append(f"GlobalId: {gid}")

        try:
            fixes = fix_element_issues(element, ifc_file)
        except Exception as e:
            elements_errored += 1
            report_lines.append(f"  ❌ ERROR while fixing this element: {e}")
            continue

        if fixes:
            elements_fixed += 1
            total_fixes += len(fixes)
            for fix in fixes:
                report_lines.append(fix)
        else:
            report_lines.append(f"  ℹ️ No fixes needed")

    report_lines.append(f"\n{'='*60}")
    report_lines.append(f"Elements fixed: {elements_fixed}")
    report_lines.append(f"Elements errored: {elements_errored}")
    report_lines.append(f"Total fixes applied: {total_fixes}")
    report_lines.append(f"\n💾 SAVE THIS FILE NOW, then try appending again.")

    text_block = get_output_text_block()
    text_block.write('\n'.join(report_lines))
    print(f"Total fixes applied: {total_fixes}, errored: {elements_errored}")


try:
    main()
except Exception as e:
    import traceback
    error_msg = f"ERROR: {str(e)}\n\n{traceback.format_exc()}"
    print(error_msg)
    try:
        text_block = get_output_text_block()
        text_block.write(error_msg)
    except:
        pass