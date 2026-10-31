package com.gemghoul;

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
