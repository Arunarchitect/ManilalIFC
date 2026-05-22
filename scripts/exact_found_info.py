# if I am going to import some edited elements from an ifc file A to B, if B has the same elements it will create error, so just check these elements are present in full or any in the file B by using this code.

import bonsai.tool as tool
import bpy

model = tool.Ifc.get()

log = bpy.data.texts.get("IFC Output") or bpy.data.texts.new("IFC Output")
log.clear()

def write(msg=""):
    log.write(str(msg) + "\n")

GUID_STRING = "2BpyirL$f6vuCuR_mweUND,0fmV3XqO13wvlJE7sf_xmm,0IqzncWeTAFRrTluzv$Brx"

GUIDS = [x.strip() for x in GUID_STRING.split(",") if x.strip()]

write("CHECKING GUIDS IN CURRENT IFC FILE")
write("=" * 80)
write("Total GUIDs given: " + str(len(GUIDS)))
write("")

ifc_by_guid = {}

for element in model:
    guid = getattr(element, "GlobalId", None)
    if guid:
        ifc_by_guid[guid] = element

found = []
missing = []

for gid in GUIDS:
    if gid in ifc_by_guid:
        found.append((gid, ifc_by_guid[gid]))
    else:
        missing.append(gid)

write("FOUND ELEMENTS")
write("=" * 80)

if not found:
    write("No matching GUIDs found in the current IFC file.")
else:
    for gid, obj in found:
        blender_obj = tool.Ifc.get_object(obj)

        write("")
        write("-" * 80)
        write("GUID: " + str(getattr(obj, "GlobalId", None)))
        write("STEP ID: #" + str(obj.id()))
        write("IFC Class: " + obj.is_a())
        write("Name: " + str(getattr(obj, "Name", None)))
        write("Description: " + str(getattr(obj, "Description", None)))
        write("ObjectType: " + str(getattr(obj, "ObjectType", None)))
        write("PredefinedType: " + str(getattr(obj, "PredefinedType", None)))
        write("Tag: " + str(getattr(obj, "Tag", None)))
        write("Blender Object: " + (blender_obj.name if blender_obj else "None"))

        write("")
        write("GROUPS / DRAWING GROUPS")
        write("-" * 40)

        group_found = False

        for inv in model.get_inverse(obj):
            if inv.is_a("IfcRelAssignsToGroup"):
                group_found = True
                group = inv.RelatingGroup

                write("Relation STEP ID: #" + str(inv.id()))
                write("Relation: " + inv.is_a())
                write("Group STEP ID: #" + str(group.id()))
                write("Group IFC Class: " + group.is_a())
                write("Group Name: " + str(getattr(group, "Name", None)))
                write("Group Description: " + str(getattr(group, "Description", None)))
                write("Group ObjectType: " + str(getattr(group, "ObjectType", None)))
                write("")

        if not group_found:
            write("No IfcRelAssignsToGroup relation found for this object.")

write("")
write("MISSING GUIDS")
write("=" * 80)

for gid in missing:
    write("NOT FOUND: " + gid)

write("")
write("SUMMARY")
write("=" * 80)
write("Total Checked: " + str(len(GUIDS)))
write("Found: " + str(len(found)))
write("Missing: " + str(len(missing)))