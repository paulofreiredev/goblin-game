"""Integration requires a graphics context: RUN_GRAPHICS_TESTS=1 python -m pytest."""
import os
import pytest

pytestmark = pytest.mark.skipif(os.environ.get('RUN_GRAPHICS_TESTS') != '1', reason='Requer contexto gráfico; habilite RUN_GRAPHICS_TESTS=1')


def test_menu_game_options_and_resume(tmp_path):
    from panda3d.core import AudioSound, ClockObject, loadPrcFileData
    loadPrcFileData('', 'audio-library-name null')
    from direct.gui.DirectGui import DirectButton
    from game.app import Game, ROOT
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        assert game.mode == 'menu'
        assert game.storage.load_player() is None
        assert game.menu_coins_label['text'] == '0'
        assert game.menu_coin_icon['image_scale'] == 0.075
        assert any(widget['text'] == 'Continuar' and widget['state'] == 'disabled'
                   for widget in game.ui if isinstance(widget, DirectButton))
        import wave
        with wave.open(str(ROOT / "assets/sound/theme.wav")) as theme:
            assert theme.getnframes() > 0
        assert game.music is not None
        game.new_game()
        assert game.mode == 'playing'
        assert len(game.heart_icons) == 5
        assert game.coins_display.value == '0'
        assert game.timer_display.value == '02:00'
        hud = game.heart_icons[0].getParent()
        hud_widget = next(widget for widget in game.ui if widget == hud)
        assert hud_widget['frameColor'] == (0, 0, 0, 0)
        assert all(icon.getZ() == game.hud_coin_icon.getZ() for icon in game.heart_icons)
        assert game.coins_display.getZ() == game.timer_display.getZ() == game.hud_coin_icon.getZ()
        assert game.coins_display.getX() > game.hud_coin_icon.getX()
        assert game.timer_display.getX() > game.coins_display.getX() + game.coins_display.width
        assert game.timer_display.height == 0.14

        assert game.minimap.getParent() == game.a2dTopRight
        assert game.heart_icons[0].getParent().getParent() == game.a2dTopLeft
        assert game.minimap_texture.getXSize() == 192
        assert len(game.heart_nodes) == 2
        lower, upper = game.coin_nodes[0].getTightBounds()
        assert upper.z - lower.z == pytest.approx(0.9, abs=1e-5)
        assert upper.y - lower.y == pytest.approx(0.16)
        lower, upper = game.terrain.getTightBounds()
        assert lower.z < -2 and upper.z > 2
        from game.world import terrain_height
        game.player.x, game.player.y = 50, 0
        game.update_character()
        assert game.actor.getZ() == pytest.approx(terrain_height(50, 0))
        game.player.x = game.player.y = 0
        game.update_character()
        assert game.hud_coin_icon['image_scale'] == game.heart_icons[0]['image_scale']
        assert all(not node.isHidden() for node in game.heart_nodes)
        heart = game.encounter.hearts[0]
        game.player.x, game.player.y, game.player.health = heart.x, heart.y, 3
        game.encounter.update(game.player, 0)
        game.update_coins()
        assert game.player.health == 4
        assert game.heart_nodes[0].isHidden()
        assert not game.heart_nodes[1].isHidden()
        game.player.x = game.player.y = 0
        from panda3d.core import PNMImage
        enemy = game.encounter.enemies[0]
        original_position = enemy.x, enemy.y
        enemy.x, enemy.y = 70, 70
        game.update_minimap()
        map_image = PNMImage()
        assert game.minimap_texture.store(map_image)
        assert map_image.getXel(140, 52).x > 0.9
        enemy.health = 0
        game.update_minimap()
        assert game.minimap_texture.store(map_image)
        assert map_image.getXel(140, 52).x < 0.2
        enemy.x, enemy.y = original_position
        enemy.health = 2
        game.player.health = 3
        game.update_hud()
        assert game.heart_icons[0].getColorScale().x > 0.9
        assert game.heart_icons[3].getColorScale().x < 0.3
        game.player.health = 5
        from panda3d.core import WindowProperties
        class UnfocusedWindow:
            def getProperties(self):
                properties = WindowProperties()
                properties.setForeground(False)
                return properties
        game.set_key('w', True)
        game.window_event(UnfocusedWindow())
        assert game.mode == 'playing'  # Screenshot tools may briefly steal focus.
        assert not game.keys
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MNonRealTime)
        clock.setDt(1 / 60)
        game.set_key('w', True)
        game.set_key('shift', True)
        for _ in range(30):
            game.taskMgr.step()
        assert game.player.y > 0
        assert game.player.animation == 'run'
        assert game.sprite.getTexture() == game.textures[2, game.player.frame]
        y = game.player.y
        game.escape()
        assert game.mode == 'menu'
        saved_time = game.player.time_remaining
        game.taskMgr.step()
        assert game.player.y == y
        assert game.player.time_remaining == saved_time
        game.options()
        game.toggle_sound()
        assert not game.sound_enabled
        assert game.music.status() != AudioSound.PLAYING
        assert game.storage.read('settings.json') == {'sound': False, 'jump_key': 'space', 'attack_key': 'x'}
        game.toggle_sound()
        assert game.sound_enabled
        game.main_menu()
        game.continue_game()
        assert game.player.y == y
        assert game.player.time_remaining == saved_time
        assert game.encounter.hearts[0].collected
        assert game.heart_nodes[0].isHidden()
        game.new_game()
        assert game.player.y == 0
        assert game.world.findAllMatches("**/water-top-pond").getNumPaths() == 0
        assert len(game.enemy_nodes) == 8
        assert game.enemy_nodes[0].hasTexture()
        lower, upper = game.enemy_nodes[0].getTightBounds()
        assert upper.z - lower.z == pytest.approx(1.45, abs=0.01)
        # Actual Panda event bindings must trigger actions only during play.
        game.messenger.send('space')
        game.taskMgr.step()
        assert game.player.z > 0
        game.messenger.send('space')
        for _ in range(65):
            game.taskMgr.step()
        assert game.player.z == 0
        enemy = game.encounter.enemies[0]
        enemy.x, enemy.y = game.player.x, game.player.y + 2
        game.player.direction = 2
        game.messenger.send('x')
        assert enemy.health == 1
        game.messenger.send('x')
        assert enemy.health == 1  # Cooldown prevents a second immediate hit.
        game.taskMgr.step()
        assert game.sprite.getTexture() == game.textures[2, game.player.frame]
        for _ in range(38):
            game.taskMgr.step()
        game.messenger.send('x')
        assert enemy.health == 0
        assert game.player.coins == 0
        assert game.coins_display.value == '0'
        assert not game.coin_nodes[0].isHidden()
        assert game.coin_nodes[1].isHidden()
        old_angle = game.coin_nodes[0].getH()
        game.player.y = enemy.y - 3
        game.taskMgr.step()
        assert game.coin_nodes[0].getH() != old_angle
        game.player.x, game.player.y = enemy.x, enemy.y
        game.taskMgr.step()
        assert game.player.coins == 1
        assert game.coins_display.value == '1'
        assert game.coin_nodes[0].isHidden()
        assert game.enemy_nodes[0].isHidden()
        game.main_menu()
        assert game.menu_coins_label['text'] == '1'
        game.messenger.send('space')
        game.messenger.send('x')
        assert game.player.vertical_speed == 0
        game.continue_game()
        assert game.encounter.enemies[0].health == 0
        assert game.player.coins == 1
        game.new_game()
        assert game.encounter.enemies[0].health == 2
        assert game.player.coins == 0
        # Former pools allow normal movement; trees still block their footprint.
        game.keys.clear()
        game.player.x, game.player.y = 9, 7
        game.set_key('d', True)
        old_x = game.player.x
        game.taskMgr.step()
        assert game.player.x - old_x == pytest.approx(6 / 60)
        game.keys.clear()
        from game.world import TREE_OBSTACLES, PLAYER_RADIUS
        trunk_x, trunk_y, trunk_radius = TREE_OBSTACLES[0]
        game.player.x, game.player.y = trunk_x - 2, trunk_y
        game.set_key('d', True)
        for _ in range(30):
            game.taskMgr.step()
        assert game.player.x <= trunk_x - trunk_radius - PLAYER_RADIUS
        game.graphicsEngine.renderFrame()
        assert game.win.saveScreenshot(str(tmp_path / 'game.png'))
        # Expired matches stop input and stay expired when resumed.
        game.player.time_remaining = 0.01
        game.taskMgr.step()
        assert game.mode == 'defeat'
        game.messenger.send('x')
        game.messenger.send('space')
        assert game.player.time_remaining == 0
        game.main_menu()
        game.continue_game()
        assert game.mode == 'defeat'
        game.new_game()
        assert game.player.time_remaining == 120
        # The final kill in the night phase ends the campaign.
        game.player.phase = 2
        game.apply_phase()
        for enemy in game.encounter.enemies:
            enemy.health = 0
        enemy = game.encounter.enemies[0]
        enemy.health, enemy.x, enemy.y = 1, 0, 2
        game.player.direction = 2
        game.messenger.send('x')
        assert game.mode == 'victory'
        assert game.storage.load_player().coins == 0
        frozen_time = game.player.time_remaining
        game.player.x, game.player.y = enemy.x, enemy.y
        game.taskMgr.step()
        assert game.player.time_remaining == frozen_time
        assert game.player.coins == 1
        game.main_menu()
        game.continue_game()
        assert game.mode == 'victory'
        # Losing the last heart resets the complete match and saves that reset.
        game.new_game()
        game.player.health, game.player.coins, game.player.time_remaining = 1, 3, 25
        game.encounter.enemies[1].health = 0
        game.encounter.hearts[0].collected = True
        enemy = game.encounter.enemies[0]
        enemy.x, enemy.y = game.player.x, game.player.y
        game.taskMgr.step()
        assert game.mode == 'playing'
        assert game.player.health == 5 and game.player.coins == 0
        assert game.player.time_remaining == 120
        assert (game.player.x, game.player.y) == (0, 0)
        assert game.encounter.defeated == 0
        assert all(enemy.health == 2 for enemy in game.encounter.enemies)
        assert all(not heart.collected for heart in game.encounter.hearts)
        assert game.storage.load_player().time_remaining == 120
        assert all(node.isHidden() for node in game.coin_nodes)
        # A fatal fall also restarts the match after a visible airborne phase.
        from game.world import move_on_terrain
        previous_encounter = game.encounter
        game.player.health = 1
        game.player.x, game.player.y = -5, 0
        move_on_terrain(game.player, -20, 0)
        game.update_character()
        initial_foot_height = game.actor.getZ() + game.sprite.getZ()
        game.taskMgr.step()
        assert 0 < game.actor.getZ() + game.sprite.getZ() < initial_foot_height
        assert game.player.health == 1
        for _ in range(60):
            game.taskMgr.step()
            if game.encounter is not previous_encounter:
                break
        assert game.encounter is not previous_encounter
        assert game.player.health == 5 and game.player.time_remaining == 120
        assert game.encounter.defeated == 0
        game.new_game()
        clock.setDt(2)
        game.taskMgr.step()
        assert game.player.time_remaining == pytest.approx(118)
        clock.setDt(1 / 60)
        game.options()
        game.begin_binding('jump')
        game.messenger.send('control-key', ['w'])
        assert game.jump_key == 'space' and game.binding_action == 'jump'
        game.messenger.send('control-key', ['x'])
        assert game.jump_key == 'space'
        game.messenger.send('control-key', ['e'])
        assert game.jump_key == 'e' and game.binding_action is None
        game.begin_binding('attack')
        game.messenger.send('control-key', ['q'])
        assert game.attack_key == 'q'
        game.toggle_sound()
        saved_settings = game.storage.read('settings.json')
        assert saved_settings['jump_key'] == 'e' and saved_settings['attack_key'] == 'q'
        game.begin_binding('jump')
        game.messenger.send('escape')
        assert game.binding_action is None and game.mode == 'options'
        game.main_menu()
        game.new_game()
        enemy = game.encounter.enemies[0]
        enemy.x, enemy.y = 0, 2
        game.player.direction = 2
        game.messenger.send('space')
        game.messenger.send('x')
        assert game.player.vertical_speed == 0 and enemy.health == 2
        game.messenger.send('q')
        assert enemy.health == 1
        game.messenger.send('e')
        assert game.player.vertical_speed > 0
    finally:
        game.destroy()


def test_clock_rendering_collection_resume_and_reset(tmp_path):
    from panda3d.core import ClockObject, loadPrcFileData
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        game.new_game()
        timer = ClockObject.getGlobalClock()
        timer.setMode(ClockObject.MNonRealTime)
        timer.setDt(1 / 60)
        assert len(game.clock_nodes) == 3
        for node in game.clock_nodes:
            assert not node.isHidden()
            lower, upper = node.getTightBounds()
            assert upper.x - lower.x == pytest.approx(0.9, abs=1e-5)
            assert upper.y - lower.y > 0.16
            assert upper.z - lower.z == pytest.approx(0.9, abs=1e-5)
            assert len([child for child in node.getChildren() if child.hasTexture()]) == 2
        node = game.clock_nodes[0]
        angle = node.getH()
        game.taskMgr.step()
        assert node.getH() != angle
        pickup = game.encounter.clocks[0]
        game.player.x, game.player.y = pickup.x, pickup.y
        before = game.player.time_remaining
        game.taskMgr.step()
        assert game.player.time_remaining == pytest.approx(before + 30 - 1 / 60)
        assert node.isHidden()
        assert game.timer_display.value == '02:30'
        game.main_menu()
        game.continue_game()
        assert game.encounter.clocks[0].collected
        assert game.clock_nodes[0].isHidden()
        assert game.player.time_remaining > 120
        game.new_game()
        assert game.player.time_remaining == 120
        assert all(not clock.collected for clock in game.encounter.clocks)
        assert all(not node.isHidden() for node in game.clock_nodes)
        game.graphicsEngine.renderFrame()
    finally:
        game.destroy()


def test_three_phase_campaign(tmp_path):
    count = 8
    from panda3d.core import loadPrcFileData
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        game.new_game()
        game.player.coins, game.player.health = 4, 3
        colors = []
        for phase in range(3):
            assert game.player.phase == phase
            assert game.mode == 'playing'
            assert len(game.encounter.enemies) == len(game.enemy_nodes) == len(game.coin_nodes) == count
            assert len(game.enemy_bars) == count
            assert game.player.health == 3 and game.player.coins == 4
            assert game.moon.isHidden() == (phase != 2)
            colors.append(tuple(game.world.getColorScale()))
            game.main_menu()
            game.continue_game()
            assert game.player.phase == phase
            assert len(game.encounter.enemies) == count
            assert not any(clock.collected for clock in game.encounter.clocks)
            for enemy in game.encounter.enemies:
                enemy.health = 0
            game.encounter.clocks[0].collected = True
            game.player.time_remaining = 15
            game.finish_match('victory')
            if phase < 2:
                assert game.player.time_remaining == 120
                assert game.encounter.defeated == 0
                assert (game.player.x, game.player.y) == (0, 0)
        assert len(set(colors)) == 3
        assert game.mode == 'victory' and game.player.phase == 2
        game.main_menu()
        game.continue_game()
        assert game.mode == 'victory'
    finally:
        game.destroy()
