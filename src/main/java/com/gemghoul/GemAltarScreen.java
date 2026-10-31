package com.gemghoul;

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
