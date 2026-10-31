package com.gemghoul;

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
