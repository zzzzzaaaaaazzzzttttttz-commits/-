package com.gemghoul;

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
