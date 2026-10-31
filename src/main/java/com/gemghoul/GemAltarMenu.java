package com.gemghoul;

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
        ItemStack tool = toolSlot.getItem(0);
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
        ItemStack tool = toolSlot.getItem(0);
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
