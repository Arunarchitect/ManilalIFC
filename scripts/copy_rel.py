# Your script is working like this:
# File A	Current IFC opened in Bonsai/Blender
# File B	External IFC (Sreekesh_new.ifc)
# Goal	Copy TEXT_LEADER → Product relations from B into A

# This line in your output means you found a GUID with no target relationship in File B:
# WARNING: No target product relation found in File B for: GUID



import bonsai.tool as tool
import ifcopenshell
import ifcopenshell.guid
import bpy
import os

# ---------------- SETTINGS ----------------
DRY_RUN = True  # First run True. After checking log, change to False.
FILE_B_NAME = "Manilal_draft.ifc"
OUTPUT_SUFFIX = "New"

GUID_STRING = """
3Puo5lMKT7xPN363Zg6Tty,1Tfg2mUKf5ee7QVegqSvWD,387e3FGQz01QASXj82f2zW,2hCNyCwlzFeAPMMiK2Sy0q,10sQijXNv00AhiUVk49R8i,2N9NtF0IP1uQiyPVJ1aY25,2uEVYeriP8PO$o7oIZPWV3,16jMV9ig180vApQ0SPOzXH,33iT9_YYn4_BzAXh$46K4V,2FQy4W5n14ZQWoz3tMmNBB,0Qsx3d13LFAQCjDqO5uzOT,3KR3Df1Dj1WxJ5Ofhj6Go_,3eFqyK0Bf8cg7v$k7TXE9d,2Ouls1DHrEMhPOcSaXhcKm,3bEdat_$1Ee9Gq06gs6Tmb,1Vc1_rNd9ElPXjdsXUGqT4,3FVBee9Uj6gxMHbsgK8RDB,3fcAl9KVH4zRRx0OqMs2GM,1wNQyNq8z8WR7D1ge2y6Fk,0ybcBBoNDDEwaPvIj694I2,0i3yW3LxP3HA0PqBNv5Fni,0riKADHS5AhPlRVOu5RHjV,2lJKXYut18j8MU47AHYvBu,2eVj3TSV13WuzvsChcWY_X,2SHiVikR99txBUhvkBa$Tx,2gfOpCAZbEGfq2vNCBi51E,0IbR5UZrH2vBW2JqWWB_7Q,1YgNyNo8X7KeF8ih4OaroL,1X1FDKc_124h$qdtNd4Dga,1Us0TtN1bAReHMwHZKj_rL,0hGmq4$WL0zeQDY0qfmjOh,0JRYqUZ4bE_goO83hUIuHy,0p1uWqdajDhuZrMYlpKy2F,2nwcMMnxP6dfYCBLBQyJ_Q,0lpRFU65597f2hMJnfRuvQ,0EI7UO2Xz6p9JDihsOIv75,12wo1jz4HB3uFyOeX27iG8,0nMzteZYvBFPR$omT$WM6N,3ogMQwn$b2awfpqQeuzZ_I,2CIV47fhj9Ue4haGnJ3$86,37TqbIqRDC1gEshkiUEWIG,29XFlV$or0OA1LYdtJvteL,3MeRWmEDv6xBvB_wOgLGbZ,3SwIQmMZj94fplJHElKB5M,2i$whtDhb5QhpNyg2Z2SAc,1C3mJVAhL0ggoK6rbHR4$E,1kcYPp5tP0MeIxe9LhbrjD,0yac9W_lP50uMX73H8T6xt,2JJIMxWff0bvoMP4ZicHoC,1YAEBYSWj6MOVntnOktxuo,0SIoL$_1TFO8m7EYODYJix,3QeLDbnVP53wUC6LG0Uucr,1OJ2cd2oT1Kw3fwM2J5W2I,32lPuJw0zCoAHrNw74LX8y,1chNbUWDjDSx1qmYv57myW,3OmQKUE1nFQ8MFLfc2dc$X,10zLDG_dzE4AuTgBkVtu_o,0ngDctf_X0Hwq3w506iL1B,2ZcW3bimb5BOBH76OCieFO,1yL6DA2Sv0YvKiuWTqbh1e,1Hg5IclpvEXxdRltXqjmdC,2bkRFTvt10wOMT7KVwanM6,1ScqMcbjv7NflqyCWrrQB_,36A5KD0KfBTfC7NK0ScPfy,2lbLKxR_PCcwcY3BTUY3lj,0hDMVePc14rwkjYd87Xaw2,2i9Mg$e$TCiAi1us1T1uQO,02Y1EO3rT4OgApmznfIXvD,2vbNkzr_XC58XUn8xCqE1v,2iux7Q$GHC5QhQF$eTh8hE,35tT0G3LLA39vf8YdJEpkh,3Y0BC$mefDGvu0x3DL6om4,2e4Jycx4X2EQ7k0JUMYTVM,1r5SwhbOX9KQlsSbSHFalv,20fLi1Ptn1y8T94HM3ufbt,2XdGYfGyfCJRF$j8ECR9FJ,3LF$tzefb6_9hwBkHHf6dh,2V5PnAuIv5reoSfe2$8n3K,3JtbhGioz7twmNObAGXkCe,2IvOR6pZD7Xelgse7uL9kB,1i6HM_o_X7peOE6JLeXDFT
"""


TARGET_ANNOTATION_GUIDS = [
    x.strip() for x in GUID_STRING.split(",") if x.strip()
]

TARGET_CLASSES = [
    "IfcSwitchingDevice",
    "IfcOutlet",
    "IfcLightFixture",
    "IfcElectricAppliance"
]

SOURCE_MODE = "LAST_ONLY"
# "LAST_ONLY" = copy only last product relation from File B
# "ALL"       = copy all target product relations from File B
# ------------------------------------------

model_a = tool.Ifc.get()

file_a_path = tool.Ifc.get_path()
folder = os.path.dirname(file_a_path)

file_b_path = os.path.normpath(os.path.join(folder, FILE_B_NAME))
model_b = ifcopenshell.open(file_b_path)

name, ext = os.path.splitext(os.path.basename(file_a_path))
output_path = os.path.normpath(os.path.join(folder, name + OUTPUT_SUFFIX + ext))

log = bpy.data.texts.get("IFC Output") or bpy.data.texts.new("IFC Output")
log.clear()

def write(msg=""):
    log.write(str(msg) + "\n")

def is_target_product(product):
    return product and any(product.is_a(cls) for cls in TARGET_CLASSES)

def get_target_relations(model, annotation):
    rels = []
    for inv in model.get_inverse(annotation):
        if inv.is_a("IfcRelAssignsToProduct"):
            product = inv.RelatingProduct
            if is_target_product(product):
                rels.append(inv)
    return rels

def remove_annotation_from_old_relations(model, annotation):
    for rel in list(get_target_relations(model, annotation)):
        old_related = list(rel.RelatedObjects)
        new_related = [x for x in old_related if x != annotation]

        write("Removing old A relation: #" + str(rel.id()))
        write("Old product: " + str(rel.RelatingProduct))
        write("RelatedObjects before: " + str([x.id() for x in old_related]))
        write("RelatedObjects after : " + str([x.id() for x in new_related]))

        if not DRY_RUN:
            if len(new_related) == 0:
                model.remove(rel)
                write("Action: deleted empty relation")
            else:
                rel.RelatedObjects = tuple(new_related)
                write("Action: removed annotation from relation")
        else:
            write("Action: DRY RUN only. No change made.")

        write("-" * 60)

def assign_annotation_to_product(model, annotation, product):
    existing_rel = None

    for inv in model.get_inverse(product):
        if inv.is_a("IfcRelAssignsToProduct") and inv.RelatingProduct == product:
            existing_rel = inv
            break

    if existing_rel:
        related = list(existing_rel.RelatedObjects)

        if annotation not in related:
            related.append(annotation)

            if not DRY_RUN:
                existing_rel.RelatedObjects = tuple(related)

            write("Added annotation to existing relation #" + str(existing_rel.id()))
        else:
            write("Annotation already exists in relation #" + str(existing_rel.id()))

    else:
        owner_history_list = model.by_type("IfcOwnerHistory")
        owner_history = owner_history_list[0] if owner_history_list else None

        if not DRY_RUN:
            new_rel = model.create_entity(
                "IfcRelAssignsToProduct",
                ifcopenshell.guid.new(),
                owner_history,
                None,
                None,
                (annotation,),
                None,
                product
            )
            write("Created new relation #" + str(new_rel.id()))
        else:
            write("Would create new IfcRelAssignsToProduct relation")

write("COPY TEXT_LEADER PRODUCT RELATIONS FROM FILE B TO FILE A")
write("=" * 100)
write("Mode: " + ("DRY RUN - no changes saved" if DRY_RUN else "LIVE - File A will be modified and saved"))
write("File A/current: " + file_a_path)
write("File B/source : " + file_b_path)
write("Output file   : " + output_path)
write("Source mode   : " + SOURCE_MODE)
write("Target classes: " + ", ".join(TARGET_CLASSES))
write("Target GUIDs  : " + ", ".join(TARGET_ANNOTATION_GUIDS))
write("=" * 100)

processed = 0
matched = 0
skipped_not_in_guid_list = 0
skipped_no_a_annotation = 0
skipped_no_b_annotation = 0
skipped_no_b_relation = 0
skipped_missing_product_in_a = 0

# Process only GUIDs given in GUID_STRING
for gid in TARGET_ANNOTATION_GUIDS:

    annotation_a = model_a.by_guid(gid)

    if not annotation_a:
        skipped_no_a_annotation += 1
        write("")
        write("WARNING: Annotation GUID not found in File A: " + gid)
        continue

    if not annotation_a.is_a("IfcAnnotation") or annotation_a.Name != "TEXT_LEADER":
        skipped_not_in_guid_list += 1
        write("")
        write("WARNING: GUID exists in File A, but is not TEXT_LEADER annotation: " + gid)
        write(str(annotation_a))
        continue

    processed += 1

    annotation_b = model_b.by_guid(gid)

    if not annotation_b:
        skipped_no_b_annotation += 1
        write("")
        write("WARNING: Same annotation GUID not found in File B: " + gid)
        continue

    rels_b = get_target_relations(model_b, annotation_b)

    if not rels_b:
        skipped_no_b_relation += 1
        write("")
        write("WARNING: No target product relation found in File B for: " + gid)
        continue

    if SOURCE_MODE == "LAST_ONLY":
        rels_b = [rels_b[-1]]

    write("")
    write("=" * 100)
    write("MATCHED TEXT_LEADER")
    write("Annotation GUID: " + gid)
    write("File A annotation: " + str(annotation_a))
    write("File B annotation: " + str(annotation_b))
    write("Relations copied from B: " + str(len(rels_b)))

    target_products_a = []

    for rel_b in rels_b:
        product_b = rel_b.RelatingProduct
        product_gid = product_b.GlobalId
        product_a = model_a.by_guid(product_gid)

        write("")
        write("Source B relation: #" + str(rel_b.id()))
        write("Source B product : " + str(product_b))
        write("Product GUID     : " + product_gid)

        if not product_a:
            skipped_missing_product_in_a += 1
            write("WARNING: Matching product not found in File A. Skipped.")
            continue

        write("Target A product : " + str(product_a))

        blender_obj = tool.Ifc.get_object(product_a)
        write("A Blender object : " + (blender_obj.name if blender_obj else "None"))

        target_products_a.append(product_a)

    if not target_products_a:
        continue

    write("")
    write("Cleaning old File A product relations for this annotation...")
    remove_annotation_from_old_relations(model_a, annotation_a)

    write("")
    write("Creating/copying File B relations into File A...")
    for product_a in target_products_a:
        assign_annotation_to_product(model_a, annotation_a, product_a)

    matched += 1

write("")
write("=" * 100)
write("SUMMARY")
write("Target GUIDs given             : " + str(len(TARGET_ANNOTATION_GUIDS)))
write("TEXT_LEADER annotations checked: " + str(processed))
write("Annotations updated/matched    : " + str(matched))
write("GUID not found in File A       : " + str(skipped_no_a_annotation))
write("Not TEXT_LEADER in File A      : " + str(skipped_not_in_guid_list))
write("No same annotation in File B   : " + str(skipped_no_b_annotation))
write("No product relation in File B  : " + str(skipped_no_b_relation))
write("Missing product in File A      : " + str(skipped_missing_product_in_a))

if not DRY_RUN:
    model_a.write(output_path)
    write("Saved fixed File A to:")
    write(output_path)
else:
    write("DRY RUN complete. No file saved.")

write("=" * 100)