package com.gemghoul;

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
