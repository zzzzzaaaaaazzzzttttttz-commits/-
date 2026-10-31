package com.gemghoul;

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
