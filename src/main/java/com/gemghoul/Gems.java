package com.gemghoul;

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
        new Gem("diamond", "protection", 0xBFE8F5, "diamond", false, false),
        new Gem("ruby", "fire_protection", 0xD4142F, null, false, false),
        new Gem("carnelian", "blast_protection", 0xC2491F, null, false, false),
        new Gem("hematite", "projectile_protection", 0x6A6E78, null, false, false),
        new Gem("tourmaline", "thorns", 0x1F8A5B, null, false, false),
        new Gem("sapphire", "unbreaking", 0x1B45B8, null, false, false),
        new Gem("emerald", "mending", 0x1FAE5E, "emerald", true, false),
        new Gem("amber", "binding_curse", 0xE0901A, null, false, true),
        new Gem("moonstone", "vanishing_curse", 0xC9D3EA, null, false, true),
        new Gem("aquamarine", "respiration", 0x6FD3D6, null, false, false),
        new Gem("blue_chalcedony", "aqua_affinity", 0x8FB8E0, null, false, false),
        new Gem("smoky_quartz", "swift_sneak", 0x6B5A4C, null, true, false),
        new Gem("opal", "feather_falling", 0xD8E6EF, null, false, false),
        new Gem("turquoise", "depth_strider", 0x2BC0B4, null, false, false),
        new Gem("selenite", "frost_walker", 0xEEF4F7, null, true, false),
        new Gem("amethyst", "soul_speed", 0x8E4FD0, "amethyst_shard", true, false),
        new Gem("moissanite", "sharpness", 0xE4F0FF, null, false, false),
        new Gem("peridot", "smite", 0x9BC92B, null, false, false),
        new Gem("tigers_eye", "bane_of_arthropods", 0xB0731F, null, false, false),
        new Gem("lapis_lazuli", "knockback", 0x26429B, "lapis_lazuli", false, false),
        new Gem("fire_opal", "fire_aspect", 0xFF6A1A, null, false, false),
        new Gem("golden_beryl", "looting", 0xE8C33A, null, false, false),
        new Gem("kyanite", "sweeping_edge", 0x3B78D6, null, false, false),
        new Gem("topaz", "efficiency", 0xF0A53A, null, false, false),
        new Gem("rose_quartz", "silk_touch", 0xF3B6C8, null, false, false),
        new Gem("citrine", "fortune", 0xF2B81C, null, false, false),
        new Gem("red_spinel", "power", 0xC01A3C, null, false, false),
        new Gem("garnet", "punch", 0x8C1026, null, false, false),
        new Gem("sunstone", "flame", 0xF08A2C, null, false, false),
        new Gem("alexandrite", "infinity", 0x2E8F86, null, false, false),
        new Gem("labradorite", "multishot", 0x3F7FA0, null, false, false),
        new Gem("tanzanite", "piercing", 0x4A4FC4, null, false, false),
        new Gem("zircon", "quick_charge", 0x5EC0E8, null, false, false),
        new Gem("pearl", "loyalty", 0xF1EBE3, null, false, false),
        new Gem("onyx", "impaling", 0x25232B, null, false, false),
        new Gem("larimar", "riptide", 0x4FB6D9, null, false, false),
        new Gem("charoite", "channeling", 0x7B3FA8, null, false, false),
        new Gem("jasper", "density", 0xA8472D, null, false, false),
        new Gem("bloodstone", "breach", 0x2F5A40, null, false, false),
        new Gem("celestite", "wind_burst", 0xA9CDF0, null, true, false),
        new Gem("jade", "luck_of_the_sea", 0x4FAE7A, null, false, false),
        new Gem("rhodochrosite", "lure", 0xE0728F, null, false, false)
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
