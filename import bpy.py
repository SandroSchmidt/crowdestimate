import bpy
import math
from mathutils import Vector, Euler

# =========================
# USER PARAMS (Option B)
# =========================
EXPORT_PATH = r"/tmp/standing_woman_lowpoly.glb"

# Target style / budget:
# Increase/decrease these to tune triangle count.
SEG_BODY = 20       # torso/limbs radial segments (higher => more tris)
SEG_HEAD = 24       # head segments (higher => more tris)
SEG_HAND_FOOT = 16  # hands/feet segments

# Color variants (RGB)
SKIN_COLOR   = (0.86, 0.73, 0.64, 1.0)
HAIR_COLOR   = (0.12, 0.08, 0.05, 1.0)
TSHIRT_COLOR = (0.20, 0.35, 0.70, 1.0)
JEANS_COLOR  = (0.08, 0.14, 0.28, 1.0)
SHOE_COLOR   = (0.90, 0.90, 0.92, 1.0)

# Clothing variants (small tweaks)
TSHIRT_SLEEVE_LEN = 0.18   # 0.12 short / 0.22 longer
JEANS_CUFF_HEIGHT = 0.06   # 0.00 none / 0.06 small cuff

# Pose variants (subtle, non-sexy)
WEIGHT_SHIFT = 0.04        # hip shift (meters)
ARM_RELAX_ANGLE = math.radians(18)
KNEE_BEND = math.radians(5)

# Scale (meters): Three.js works well with real-world scale.
HEIGHT = 1.65

# =========================
# Helpers
# =========================
def wipe_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.armatures):
        for b in list(block):
            try:
                block.remove(b)
            except:
                pass

def mat_principled(name, base_color, rough=0.6, spec=0.25):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular"].default_value = spec
    return m

def add_cylinder(name, radius, depth, seg, loc=(0,0,0), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=seg, radius=radius, depth=depth,
        location=loc, rotation=rot
    )
    obj = bpy.context.object
    obj.name = name
    return obj

def add_uv_sphere(name, radius, seg_u, seg_v, loc=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg_u, ring_count=seg_v, radius=radius,
        location=loc
    )
    obj = bpy.context.object
    obj.name = name
    return obj

def add_cube(name, size, loc=(0,0,0), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    return obj

def shade_smooth_auto(obj, angle_deg=45):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth()
    if obj.data:
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = math.radians(angle_deg)
    obj.select_set(False)

def apply_all(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.select_set(False)

def join_objects(objs, name):
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = name
    for o in objs:
        o.select_set(False)
    return joined

# =========================
# Build model
# =========================
wipe_scene()

# Materials
mat_skin  = mat_principled("MAT_Skin",  SKIN_COLOR, rough=0.55, spec=0.35)
mat_hair  = mat_principled("MAT_Hair",  HAIR_COLOR, rough=0.65, spec=0.15)
mat_shirt = mat_principled("MAT_TShirt",TSHIRT_COLOR, rough=0.75, spec=0.10)
mat_jeans = mat_principled("MAT_Jeans", JEANS_COLOR, rough=0.80, spec=0.08)
mat_shoes = mat_principled("MAT_Shoes", SHOE_COLOR, rough=0.60, spec=0.20)

# Proportions (derived from HEIGHT)
h = HEIGHT
head_r   = 0.095 * (h/1.65)
neck_h   = 0.05  * (h/1.65)
torso_h  = 0.45  * (h/1.65)
hip_h    = 0.12  * (h/1.65)
leg_h    = 0.78  * (h/1.65) * 0.5
arm_h    = 0.55  * (h/1.65) * 0.5

shoulder_w = 0.34 * (h/1.65)
hip_w      = 0.28 * (h/1.65)

# Root Z offsets
z_feet   = 0.0
z_legtop = z_feet + (leg_h * 2)
z_hip    = z_legtop + hip_h
z_torso  = z_hip + torso_h
z_neck   = z_torso + neck_h
z_head   = z_neck + head_r*1.2

# -------------------------
# Legs (skin parts will be covered by jeans, but keep simple)
# -------------------------
leg_r = 0.055 * (h/1.65)
calf_r= 0.050 * (h/1.65)

# Left leg
legL = add_cylinder("Leg_L", radius=leg_r, depth=leg_h*2, seg=SEG_BODY,
                    loc=(-hip_w*0.35, 0, leg_h))
# Right leg
legR = add_cylinder("Leg_R", radius=leg_r, depth=leg_h*2, seg=SEG_BODY,
                    loc=( hip_w*0.35, 0, leg_h))

# Slight knee/stance variation (object-level, then apply)
legL.rotation_euler = Euler((0, 0, math.radians(1)), 'XYZ')
legR.rotation_euler = Euler((math.radians(1), 0, math.radians(-1)), 'XYZ')

# -------------------------
# Shoes
# -------------------------
shoe_len = 0.24 * (h/1.65)
shoe_w   = 0.10 * (h/1.65)
shoe_h   = 0.08 * (h/1.65)

shoeL = add_cube("Shoe_L", size=1.0, loc=(-hip_w*0.35, shoe_len*0.15, shoe_h*0.5))
shoeL.scale = (shoe_w*0.5, shoe_len*0.5, shoe_h*0.5)

shoeR = add_cube("Shoe_R", size=1.0, loc=( hip_w*0.35, shoe_len*0.15, shoe_h*0.5))
shoeR.scale = (shoe_w*0.5, shoe_len*0.5, shoe_h*0.5)

# Round-ish shoes via bevel modifier (still low-poly)
for s in (shoeL, shoeR):
    bev = s.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.01*(h/1.65)
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    shade_smooth_auto(s, 60)
    s.data.materials.append(mat_shoes)

# -------------------------
# Hips + Torso (skin base)
# -------------------------
hips = add_cylinder("Hips", radius=hip_w*0.55, depth=hip_h, seg=SEG_BODY,
                    loc=(0, 0, z_legtop + hip_h*0.5))
torso = add_cylinder("Torso", radius=shoulder_w*0.42, depth=torso_h, seg=SEG_BODY,
                     loc=(0, 0, z_hip + torso_h*0.5))

# Slight weight shift
hips.location.x += WEIGHT_SHIFT
torso.location.x += WEIGHT_SHIFT * 0.6

# -------------------------
# Head + Hair
# -------------------------
head = add_uv_sphere("Head", radius=head_r, seg_u=SEG_HEAD, seg_v=SEG_HEAD//2,
                     loc=(WEIGHT_SHIFT*0.5, 0, z_neck + head_r*1.05))
# Subtle face direction
head.rotation_euler = Euler((0, 0, math.radians(2)), 'XYZ')

# Simple hair cap
hair = add_uv_sphere("Hair", radius=head_r*1.03, seg_u=SEG_HEAD, seg_v=SEG_HEAD//2,
                     loc=head.location)
# Flatten hair to look like cap + volume at back
hair.scale = (1.0, 1.05, 0.92)
hair.location.y -= head_r*0.05

# Remove lower half of hair sphere (quick boolean via bisect in edit mode)
bpy.context.view_layer.objects.active = hair
hair.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bisect(plane_co=(0,0,head.location.z - head_r*0.08), plane_no=(0,0,1), clear_inner=True)
bpy.ops.object.mode_set(mode='OBJECT')
hair.select_set(False)

# -------------------------
# Arms (relaxed)
# -------------------------
arm_r = 0.040 * (h/1.65)
hand_r= 0.035 * (h/1.65)

# Upper arm cylinders approximated as one piece each (low poly)
armZ = z_hip + torso_h*0.80
armL = add_cylinder("Arm_L", radius=arm_r, depth=arm_h*2, seg=SEG_BODY,
                    loc=(-shoulder_w*0.55 + WEIGHT_SHIFT*0.2, 0.02, armZ - arm_h))
armR = add_cylinder("Arm_R", radius=arm_r, depth=arm_h*2, seg=SEG_BODY,
                    loc=( shoulder_w*0.55 + WEIGHT_SHIFT*0.2, 0.02, armZ - arm_h))

# Rotate arms down/out slightly (relaxed)
armL.rotation_euler = Euler((math.radians(3), 0,  ARM_RELAX_ANGLE), 'XYZ')
armR.rotation_euler = Euler((math.radians(3), 0, -ARM_RELAX_ANGLE), 'XYZ')

# Hands
handL = add_uv_sphere("Hand_L", radius=hand_r, seg_u=SEG_HAND_FOOT, seg_v=SEG_HAND_FOOT//2,
                      loc=(armL.location.x - 0.02, 0.02, z_hip + torso_h*0.30))
handR = add_uv_sphere("Hand_R", radius=hand_r, seg_u=SEG_HAND_FOOT, seg_v=SEG_HAND_FOOT//2,
                      loc=(armR.location.x + 0.02, 0.02, z_hip + torso_h*0.30))

# -------------------------
# Clothing: T-Shirt (shell over torso)
# -------------------------
shirt = add_cylinder("TShirt", radius=(shoulder_w*0.42)*1.03, depth=torso_h*0.72, seg=SEG_BODY,
                     loc=torso.location)
shirt.location.z += torso_h*0.06

# sleeves: two short cylinders
sleeve_r = arm_r*1.15
sleeve_d = TSHIRT_SLEEVE_LEN*(h/1.65)
sleeveL = add_cylinder("Sleeve_L", radius=sleeve_r, depth=sleeve_d, seg=SEG_BODY,
                       loc=(armL.location.x, 0.03, armZ + 0.01))
sleeveR = add_cylinder("Sleeve_R", radius=sleeve_r, depth=sleeve_d, seg=SEG_BODY,
                       loc=(armR.location.x, 0.03, armZ + 0.01))
# orient sleeves to roughly follow arms
sleeveL.rotation_euler = armL.rotation_euler
sleeveR.rotation_euler = armR.rotation_euler

# -------------------------
# Clothing: Jeans (shell over legs + hips)
# -------------------------
jeansL = add_cylinder("Jeans_L", radius=leg_r*1.06, depth=leg_h*2.05, seg=SEG_BODY,
                      loc=legL.location)
jeansR = add_cylinder("Jeans_R", radius=leg_r*1.06, depth=leg_h*2.05, seg=SEG_BODY,
                      loc=legR.location)
jeansH = add_cylinder("Jeans_Hips", radius=hip_w*0.56, depth=hip_h*1.10, seg=SEG_BODY,
                      loc=hips.location)

# Optional cuffs
if JEANS_CUFF_HEIGHT > 0.0:
    cuffH = JEANS_CUFF_HEIGHT*(h/1.65)
    cuffL = add_cylinder("Cuff_L", radius=leg_r*1.09, depth=cuffH, seg=SEG_BODY,
                         loc=(jeansL.location.x, 0, cuffH*0.5))
    cuffR = add_cylinder("Cuff_R", radius=leg_r*1.09, depth=cuffH, seg=SEG_BODY,
                         loc=(jeansR.location.x, 0, cuffH*0.5))
    cuffL.data.materials.append(mat_jeans)
    cuffR.data.materials.append(mat_jeans)
    shade_smooth_auto(cuffL, 60)
    shade_smooth_auto(cuffR, 60)

# -------------------------
# Materials assignment
# -------------------------
for o in (head, hips, torso, armL, armR, handL, handR, legL, legR):
    o.data.materials.append(mat_skin)

hair.data.materials.append(mat_hair)

for o in (shirt, sleeveL, sleeveR):
    o.data.materials.append(mat_shirt)

for o in (jeansL, jeansR, jeansH):
    o.data.materials.append(mat_jeans)

# Smooth shading
for o in (head, hair, hips, torso, armL, armR, handL, handR, legL, legR, shirt, sleeveL, sleeveR, jeansL, jeansR, jeansH):
    shade_smooth_auto(o, 60)

# -------------------------
# Apply transforms + join for clean export
# -------------------------
all_objs = [head, hair, hips, torso, armL, armR, handL, handR, legL, legR,
            shirt, sleeveL, sleeveR, jeansL, jeansR, jeansH, shoeL, shoeR]

for o in all_objs:
    apply_all(o)

# Join into one mesh object (good for static Three.js use)
# If you prefer separate meshes for materials, you can skip joining; GLB supports multiple objects.
body_join = join_objects(all_objs, "Woman_LowPoly_Static")

# Ensure origin at feet, Z-up, centered
bpy.context.view_layer.objects.active = body_join
body_join.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
# move so lowest point sits on Z=0
min_z = min((body_join.matrix_world @ Vector(v.co)).z for v in body_join.data.vertices)
body_join.location.z -= min_z
apply_all(body_join)
body_join.select_set(False)

# -------------------------
# Export GLB
# -------------------------
# Recommended for Three.js:
bpy.ops.export_scene.gltf(
    filepath=EXPORT_PATH,
    export_format='GLB',
    export_yup=True,
    export_apply=True,
    export_texcoords=True,
    export_normals=True,
    export_materials='EXPORT',
    export_colors=True
)

print(f"Export done: {EXPORT_PATH}")
