package com.gemghoul;

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
