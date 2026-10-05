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
        assert game.sprite.getTexture() == game.textures[game.sprite_direction, game.player.frame]
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
        assert game.storage.read('settings.json') == {'sound': False, 'jump_key': 'space', 'attack_key': 'x', 'difficulty': 'medium', 'gamepad_bindings': game.gamepad_bindings, 'local_controls': game.local_controls}
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
        assert game.sprite.getTexture() == game.textures[game.sprite_direction, game.player.frame]
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
        assert ((game.player.x - old_x) ** 2 + (game.player.y - 7) ** 2) ** 0.5 == pytest.approx(6 / 60)
        game.keys.clear()
        from game.world import TREE_OBSTACLES, PLAYER_RADIUS
        game.camera_mode = 'first_person'
        game.fps_heading = 0
        trunk_x, trunk_y, trunk_radius = TREE_OBSTACLES[0]
        game.player.x, game.player.y = trunk_x - 2, trunk_y
        game.set_key('d', True)
        for _ in range(30):
            game.taskMgr.step()
        assert game.player.x <= trunk_x - trunk_radius - PLAYER_RADIUS
        game.camera_mode = 'third_person'
        game.update_camera(snap=True)
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


@pytest.mark.parametrize('difficulty,count', [('easy', 3), ('medium', 8), ('hard', 12)])
def test_three_phase_campaign_and_saved_difficulty(tmp_path, difficulty, count):
    from panda3d.core import loadPrcFileData
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        game.difficulty = difficulty
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
            game.difficulty = 'easy' if difficulty != 'easy' else 'hard'
            game.continue_game()
            assert game.player.phase == phase and game.player.difficulty == difficulty
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
        game.options()
        game.cycle_difficulty()
        assert game.storage.read('settings.json')['difficulty'] == game.difficulty
        game.new_game()
        assert game.player.phase == 0
        assert game.player.difficulty == game.difficulty
    finally:
        game.destroy()


def test_fps_toggle_movement_attack_jump_and_menu(tmp_path):
    from panda3d.core import ClockObject, loadPrcFileData
    from game.world import player_ground_height
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        game.messenger.send('f')
        assert game.camera_mode == 'third_person'
        game.new_game()
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MNonRealTime)
        clock.setDt(1 / 60)
        game.messenger.send('f')
        assert game.camera_mode == 'first_person' and game.sprite.isHidden()
        assert game.shadow.isHidden() and not game.crosshair.isHidden()
        assert game.camera.getZ() == pytest.approx(player_ground_height(0, 0) + 2)
        game.turn_fps_view(600, 0)
        game.set_key('w', True)
        game.taskMgr.step()
        assert game.player.x == pytest.approx(6 / 60)
        assert game.player.y == pytest.approx(0, abs=1e-6)
        assert game.player.direction == 4
        game.keys.clear()
        enemy = game.encounter.enemies[0]
        enemy.x, enemy.y = game.player.x + 2, game.player.y
        game.messenger.send('x')
        assert enemy.health == 1
        game.messenger.send('space')
        game.taskMgr.step()
        assert game.camera.getZ() == pytest.approx(player_ground_height(game.player.x, game.player.y) + game.player.z + 2)
        game.turn_fps_view(0, -10000)
        assert game.fps_pitch == 75
        game.escape()
        assert not game.mouse_captured and game.mode == 'menu'
        game.messenger.send('f')
        assert game.camera_mode == 'first_person'
        game.continue_game()
        for _ in range(24):
            game.taskMgr.step()
        game.messenger.send('f')
        assert game.camera_mode == 'third_person'
        assert not game.sprite.isHidden() and game.crosshair.isHidden()
        assert (game.camera.getPos() - game.actor.getPos()).length() > 8
    finally:
        game.destroy()


def test_controller_options_mapping_gameplay_and_disconnect(tmp_path):
    from panda3d.core import ClockObject, loadPrcFileData
    from direct.gui.DirectGui import DirectButton, DirectLabel
    from tests.test_gamepad import fake_gamepad
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        game.options()
        assert any(isinstance(item, DirectButton) and item['text'] == 'Controle USB' for item in game.ui)
        game.controller_options()
        assert game.mode == 'controller_options'
        assert any('Nenhum controle' in item['text'] for item in game.ui if isinstance(item, DirectLabel))
        device = fake_gamepad()
        game.gamepad_device = device
        game.gamepad_scan_time = 1000
        game.controller_options(scan=False)
        game.begin_gamepad_binding('run')
        device.buttons[3].pressed = True
        game.poll_gamepad(0)
        assert game.gamepad_bindings['run'] == 'button:3'
        assert game.storage.read('settings.json')['gamepad_bindings']['run'] == 'button:3'
        device.buttons[3].pressed = False
        game.begin_gamepad_binding('attack')
        device.buttons[0].pressed = True
        game.poll_gamepad(0)
        assert game.pending_gamepad_action is None
        assert game.gamepad_bindings['attack'] == 'button:0'
        assert game.gamepad_bindings['jump'] == 'button:1'
        assert game.storage.read('settings.json')['gamepad_bindings'] == game.gamepad_bindings
        device.buttons[0].pressed = False
        game.poll_gamepad(0)
        game.begin_gamepad_binding('attack')
        device.buttons[6].pressed = True
        game.poll_gamepad(0)
        assert game.gamepad_bindings['attack'] == 'button:6'
        device.buttons[6].pressed = False
        game.begin_gamepad_binding('jump')
        device.buttons[0].pressed = True
        game.poll_gamepad(0)
        assert game.gamepad_bindings['jump'] == 'button:0'
        device.buttons[0].pressed = False
        game.begin_gamepad_binding('jump')
        game.escape()
        assert game.pending_gamepad_action is None and game.mode == 'controller_options'
        game.escape()
        assert game.mode == 'options'
        game.new_game()
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MNonRealTime)
        clock.setDt(1 / 60)
        device.axes[1].value = 1
        device.buttons[3].pressed = True
        game.taskMgr.step()
        assert game.player.y == pytest.approx(12 / 60)
        device.axes[1].value = 0
        device.buttons[3].pressed = False
        device.buttons[0].pressed = True
        game.taskMgr.step()
        assert game.player.z > 0
        device.buttons[0].pressed = False
        game.new_game()
        enemy = game.encounter.enemies[0]
        enemy.x, enemy.y = 0, 2
        game.player.direction = 2
        device.buttons[6].pressed = True
        game.taskMgr.step()
        assert enemy.health == 1
        for _ in range(65):
            enemy.x, enemy.y = 0, 2
            game.taskMgr.step()
        assert enemy.health == 1
        device.connected = False
        old_position = game.player.x, game.player.y
        game.taskMgr.step()
        assert (game.player.x, game.player.y) == old_position
        assert not any(game.gamepad_previous.values())
        game.messenger.send('f')
        device.connected = True
        device.buttons[6].pressed = False
        device.axes[0].value = 1
        heading = game.fps_heading
        game.taskMgr.step()
        assert game.fps_heading == heading
        assert (game.player.x, game.player.y) != old_position
    finally:
        game.destroy()


def test_usb_four_directions_follow_view_in_both_camera_modes(tmp_path):
    from panda3d.core import ClockObject, loadPrcFileData
    from tests.test_gamepad import fake_gamepad
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        device = fake_gamepad()
        game.gamepad_device, game.gamepad_scan_time = device, 1000
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MNonRealTime)
        clock.setDt(1 / 60)
        for mode in ['third_person', 'first_person']:
            for axes, expected in [((0, 1), (0.1, 0)), ((0, -1), (-0.1, 0)),
                                   ((1, 0), (0, -0.1)), ((-1, 0), (0, 0.1))]:
                game.new_game()
                game.camera_mode = mode
                game.follow_heading = game.fps_heading = 90
                game.player.x = game.player.y = 70
                game.update_camera(snap=True)
                for axis, value in zip(device.axes, axes):
                    axis.value = value
                game.taskMgr.step()
                assert (game.player.x - 70, game.player.y - 70) == pytest.approx(expected, abs=1e-5)
    finally:
        game.destroy()


def test_usb_start_menu_navigation_confirmation_and_camera_delay(tmp_path):
    from panda3d.core import ClockObject, loadPrcFileData
    from tests.test_gamepad import fake_gamepad
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        device = fake_gamepad()
        game.gamepad_device, game.gamepad_scan_time = device, 1000
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MNonRealTime)
        clock.setDt(1 / 60)
        game.new_game()
        game.messenger.send('f')
        game.messenger.send('f')
        assert game.camera_mode == 'first_person'
        for _ in range(23):
            game.taskMgr.step()
        game.messenger.send('f')
        assert game.camera_mode == 'third_person'
        device.buttons[7].pressed = True
        game.taskMgr.step()
        assert game.mode == 'menu'
        assert game.menu_focus['text'] == 'Novo jogo'
        device.buttons[7].pressed = False
        device.axes[1].value = -1
        game.taskMgr.step()
        assert game.menu_focus['text'] == 'Continuar'
        device.axes[1].value = 0
        device.buttons[0].pressed = True
        game.taskMgr.step()
        assert game.mode == 'playing'
    finally:
        game.destroy()


def test_two_players_controls_pause_resume_and_solo_save(tmp_path):
    from panda3d.core import ClockObject, loadPrcFileData
    from direct.gui.DirectGui import DirectButton
    from tests.test_gamepad import fake_gamepad
    loadPrcFileData('', 'audio-library-name null')
    from game.app import Game
    game = Game(offscreen=True, storage_directory=tmp_path)
    try:
        assert any(isinstance(item, DirectButton) and item['text'] == 'Dois jogadores' for item in game.ui)
        game.new_game()
        game.player.coins = 9
        game.main_menu()
        saved = game.storage.read('save.json')
        game.two_player_menu()
        game.new_capture()
        assert game.mode == 'capture'
        assert len(game.capture_match.players) == 2
        assert len(game.capture_flags) == 2
        clock = ClockObject.getGlobalClock()
        clock.setMode(ClockObject.MNonRealTime)
        clock.setDt(1 / 60)
        first, second = game.capture_match.players
        second_position = second.x, second.y
        first_position = first.x, first.y
        game.set_key('w', True)
        game.taskMgr.step()
        assert (first.x, first.y) != first_position
        assert (second.x, second.y) == second_position
        game.keys.clear()
        first_position = first.x, first.y
        game.set_key('arrow_up', True)
        game.taskMgr.step()
        assert (first.x, first.y) == first_position
        assert (second.x, second.y) != second_position
        game.local_controls_menu(1)
        game.begin_local_binding('jump')
        game.capture_key('n')
        assert game.local_controls[1]['jump'] == 'n'
        device = fake_gamepad()
        game.gamepad_device = device
        game.gamepad_scan_time = 1000
        game.resume_capture()
        session = game.capture_match
        device.buttons[7].pressed = True
        game.taskMgr.step()
        assert game.mode == 'menu'
        positions = [(p.x, p.y) for p in session.players]
        game.taskMgr.step()
        assert positions == [(p.x, p.y) for p in session.players]
        game.two_player_menu()
        game.resume_capture()
        assert game.mode == 'capture' and game.capture_match is session
        game.main_menu()
        assert game.storage.read('save.json') == saved
        game.continue_game()
        assert game.mode == 'playing' and game.player.coins == 9
        assert game.capture_match is None
        game.graphicsEngine.renderFrame()
    finally:
        game.destroy()
