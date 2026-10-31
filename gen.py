import json, re, os, random, math, shutil
from PIL import Image, ImageDraw

SRC = "/mnt/user-data/uploads/gem-enchantments-table.html"
ROOT = "/home/claude/gemghoul-mod"
MOD = "gemghoul"
PKG = "com/gemghoul"
shutil.rmtree(ROOT, ignore_errors=True)

def w(path, text):
    p = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)

def wj(path, obj):
    w(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- data
txt = open(SRC, encoding="utf-8").read()
D = json.loads(re.search(r"var D=(\[.*?\]);\s*var B", txt, re.S).group(1))
SPECIAL = {"Curse of Binding": "binding_curse", "Curse of Vanishing": "vanishing_curse"}
VANILLA = {"Diamond": "diamond", "Emerald": "emerald", "Lapis Lazuli": "lapis_lazuli", "Amethyst": "amethyst_shard"}
TREASURE = {"mending", "frost_walker", "soul_speed", "swift_sneak", "wind_burst"}
CURSE = {"binding_curse", "vanishing_curse"}

gems = []
for cat, rows in D:
    for ench, gem, color, desc in rows:
        gems.append(dict(
            ench=SPECIAL.get(ench, ench.lower().replace(" ", "_")),
            name=gem,
            id=gem.lower().replace("'", "").replace(" ", "_"),
            color=color, desc=desc,
            vanilla=VANILLA.get(gem)))
print(len(gems), "gems,", sum(1 for g in gems if not g["vanilla"]), "custom")

# ---------------------------------------------------------------- lang
lang = {
    "block.gemghoul.gem_altar": "Ghoul Gem Altar",
    "container.gemghoul.gem_altar": "Ghoul Gem Altar",
    "itemGroup.gemghoul": "Gem Ghoul",
    "gemghoul.cost": "Cost: %s levels",
    "gemghoul.level": "Level %s",
}
for g in gems:
    lang["gemghoul.gem." + g["id"]] = g["name"]
    lang["gemghoul.gem." + g["id"] + ".desc"] = g["desc"]
    if not g["vanilla"]:
        lang["item.gemghoul." + g["id"]] = g["name"]
wj("src/main/resources/assets/gemghoul/lang/en_us.json", lang)

# enchantment names -> gem names (in the minecraft namespace so they win over vanilla files)
ench_lang = {"enchantment.minecraft." + g["ench"]: g["name"] for g in gems}
wj("src/main/resources/assets/minecraft/lang/en_us.json", ench_lang)
wj("src/main/resources/assets/minecraft/lang/ar_sa.json", ench_lang)

# ---------------------------------------------------------------- gem textures
def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def lighten(c, t): return tuple(int(v + (255 - v) * min(1, t)) for v in c)
def dark(c, f): return tuple(int(v * f) for v in c)

POLY = {
    "kite": [(4, 2), (11, 2), (14, 6), (8, 14), (7, 14), (1, 6)],
    "emerald": [(4, 2), (11, 2), (13, 4), (13, 11), (11, 13), (4, 13), (2, 11), (2, 4)],
    "tear": [(7, 1), (8, 1), (11, 6), (12, 9), (11, 12), (8, 14), (7, 14), (4, 12), (3, 9), (4, 6)],
    "trillion": [(7, 2), (8, 2), (14, 12), (13, 13), (2, 13), (1, 12)],
    "hex": [(5, 2), (10, 2), (14, 8), (10, 13), (5, 13), (1, 8)],
    "shard": [(7, 1), (8, 1), (11, 4), (11, 13), (8, 14), (7, 14), (4, 13), (4, 4)],
    "square": [(3, 2), (12, 2), (13, 3), (13, 12), (12, 13), (3, 13), (2, 12), (2, 3)],
}
STYLE = {  # name: (shape, style)
    "Ruby": ("kite", "faceted"), "Carnelian": ("oval", "smooth"), "Hematite": ("hex", "faceted"),
    "Tourmaline": ("shard", "faceted"), "Sapphire": ("oval", "faceted"), "Amber": ("tear", "smooth"),
    "Moonstone": ("round", "sparkle"), "Aquamarine": ("emerald", "faceted"), "Blue Chalcedony": ("cab", "smooth"),
    "Smoky Quartz": ("shard", "faceted"), "Opal": ("oval", "sparkle"), "Turquoise": ("cab", "smooth"),
    "Selenite": ("shard", "faceted"), "Moissanite": ("kite", "faceted"), "Peridot": ("square", "faceted"),
    "Tiger's Eye": ("oval", "banded"), "Fire Opal": ("round", "sparkle"), "Golden Beryl": ("emerald", "faceted"),
    "Kyanite": ("shard", "faceted"), "Topaz": ("tear", "faceted"), "Rose Quartz": ("hex", "faceted"),
    "Citrine": ("square", "faceted"), "Red Spinel": ("round", "faceted"), "Garnet": ("hex", "faceted"),
    "Sunstone": ("round", "sparkle"), "Alexandrite": ("tear", "faceted"), "Labradorite": ("oval", "sparkle"),
    "Tanzanite": ("trillion", "faceted"), "Zircon": ("kite", "faceted"), "Pearl": ("round", "pearl"),
    "Onyx": ("oval", "smooth"), "Larimar": ("cab", "banded"), "Charoite": ("cab", "banded"),
    "Jasper": ("cab", "banded"), "Bloodstone": ("oval", "bloodstone"), "Celestite": ("shard", "faceted"),
    "Jade": ("cab", "smooth"), "Rhodochrosite": ("oval", "banded"),
}

def render_gem(shape, style, rgb, seed):
    rnd = random.Random(seed)
    m = Image.new("L", (16, 16), 0); d = ImageDraw.Draw(m)
    if shape == "round": d.ellipse([2, 2, 13, 13], fill=255)
    elif shape == "oval": d.ellipse([3, 1, 12, 14], fill=255)
    elif shape == "cab": d.ellipse([1, 3, 14, 12], fill=255)
    else: d.polygon(POLY[shape], fill=255)
    px = m.load()
    pts = [(x, y) for y in range(16) for x in range(16) if px[x, y] > 0]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx = (min(xs) + max(xs)) / 2; cy = (min(ys) + max(ys)) / 2
    r = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + 0.5
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); ip = img.load()
    inm = lambda x, y: 0 <= x < 16 and 0 <= y < 16 and px[x, y] > 0
    rainbow = [(255, 120, 160), (120, 200, 255), (255, 230, 120), (150, 255, 190)]
    for (x, y) in pts:
        edge = not (inm(x - 1, y) and inm(x + 1, y) and inm(x, y - 1) and inm(x, y + 1))
        dx, dy = x - cx, y - cy
        dist = math.hypot(dx, dy) / r
        ang = math.atan2(dy, dx)
        if edge:
            col = dark(rgb, 0.42)
        elif style == "faceted":
            a = ((ang + math.pi) / (2 * math.pi)) * 8
            f = [1.2, 1.0, 0.8, 0.9, 1.15, 0.95, 0.75, 0.88][int(a) % 8]
            col = lighten(rgb, (f - 1) * 1.6) if f > 1 else dark(rgb, f)
            if dist < 0.4: col = lighten(rgb, 0.35)
            frac = a - int(a)
            if 0.4 <= dist < 0.95 and (frac < 0.1 or frac > 0.9): col = dark(col, 0.8)
        else:
            t = (dx + dy) / (2 * r)
            light = 1.12 - 0.42 * (t + 1) / 2
            col = lighten(rgb, (light - 1) * 1.6) if light > 1 else dark(rgb, light)
            if math.hypot(x - (cx - 0.35 * r), y - (cy - 0.4 * r)) < 1.6: col = lighten(col, 0.55)
            if style == "banded" and ((x * 2 + y) // 3) % 2: col = dark(col, 0.82)
            if style == "sparkle" and rnd.random() < 0.18:
                s = rnd.choice(rainbow); col = tuple(int(col[i] * 0.55 + s[i] * 0.45) for i in range(3))
            if style == "bloodstone" and rnd.random() < 0.13: col = (190, 30, 40)
            if style == "pearl": col = lighten(col, 0.18)
        ip[x, y] = col + (255,)
    sx, sy = int(cx - r * 0.42), int(cy - r * 0.5)
    if inm(sx, sy) and ip[sx, sy][3]: ip[sx, sy] = (255, 255, 255, 255)
    return img

TEX = "src/main/resources/assets/gemghoul/textures"
os.makedirs(os.path.join(ROOT, TEX, "item"), exist_ok=True)
sheet = Image.new("RGBA", (16 * 8 * 4, 16 * 5 * 4), (40, 40, 48, 255))
k = 0
for i, g in enumerate(gems):
    if g["vanilla"]: continue
    shape, style = STYLE[g["name"]]
    im = render_gem(shape, style, hx(g["color"]), i)
    im.save(os.path.join(ROOT, TEX, "item", g["id"] + ".png"))
    sheet.paste(im.resize((64, 64), Image.NEAREST), ((k % 8) * 64, (k // 8) * 64), im.resize((64, 64), Image.NEAREST))
    k += 1
    wj(f"src/main/resources/assets/gemghoul/models/item/{g['id']}.json",
       {"parent": "minecraft:item/generated", "textures": {"layer0": f"gemghoul:item/{g['id']}"}})
sheet.save("/home/claude/sheet.png")

# ---------------------------------------------------------------- ghoul altar texture (64x64, 4x4 cells of 16px)
rnd = random.Random(7)
def noise_cell(img, cx, cy, base, amp=10):
    p = img.load()
    for y in range(16):
        for x in range(16):
            n = rnd.randint(-amp, amp)
            p[cx * 16 + x, cy * 16 + y] = tuple(max(0, min(255, base[i] + n)) for i in range(3)) + (255,)
alt = Image.new("RGBA", (64, 64), (255, 0, 255, 255))
noise_cell(alt, 0, 0, (58, 50, 72)); noise_cell(alt, 1, 0, (92, 82, 110), 8)
noise_cell(alt, 2, 0, (40, 34, 58), 5); noise_cell(alt, 3, 0, (212, 175, 55), 12)
noise_cell(alt, 0, 1, (98, 128, 92), 9); noise_cell(alt, 1, 1, (66, 88, 64), 8)
noise_cell(alt, 2, 1, (98, 128, 92), 9); noise_cell(alt, 3, 1, (225, 218, 195), 8)
ad = ImageDraw.Draw(alt)
ad.ellipse([32 + 2, 2, 32 + 13, 13], outline=(150, 90, 255, 255))          # rune circle on altar top
ad.ellipse([32 + 5, 5, 32 + 10, 10], outline=(90, 220, 255, 255))
ad.line([32 + 7, 1, 32 + 7, 14], fill=(150, 90, 255, 255)); ad.line([32 + 1, 7, 32 + 14, 7], fill=(150, 90, 255, 255))
for (x0, y0) in [(0, 0)]:                                                  # brick lines on trim stone
    for yy in (4, 9, 14): ad.line([16, yy, 31, yy], fill=(60, 52, 78, 255))
ad.rectangle([32 + 3, 16 + 5, 32 + 5, 16 + 7], fill=(255, 226, 60, 255))    # face (cell 2,1): eyes
ad.rectangle([32 + 10, 16 + 5, 32 + 12, 16 + 7], fill=(255, 226, 60, 255))
ad.point([32 + 4, 16 + 6], fill=(20, 20, 20, 255)); ad.point([32 + 11, 16 + 6], fill=(20, 20, 20, 255))
ad.rectangle([32 + 4, 16 + 10, 32 + 11, 16 + 13], fill=(25, 12, 20, 255))   # mouth
for tx in (5, 7, 9): ad.rectangle([32 + tx, 16 + 10, 32 + tx, 16 + 11], fill=(235, 235, 220, 255))
ad.point([32 + 7, 16 + 8], fill=(50, 70, 48, 255)); ad.point([32 + 8, 16 + 8], fill=(50, 70, 48, 255))
alt.save(os.path.join(ROOT, TEX, "block", "gem_altar.png") if os.path.isdir(os.path.join(ROOT, TEX, "block")) else "/tmp/x.png")
os.makedirs(os.path.join(ROOT, TEX, "block"), exist_ok=True)
alt.save(os.path.join(ROOT, TEX, "block", "gem_altar.png"))

def cell(c, r): return [c * 4, r * 4, c * 4 + 4, r * 4 + 4]
STONE, TRIM, RUNE, GOLD, SKIN, SKIND, FACE, BONE = cell(0, 0), cell(1, 0), cell(2, 0), cell(3, 0), cell(0, 1), cell(1, 1), cell(2, 1), cell(3, 1)

def element(frm, to, side, up=None, down=None, north=None):
    up = up or side; down = down or side; north = north or side
    return {"from": frm, "to": to, "faces": {
        "north": {"uv": north, "texture": "#main"}, "south": {"uv": side, "texture": "#main"},
        "east": {"uv": side, "texture": "#main"}, "west": {"uv": side, "texture": "#main"},
        "up": {"uv": up, "texture": "#main"}, "down": {"uv": down, "texture": "#main"}}}

els = [
    element([1, 0, 1], [15, 3, 15], STONE, up=TRIM),
    element([4, 3, 4], [12, 7, 12], TRIM),
    element([0, 7, 0], [16, 9, 16], STONE, up=RUNE),
    element([0.5, 9, 0.5], [2.5, 10, 2.5], GOLD), element([13.5, 9, 0.5], [15.5, 10, 2.5], GOLD),
    element([0.5, 9, 13.5], [2.5, 10, 15.5], GOLD), element([13.5, 9, 13.5], [15.5, 10, 15.5], GOLD),
    # ghoul (faces north)
    element([5, 9, 6], [7.5, 11, 9], SKIN), element([8.5, 9, 6], [11, 11, 9], SKIN),
    element([4.5, 10.5, 5.5], [11.5, 15.5, 10.5], SKIN, up=SKIND, down=SKIND),
    element([5.5, 15, 4], [10.5, 20, 9], SKIN, up=SKIND, north=FACE),
    element([2.5, 9, 4.5], [4.5, 15, 6.5], SKIN, down=BONE),
    element([11.5, 9, 4.5], [13.5, 15, 6.5], SKIN, down=BONE),
    element([6, 13, 10.5], [7, 16, 11.5], BONE), element([9, 13, 10.5], [10, 16, 11.5], BONE),
]
wj("src/main/resources/assets/gemghoul/models/block/gem_altar.json",
   {"parent": "minecraft:block/block", "textures": {"particle": "gemghoul:block/gem_altar", "main": "gemghoul:block/gem_altar"}, "elements": els})
wj("src/main/resources/assets/gemghoul/models/item/gem_altar.json",
   {"parent": "gemghoul:block/gem_altar", "display": {"gui": {"rotation": [30, 225, 0], "translation": [0, -2, 0], "scale": [0.45, 0.45, 0.45]}}})
wj("src/main/resources/assets/gemghoul/blockstates/gem_altar.json", {"variants": {
    "facing=north": {"model": "gemghoul:block/gem_altar"},
    "facing=east": {"model": "gemghoul:block/gem_altar", "y": 90},
    "facing=south": {"model": "gemghoul:block/gem_altar", "y": 180},
    "facing=west": {"model": "gemghoul:block/gem_altar", "y": 270}}})

# ---------------------------------------------------------------- bookshelf -> colored ore
rb = random.Random(11)
def stone(amp=12):
    im = Image.new("RGBA", (16, 16)); p = im.load()
    for y in range(16):
        for x in range(16):
            n = rb.randint(-amp, amp); b = 122 + n
            if rb.random() < 0.08: b -= 22
            p[x, y] = (b, b, b + 3, 255)
    return im
ore = stone(); op = ore.load()
ORE = [(224, 30, 60), (40, 90, 230), (30, 200, 100), (160, 80, 230), (250, 190, 40), (60, 210, 220), (255, 120, 40), (240, 120, 180)]
spots = [(2, 2), (9, 1), (5, 6), (11, 7), (1, 10), (7, 11), (12, 12), (3, 13)]
for (sx, sy), col in zip(spots, ORE):
    for (dx, dy) in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1)]:
        x, y = sx + dx, sy + dy
        if x < 16 and y < 16: op[x, y] = col + (255,)
    op[sx, sy] = lighten(col, 0.55) + (255,)
    if sx + 2 < 16 and sy + 2 < 16: op[sx + 1, sy + 2] = dark(col, 0.55) + (255,)
ore.save(os.path.join(ROOT, "src/main/resources/assets/minecraft/textures/block/bookshelf.png")) if os.path.isdir(os.path.join(ROOT, "src/main/resources/assets/minecraft/textures/block")) else None
os.makedirs(os.path.join(ROOT, "src/main/resources/assets/minecraft/textures/block"), exist_ok=True)
ore.save(os.path.join(ROOT, "src/main/resources/assets/minecraft/textures/block/bookshelf.png"))
top = stone(8); tp = top.load()
for i in range(16):
    for e in ((i, 0), (i, 15), (0, i), (15, i)): tp[e] = (85, 85, 90, 255)
top.save(os.path.join(ROOT, TEX, "block", "gem_shelf_top.png"))
wj("src/main/resources/assets/minecraft/models/block/bookshelf.json",
   {"parent": "minecraft:block/cube_column", "textures": {"end": "gemghoul:block/gem_shelf_top", "side": "minecraft:block/bookshelf"}})

# ---------------------------------------------------------------- GUI texture (256x256, panel 176x166)
gui = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); gd = ImageDraw.Draw(gui)
gd.rectangle([0, 0, 175, 165], fill=(198, 198, 198, 255), outline=(20, 16, 28, 255))
gd.line([1, 1, 174, 1], fill=(255, 255, 255, 255)); gd.line([1, 1, 1, 164], fill=(255, 255, 255, 255))
gd.line([1, 164, 174, 164], fill=(85, 85, 85, 255)); gd.line([174, 1, 174, 164], fill=(85, 85, 85, 255))
def slot(x, y):
    gd.rectangle([x - 1, y - 1, x + 16, y + 16], fill=(139, 139, 139, 255))
    gd.line([x - 1, y - 1, x + 16, y - 1], fill=(55, 55, 55, 255)); gd.line([x - 1, y - 1, x - 1, y + 16], fill=(55, 55, 55, 255))
    gd.line([x - 1, y + 16, x + 16, y + 16], fill=(255, 255, 255, 255)); gd.line([x + 16, y - 1, x + 16, y + 16], fill=(255, 255, 255, 255))
slot(15, 47)
for r in range(3):
    for c in range(9): slot(8 + 18 * c, 84 + 18 * r)
for c in range(9): slot(8 + 18 * c, 142)
for i in range(3):
    gd.rectangle([60, 14 + 19 * i, 167, 32 + 19 * i], fill=(38, 26, 58, 255), outline=(110, 80, 170, 255))
gd.rectangle([8, 12, 53, 41], fill=(28, 22, 38, 255), outline=(90, 70, 130, 255))      # ghoul portrait
gd.rectangle([20, 18, 41, 38], fill=(98, 128, 92, 255))
gd.rectangle([23, 24, 26, 27], fill=(255, 226, 60, 255)); gd.rectangle([35, 24, 38, 27], fill=(255, 226, 60, 255))
gd.rectangle([24, 32, 37, 36], fill=(25, 12, 20, 255))
for tx in (26, 29, 32, 35): gd.rectangle([tx, 32, tx, 33], fill=(235, 235, 220, 255))
os.makedirs(os.path.join(ROOT, TEX, "gui"), exist_ok=True)
gui.save(os.path.join(ROOT, TEX, "gui", "gem_altar.png"))

# ---------------------------------------------------------------- data (recipe, loot, tags)
wj("src/main/resources/data/gemghoul/recipe/gem_altar.json", {
    "type": "minecraft:crafting_shaped", "category": "misc",
    "key": {"F": {"item": "minecraft:rotten_flesh"}, "D": {"item": "minecraft:diamond"}, "O": {"item": "minecraft:obsidian"}},
    "pattern": [" F ", "DOD", "OOO"], "result": {"id": "gemghoul:gem_altar", "count": 1}})
wj("src/main/resources/data/gemghoul/loot_table/blocks/gem_altar.json", {
    "type": "minecraft:block", "pools": [{"rolls": 1.0, "bonus_rolls": 0.0,
    "entries": [{"type": "minecraft:item", "name": "gemghoul:gem_altar"}],
    "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
wj("src/main/resources/data/minecraft/tags/block/mineable/pickaxe.json", {"values": ["gemghoul:gem_altar"]})
wj("src/main/resources/data/minecraft/tags/block/needs_diamond_tool.json", {"values": ["gemghoul:gem_altar"]})

w("src/main/templates/META-INF/neoforge.mods.toml", '''modLoader="javafml"
loaderVersion="[4,)"
license="MIT"

[[mods]]
modId="gemghoul"
version="1.0.0"
displayName="Gem Ghoul"
description=\'\'\'Enchant with gemstones. A ghoul on an altar offers three random gems for your tool.\'\'\'

[[dependencies.gemghoul]]
modId="neoforge"
type="required"
versionRange="[21.1.0,)"
ordering="NONE"
side="BOTH"

[[dependencies.gemghoul]]
modId="minecraft"
type="required"
versionRange="[1.21.1,1.22)"
ordering="NONE"
side="BOTH"
''')

# ---------------------------------------------------------------- Java
J = "src/main/java/" + PKG + "/"
rows = []
for g in gems:
    van = '"%s"' % g["vanilla"] if g["vanilla"] else "null"
    rows.append('        new Gem("%s", "%s", 0x%s, %s, %s, %s)' % (
        g["id"], g["ench"], g["color"].lstrip("#").upper(), van,
        str(g["ench"] in TREASURE).lower(), str(g["ench"] in CURSE).lower()))
w(J + "Gems.java", '''package com.gemghoul;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.enchantment.Enchantment;

/** Generated from gem-enchantments-table.html: one gem per vanilla enchantment. */
public final class Gems {
    public record Gem(String id, String enchantment, int color, String vanillaItem, boolean treasure, boolean curse) {
        /** Very dark gems (Onyx...) are lightened so their names stay readable. */
        public int displayColor() {
            int r = (color >> 16) & 255, g = (color >> 8) & 255, b = color & 255;
            if (0.299 * r + 0.587 * g + 0.114 * b < 110) {
                r += (255 - r) * 55 / 100; g += (255 - g) * 55 / 100; b += (255 - b) * 55 / 100;
            }
            return (r << 16) | (g << 8) | b;
        }
    }

    public static final List<Gem> ALL = List.of(
''' + ",\n".join(rows) + '''
    );

    private static Map<Item, Gem> vanillaMap;

    public static ResourceKey<Enchantment> key(Gem g) {
        return ResourceKey.create(Registries.ENCHANTMENT, ResourceLocation.withDefaultNamespace(g.enchantment()));
    }

    public static MutableComponent name(Gem g) {
        return Component.translatable("gemghoul.gem." + g.id());
    }

    public static MutableComponent coloredName(Gem g) {
        return name(g).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(g.displayColor())));
    }

    public static MutableComponent desc(Gem g) {
        return Component.translatable("gemghoul.gem." + g.id() + ".desc");
    }

    /** The item that represents this gem (a vanilla item for Diamond, Emerald, Lapis, Amethyst). */
    public static Item itemOf(Gem g) {
        if (g.vanillaItem() != null) {
            return BuiltInRegistries.ITEM.get(ResourceLocation.withDefaultNamespace(g.vanillaItem()));
        }
        return ModItems.GEM_ITEMS.get(g.id()).get();
    }

    public static Gem byVanillaItem(Item item) {
        if (vanillaMap == null) {
            Map<Item, Gem> m = new HashMap<>();
            for (Gem g : ALL) {
                if (g.vanillaItem() != null) m.put(itemOf(g), g);
            }
            vanillaMap = m;
        }
        return vanillaMap.get(item);
    }

    private Gems() {}
}
''')

w(J + "GemGhoulMod.java", '''package com.gemghoul;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(GemGhoulMod.MODID)
public class GemGhoulMod {
    public static final String MODID = "gemghoul";

    public GemGhoulMod(IEventBus modBus) {
        ModBlocks.BLOCKS.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModMenus.MENUS.register(modBus);
        ModTabs.TABS.register(modBus);
    }
}
''')

w(J + "ModBlocks.java", '''package com.gemghoul;

import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(GemGhoulMod.MODID);

    public static final DeferredBlock<GemAltarBlock> GEM_ALTAR = BLOCKS.register("gem_altar",
            () -> new GemAltarBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_PURPLE)
                    .strength(5.0F, 1200.0F)
                    .requiresCorrectToolForDrops()
                    .lightLevel(state -> 7)
                    .noOcclusion()));
}
''')

w(J + "ModItems.java", '''package com.gemghoul;

import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(GemGhoulMod.MODID);

    public static final DeferredItem<BlockItem> GEM_ALTAR_ITEM = ITEMS.registerSimpleBlockItem("gem_altar", ModBlocks.GEM_ALTAR);

    /** Only gems that do not already exist in vanilla get their own item. */
    public static final Map<String, DeferredItem<Item>> GEM_ITEMS = new LinkedHashMap<>();

    static {
        for (Gems.Gem gem : Gems.ALL) {
            if (gem.vanillaItem() == null) {
                GEM_ITEMS.put(gem.id(), ITEMS.<Item>register(gem.id(), () -> new GemItem(new Item.Properties(), gem)));
            }
        }
    }
}
''')

w(J + "GemItem.java", '''package com.gemghoul;

import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

public class GemItem extends Item {
    private final Gems.Gem gem;

    public GemItem(Properties properties, Gems.Gem gem) {
        super(properties);
        this.gem = gem;
    }

    /** Gem name on top, tinted with the gem color. */
    @Override
    public Component getName(ItemStack stack) {
        return Component.translatable(this.getDescriptionId())
                .withStyle(Style.EMPTY.withColor(TextColor.fromRgb(gem.displayColor())));
    }

    /** What the gem does, below the name. */
    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Gems.desc(gem).withStyle(ChatFormatting.GRAY));
    }
}
''')

w(J + "ModMenus.java", '''package com.gemghoul;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.MenuType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModMenus {
    public static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, GemGhoulMod.MODID);

    public static final DeferredHolder<MenuType<?>, MenuType<GemAltarMenu>> GEM_ALTAR =
            MENUS.register("gem_altar", () -> new MenuType<>(GemAltarMenu::new, FeatureFlags.DEFAULT_FLAGS));
}
''')

w(J + "ModTabs.java", '''package com.gemghoul;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, GemGhoulMod.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.gemghoul"))
                    .icon(() -> new ItemStack(ModItems.GEM_ALTAR_ITEM.get()))
                    .displayItems((params, output) -> {
                        output.accept(ModItems.GEM_ALTAR_ITEM.get());
                        for (DeferredHolder<Item, Item> gem : ModItems.GEM_ITEMS.values()) {
                            output.accept(gem.get());
                        }
                    })
                    .build());
}
''')

w(J + "GemAltarBlock.java", '''package com.gemghoul;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EnchantingTableBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A stone altar with a ghoul crouching on it. Right-click to open the gem menu. */
public class GemAltarBlock extends HorizontalDirectionalBlock {
    public static final MapCodec<GemAltarBlock> CODEC = simpleCodec(GemAltarBlock::new);
    private static final VoxelShape SHAPE = Block.box(0, 0, 0, 16, 19, 16);
    private static final VoxelShape COLLISION = Block.box(0, 0, 0, 16, 16, 16);

    public GemAltarBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FACING, Direction.NORTH));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        // the ghoul looks at the player
        return defaultBlockState().setValue(FACING, context.getHorizontalDirection().getOpposite());
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    @Override
    protected VoxelShape getCollisionShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return COLLISION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        player.openMenu(new SimpleMenuProvider(
                (id, inventory, p) -> new GemAltarMenu(id, inventory, ContainerLevelAccess.create(level, pos)),
                Component.translatable("container.gemghoul.gem_altar")));
        return InteractionResult.CONSUME;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        // gem shelves send enchant glyphs to the ghoul, exactly like bookshelves do for the vanilla table
        for (BlockPos off : EnchantingTableBlock.BOOKSHELF_OFFSETS) {
            if (random.nextInt(16) == 0 && EnchantingTableBlock.isValidBookShelf(level, pos, off)) {
                level.addParticle(ParticleTypes.ENCHANT,
                        pos.getX() + 0.5, pos.getY() + 1.6, pos.getZ() + 0.5,
                        off.getX() + random.nextFloat() - 0.5, off.getY() - random.nextFloat() - 1.0F,
                        off.getZ() + random.nextFloat() - 0.5);
            }
        }
        if (random.nextInt(8) == 0) {
            level.addParticle(ParticleTypes.SOUL,
                    pos.getX() + 0.5 + (random.nextDouble() - 0.5) * 0.4, pos.getY() + 1.1,
                    pos.getZ() + 0.5 + (random.nextDouble() - 0.5) * 0.4, 0.0, 0.02, 0.0);
        }
    }
}
''')

w(J + "GemAltarMenu.java", '''package com.gemghoul;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.EnchantingTableBlock;

public class GemAltarMenu extends AbstractContainerMenu {
    /** Max gems socketed in one tool. */
    public static final int MAX_GEMS = 3;

    private final Container toolSlot = new SimpleContainer(1) {
        @Override
        public void setChanged() {
            super.setChanged();
            GemAltarMenu.this.slotsChanged(this);
        }
    };
    private final ContainerLevelAccess access;
    private final Player owner;
    private final RandomSource random = RandomSource.create();
    /** 0-2 = level cost, 3-5 = gem index (-1 none), 6-8 = gem level. Synced to the client. */
    private final ContainerData data = new SimpleContainerData(9);

    public GemAltarMenu(int id, Inventory inventory) {
        this(id, inventory, ContainerLevelAccess.NULL);
    }

    public GemAltarMenu(int id, Inventory inventory, ContainerLevelAccess access) {
        super(ModMenus.GEM_ALTAR.get(), id);
        this.access = access;
        this.owner = inventory.player;
        for (int i = 0; i < 3; i++) data.set(3 + i, -1);

        addSlot(new Slot(toolSlot, 0, 15, 47) {
            @Override
            public int getMaxStackSize() {
                return 1;
            }
        });
        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 9; col++)
                addSlot(new Slot(inventory, col + row * 9 + 9, 8 + col * 18, 84 + row * 18));
        for (int col = 0; col < 9; col++)
            addSlot(new Slot(inventory, col, 8 + col * 18, 142));
        addDataSlots(data);
    }

    public int getCost(int i) { return data.get(i); }
    public int getGemIndex(int i) { return data.get(3 + i); }
    public int getGemLevel(int i) { return data.get(6 + i); }

    @Override
    public void slotsChanged(Container container) {
        if (container != toolSlot) return;
        access.execute((level, pos) -> {
            updateOffers(level, pos);
            broadcastChanges();
        });
    }

    private void updateOffers(Level level, BlockPos pos) {
        for (int i = 0; i < 3; i++) {
            data.set(i, 0);
            data.set(3 + i, -1);
            data.set(6 + i, 0);
        }
        ItemStack tool = toolSlot.getItem();
        if (tool.isEmpty() || tool.is(Items.BOOK) || tool.getItem().getEnchantmentValue(tool) <= 0 || tool.getMaxStackSize() != 1) return;
        ItemEnchantments existing = tool.getOrDefault(DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY);
        if (existing.size() >= MAX_GEMS) return;

        // gem shelves (bookshelves) around the altar, same pattern and cap as the vanilla table
        int power = 0;
        for (BlockPos off : EnchantingTableBlock.BOOKSHELF_OFFSETS) {
            if (EnchantingTableBlock.isValidBookShelf(level, pos, off)) power++;
        }
        power = Math.min(power, 15);

        random.setSeed(owner.getEnchantmentSeed());
        Registry<Enchantment> lookup = level.registryAccess().registryOrThrow(Registries.ENCHANTMENT);
        Set<Integer> used = new HashSet<>();

        for (int slot = 0; slot < 3; slot++) {
            int base = random.nextInt(8) + 1 + (power >> 1) + random.nextInt(power + 1);
            int cost = switch (slot) {
                case 0 -> Math.max(base / 3, 1);
                case 1 -> base * 2 / 3 + 1;
                default -> Math.max(base, power * 2);
            };
            if (cost < slot + 1) continue;
            // rare gems (Mending, Soul Speed...) only show up in the top slot with enough shelves
            boolean allowRare = slot == 2 && power >= 8 && random.nextInt(4) == 0;

            List<int[]> options = new ArrayList<>();
            for (int gi = 0; gi < Gems.ALL.size(); gi++) {
                Gems.Gem gem = Gems.ALL.get(gi);
                if (gem.curse() || used.contains(gi)) continue;
                if (gem.treasure() && !allowRare) continue;
                Optional<Holder.Reference<Enchantment>> opt = lookup.getHolder(Gems.key(gem));
                if (opt.isEmpty()) continue;
                Holder<Enchantment> holder = opt.get();
                Enchantment ench = holder.value();
                if (!tool.supportsEnchantment(holder) || existing.keySet().contains(holder)) continue;
                boolean compatible = true;
                for (Holder<Enchantment> other : existing.keySet()) {
                    if (!Enchantment.areCompatible(holder, other)) { compatible = false; break; }
                }
                if (!compatible) continue;
                for (int lvl = ench.getMaxLevel(); lvl >= 1; lvl--) {
                    if (cost >= ench.getMinCost(lvl) && cost <= ench.getMaxCost(lvl)) {
                        options.add(new int[] {gi, lvl});
                        break;
                    }
                }
            }
            if (options.isEmpty()) continue;
            int[] pick = options.get(random.nextInt(options.size()));
            used.add(pick[0]);
            data.set(slot, cost);
            data.set(3 + slot, pick[0]);
            data.set(6 + slot, pick[1]);
        }
    }

    @Override
    public boolean clickMenuButton(Player player, int id) {
        if (id < 0 || id >= 3) return false;
        ItemStack tool = toolSlot.getItem();
        int cost = data.get(id), gemIndex = data.get(3 + id), gemLevel = data.get(6 + id);
        if (tool.isEmpty() || cost <= 0 || gemIndex < 0) return false;
        boolean creative = player.getAbilities().instabuild;
        if (!creative && player.experienceLevel < cost) return false;

        access.execute((level, pos) -> {
            Gems.Gem gem = Gems.ALL.get(gemIndex);
            Optional<Holder.Reference<Enchantment>> opt = level.registryAccess()
                    .registryOrThrow(Registries.ENCHANTMENT).getHolder(Gems.key(gem));
            if (opt.isEmpty()) return;
            Holder<Enchantment> holder = opt.get();
            tool.enchant(holder, gemLevel);
            player.onEnchantmentPerformed(tool, creative ? 0 : id + 1);
            toolSlot.setChanged();
            level.playSound(null, pos, SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.BLOCKS,
                    1.0F, level.random.nextFloat() * 0.1F + 0.9F);
        });
        return true;
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        access.execute((level, pos) -> clearContainer(player, toolSlot));
    }

    @Override
    public boolean stillValid(Player player) {
        return stillValid(access, player, ModBlocks.GEM_ALTAR.get());
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        ItemStack result = ItemStack.EMPTY;
        Slot slot = slots.get(index);
        if (slot != null && slot.hasItem()) {
            ItemStack stack = slot.getItem();
            result = stack.copy();
            if (index == 0) {
                if (!moveItemStackTo(stack, 1, 37, true)) return ItemStack.EMPTY;
            } else {
                if (slots.get(0).hasItem()) return ItemStack.EMPTY;
                slots.get(0).setByPlayer(stack.copyWithCount(1));
                stack.shrink(1);
            }
            if (stack.isEmpty()) slot.setByPlayer(ItemStack.EMPTY); else slot.setChanged();
            if (stack.getCount() == result.getCount()) return ItemStack.EMPTY;
            slot.onTake(player, stack);
        }
        return result;
    }
}
''')

w(J + "GemAltarScreen.java", '''package com.gemghoul;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

public class GemAltarScreen extends AbstractContainerScreen<GemAltarMenu> {
    private static final ResourceLocation TEXTURE =
            ResourceLocation.fromNamespaceAndPath(GemGhoulMod.MODID, "textures/gui/gem_altar.png");

    public GemAltarScreen(GemAltarMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
    }

    private boolean affordable(int cost) {
        return minecraft.player.getAbilities().instabuild || minecraft.player.experienceLevel >= cost;
    }

    private boolean overBar(int i, double mx, double my) {
        int x = leftPos + 60, y = topPos + 14 + 19 * i;
        return mx >= x && mx < x + 108 && my >= y && my < y + 19;
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        g.blit(TEXTURE, leftPos, topPos, 0, 0, imageWidth, imageHeight);
        for (int i = 0; i < 3; i++) {
            int x = leftPos + 60, y = topPos + 14 + 19 * i;
            int cost = menu.getCost(i), gi = menu.getGemIndex(i);
            if (cost <= 0 || gi < 0) {
                g.fill(x + 1, y + 1, x + 107, y + 18, 0x90000000);
                continue;
            }
            Gems.Gem gem = Gems.ALL.get(gi);
            boolean ok = affordable(cost);
            if (overBar(i, mouseX, mouseY) && ok) g.fill(x + 1, y + 1, x + 107, y + 18, 0x40FFFFFF);
            if (!ok) g.fill(x + 1, y + 1, x + 107, y + 18, 0x70000000);

            g.renderItem(new ItemStack(Gems.itemOf(gem)), x + 2, y + 1);

            g.pose().pushPose();
            g.pose().translate(x + 21, y + 3, 0);
            g.pose().scale(0.8F, 0.8F, 1.0F);
            g.drawString(font, Gems.name(gem), 0, 0, ok ? gem.displayColor() : 0x808080, true);
            g.pose().popPose();

            g.pose().pushPose();
            g.pose().translate(x + 21, y + 11, 0);
            g.pose().scale(0.7F, 0.7F, 1.0F);
            g.drawString(font, Component.translatable("gemghoul.level", menu.getGemLevel(i)), 0, 0, 0xA0A0A0, true);
            g.pose().popPose();

            String c = Integer.toString(cost);
            g.drawString(font, c, x + 104 - font.width(c), y + 6, ok ? 0x80FF20 : 0xFC5454, true);
        }
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        renderTooltip(g, mouseX, mouseY);
        for (int i = 0; i < 3; i++) {
            int cost = menu.getCost(i), gi = menu.getGemIndex(i);
            if (cost <= 0 || gi < 0 || !overBar(i, mouseX, mouseY)) continue;
            Gems.Gem gem = Gems.ALL.get(gi);
            List<Component> tip = new ArrayList<>();
            // name on top, what it does below
            tip.add(Gems.coloredName(gem).append(" ").append(Component.translatable("enchantment.level." + menu.getGemLevel(i))));
            tip.add(Gems.desc(gem).withStyle(ChatFormatting.GRAY));
            tip.add(Component.translatable("gemghoul.cost", cost)
                    .withStyle(affordable(cost) ? ChatFormatting.GREEN : ChatFormatting.RED));
            g.renderComponentTooltip(font, tip, mouseX, mouseY);
        }
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == 0) {
            for (int i = 0; i < 3; i++) {
                if (overBar(i, mouseX, mouseY) && menu.clickMenuButton(minecraft.player, i)) {
                    minecraft.gameMode.handleInventoryButtonClick(menu.containerId, i);
                    return true;
                }
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }
}
''')

w(J + "ClientEvents.java", '''package com.gemghoul;

import net.minecraft.ChatFormatting;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterMenuScreensEvent;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;

public class ClientEvents {
    @EventBusSubscriber(modid = GemGhoulMod.MODID, bus = EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static class ModBus {
        @SubscribeEvent
        public static void registerScreens(RegisterMenuScreensEvent event) {
            event.register(ModMenus.GEM_ALTAR.get(), GemAltarScreen::new);
        }
    }

    /** Vanilla gems (Diamond, Emerald, Lapis Lazuli, Amethyst Shard) also show what their gem does. */
    @EventBusSubscriber(modid = GemGhoulMod.MODID, value = Dist.CLIENT)
    public static class GameBus {
        @SubscribeEvent
        public static void onTooltip(ItemTooltipEvent event) {
            Gems.Gem gem = Gems.byVanillaItem(event.getItemStack().getItem());
            if (gem != null) {
                event.getToolTip().add(Gems.desc(gem).withStyle(ChatFormatting.GRAY));
            }
        }
    }
}
''')

w("README.txt", '''Gem Ghoul - NeoForge 1.21.1 mod (JDK 21 required)

BUILD
1. Download the official NeoForge 1.21.1 MDK (neoforged.net -> Downloads -> MDKs, "1.21.1").
2. In the MDK: delete src/main/java/com/example, and delete src/main/templates/META-INF/neoforge.mods.toml.
3. Copy this project's src/ folder over the MDK's src/ (merge).
4. In the MDK gradle.properties set:
     mod_id=gemghoul
     mod_name=Gem Ghoul
     mod_version=1.0.0
     mod_group_id=com.gemghoul
5. Run:  gradlew build     (output: build/libs/gemghoul-1.0.0.jar)
6. Put the jar in your .minecraft/versions/<your version>/mods folder.
   (Test with a 1.21.1 NeoForge instance.)

Regenerating: gen.py rebuilds everything from gem-enchantments-table.html.
''')

shutil.copy("/home/claude/gen.py", os.path.join(ROOT, "gen.py"))
print("done")
