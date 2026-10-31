package com.gemghoul;

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
