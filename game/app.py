"""Cena 3D, sprites direcionais, interface e áudio."""
from pathlib import Path
from io import BytesIO
import math
import random

from PIL import Image, ImageDraw, ImageFont
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    CardMaker, Filename, Fog, PNMImage, TextNode, Texture,
    TransparencyAttrib, Vec3, StringStream, AmbientLight, DirectionalLight,
    Geom, GeomNode, GeomTriangles, GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    InputDevice, InputDeviceManager, WindowProperties, BitMask32, loadPrcFileData,
)

from game.capture import CaptureMatch, LOCAL_ACTIONS, load_local_controls, replace_local_key
from game.state import DIFFICULTIES, PHASE_COUNT, FIELD_LIMIT, Player, Storage
from game.models import load_tree, load_enemy
from game.hud import SevenSegmentDisplay
from game.gamepad import GAMEPAD_ACTIONS, binding_label, load_bindings, mapped_actions, read_device, replace_binding
from game.camera import (facing_direction, follow_heading, relative_movement,
                         segment_box_hit, third_person_position, view_direction)
from game.controls import key_label, load_controls, valid_action_key
from game.world import (
    Encounter, TREE_CLUSTERS, TREE_SCALE, TREE_OBSTACLES, LOCAL_TREE_OBSTACLES,
    safe_position, terrain_height, terrain_surfaces, player_ground_height,
    jump_player, update_player_actions, move_on_terrain,
)

ROOT = Path(__file__).resolve().parent.parent
loadPrcFileData("", "window-title Wolf Riders\nwin-size 1280 720\nsync-video true\nshow-frame-rate-meter false")


def heart_outline():
    points = []
    for step in range(120):
        angle = step * 2 * math.pi / 120
        x = 16 * math.sin(angle) ** 3
        z = (13 * math.cos(angle) - 5 * math.cos(2 * angle)
             - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        points.append((x, z))
    return points


def pickup_geometry(name, outline):
    """Extrude a star-shaped outline into a collectible with visible thickness."""
    data = GeomVertexData(name, GeomVertexFormat.getV3c4(), Geom.UHStatic)
    vertex = GeomVertexWriter(data, "vertex")
    color = GeomVertexWriter(data, "color")
    triangles = GeomTriangles(Geom.UHStatic)
    stride = len(outline) + 1
    for y in (-0.08, 0.08):
        vertex.addData3(0, y, 0)
        color.addData4(1, 1, 1, 1)
        for x, z in outline:
            vertex.addData3(x, y, z)
            color.addData4(0.8, 0.8, 0.8, 1)
    for index in range(len(outline)):
        a, b = index + 1, (index + 1) % len(outline) + 1
        triangles.addVertices(0, a, b)
        triangles.addVertices(stride, b + stride, a + stride)
        triangles.addVertices(a, a + stride, b)
        triangles.addVertices(b, a + stride, b + stride)
    geometry = Geom(data)
    geometry.addPrimitive(triangles)
    return geometry


class Game(ShowBase):
    def __init__(self, *, offscreen=False, storage_directory=None):
        super().__init__(windowType="offscreen" if offscreen else None)
        self.original_camera_mask = self.cam.node().getCameraMask()
        self.disableMouse()
        self.ui_font = self.loader.loadFont(str(ROOT / "assets/fonts/goblin-digital.ttf"))
        self.body_font = self.loader.loadFont(str(ROOT / "assets/fonts/menu-mono.ttf"))
        self.setBackgroundColor(0.63, 0.80, 0.88)
        self.camLens.setFov(60)
        self.camLens.setNearFar(0.1, 400)
        self.storage = Storage(storage_directory or ROOT / ".local")
        settings = self.storage.read("settings.json")
        self.sound_enabled = settings.get("sound", True) is not False
        self.jump_key, self.attack_key = load_controls(settings)
        self.gamepad_bindings = load_bindings(settings)
        self.local_controls = load_local_controls(settings)
        self.local_binding = None
        self.local_team = 0
        self.capture_match = None
        self.capture_nodes = []
        self.local_previous = [{}, {}]
        self.gamepad_device = None
        self.second_gamepad_device = None
        self.second_gamepad_bindings = load_bindings({"gamepad_bindings": settings.get("second_gamepad_bindings")})
        self.second_gamepad_previous = {}
        self.controller_team = 0
        self.second_camera = None
        self.gamepad_previous = {}
        self.gamepad_scan_time = 0.0
        self.pending_gamepad_action = None
        self.gamepad_baseline = set()
        self.menu_previous_actions = {}
        self.menu_repeat_time = 0.0
        self.menu_focus = None
        self.menu_input_block = 0.0
        self.gamepad_message = ""
        self.binding_action = None
        self.binding_message = ""
        preference = settings.get("difficulty", "medium")
        self.difficulty = preference if isinstance(preference, str) and preference in DIFFICULTIES else "medium"
        self.player = Player()
        self.encounter = Encounter()
        self.mode = "menu"
        self.keys = {}
        self.camera_heading = 0.0
        self.follow_heading = 0.0
        self.camera_mode = "third_person"
        self.fps_heading = 0.0
        self.fps_pitch = 0.0
        self.camera_switch_cooldown = 0.0
        self.third_orbit_drag = False
        self.mouse_captured = False
        self.ui = []
        self.save_timer = 0.0
        self.music = None
        self.audio_error = ""
        self.make_world()
        self.make_sky()
        self.make_scenery()
        self.make_coins()
        self.load_sprites()
        self.make_character()
        self.update_enemies()
        try:
            self.music = self.loader.loadMusic(Filename.fromOsSpecific(str(ROOT / "assets/sound/theme.wav")))
            self.music.setLoop(True)
            self.music.setVolume(0.55)
        except (OSError, AttributeError) as error:
            self.audio_error = f"Áudio indisponível: {error}"
        self.apply_audio()
        for key in ("w", "a", "s", "d", "arrow_up", "arrow_down", "arrow_left", "arrow_right", "shift"):
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])
        self.bind_action_keys()
        if self.buttonThrowers:
            self.buttonThrowers[0].node().setButtonDownEvent("control-key")
            self.buttonThrowers[0].node().setButtonUpEvent("control-key-up")
        self.accept("control-key", self.capture_key)
        self.accept("control-key-up", self.release_key)
        self.accept("escape", self.escape)
        self.accept("f", self.toggle_camera)
        self.accept("mouse3", self.begin_camera_orbit)
        self.accept("mouse3-up", self.end_camera_orbit)
        self.accept("window-event", self.window_event)
        self.camera.setPos(0, -20, 7)
        self.camera.lookAt(0, 0, 3)
        self.main_menu()
        self.taskMgr.add(self.update, "game-update")

    def set_key(self, key, pressed):
        self.keys[key] = pressed

    def bind_action_keys(self):
        self.accept(self.jump_key, self.jump)
        self.accept(self.attack_key, self.attack)

    def save_settings(self):
        return self.storage.write("settings.json", {"sound": self.sound_enabled,
                                  "jump_key": self.jump_key, "attack_key": self.attack_key, "difficulty": self.difficulty,
                                  "gamepad_bindings": self.gamepad_bindings, "local_controls": self.local_controls, "second_gamepad_bindings": self.second_gamepad_bindings})

    def begin_binding(self, action):
        self.binding_action = action
        self.binding_message = "Pressione a nova tecla. Esc: cancelar."
        self.options()

    def release_key(self, button):
        key = button if isinstance(button, str) else button.getName()
        self.set_key(key, False)

    def capture_key(self, button):
        key = button if isinstance(button, str) else button.getName()
        self.set_key(key, True)
        if self.mode == "local_controls" and self.local_binding:
            if key == "escape":
                self.local_binding = None
            else:
                try:
                    self.local_controls = replace_local_key(self.local_controls, self.local_team, self.local_binding, key)
                except ValueError:
                    self.binding_message = "Tecla reservada. Escolha outra."
                else:
                    self.local_binding = None
                    self.binding_message = "Configuração substituída e salva"
                    self.save_settings()
            self.local_controls_menu(self.local_team)
            return
        if self.mode != "options" or self.binding_action is None:
            return
        key = button if isinstance(button, str) else button.getName()
        if key.startswith("mouse"):
            return
        if key == "escape":
            self.binding_action = None
            self.binding_message = "Escolha cancelada."
        elif not valid_action_key(key):
            self.binding_message = "Tecla reservada. Escolha outra tecla."
        else:
            other = self.attack_key if self.binding_action == "jump" else self.jump_key
            if key == other:
                self.binding_message = "A outra ação já usa essa tecla. Escolha outra."
            else:
                self.ignore(self.jump_key)
                self.ignore(self.attack_key)
                if self.binding_action == "jump":
                    self.jump_key = key
                else:
                    self.attack_key = key
                self.bind_action_keys()
                self.binding_action = None
                self.binding_message = "Tecla salva."
                self.save_settings()
        self.options()

    def window_event(self, window):
        if window and window.getProperties().hasForeground() and not window.getProperties().getForeground():
            self.keys.clear()
            self.set_mouse_capture(False)
        elif self.mode in ("playing", "victory") and self.camera_mode == "first_person":
            self.set_mouse_capture(True)

    def make_world(self):
        self.world = self.render.attachNewNode("field")
        rng = random.Random(42)
        # Split the surface at every rectangular boundary; join levels with walls.
        data = GeomVertexData("terrain", GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(data, "vertex")
        color = GeomVertexWriter(data, "color")
        triangles = GeomTriangles(Geom.UHStatic)
        xs, ys = {-100, 100}, {-100, 100}
        for x0, x1, y0, y1, height in terrain_surfaces():
            xs.update((x0, x1))
            ys.update((y0, y1))
        xs, ys = sorted(xs), sorted(ys)

        def quad(points, shade):
            start = vertex.getWriteRow()
            for point in points:
                vertex.addData3(*point)
                color.addData4(*shade, 1)
            triangles.addVertices(start, start + 1, start + 2)
            triangles.addVertices(start, start + 2, start + 3)

        for ix, (x0, x1) in enumerate(zip(xs, xs[1:])):
            for iy, (y0, y1) in enumerate(zip(ys, ys[1:])):
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                height = terrain_height(cx, cy)
                tone = height * 0.018
                quad([(x0, y0, height), (x1, y0, height),
                      (x1, y1, height), (x0, y1, height)],
                     (0.20 + tone, 0.43 + tone, 0.16 + tone))
                edges = [
                    ((x0, y1), (x0, y0), (xs[ix - 1] + x0) / 2 if ix else x0 - 1, cy),
                    ((x1, y0), (x1, y1), (x1 + xs[ix + 2]) / 2 if ix + 2 < len(xs) else x1 + 1, cy),
                    ((x0, y0), (x1, y0), cx, (ys[iy - 1] + y0) / 2 if iy else y0 - 1),
                    ((x1, y1), (x0, y1), cx, (y1 + ys[iy + 2]) / 2 if iy + 2 < len(ys) else y1 + 1),
                ]
                for (ax, ay), (bx, by), nx, ny in edges:
                    neighbor_height = terrain_height(nx, ny)
                    if height > neighbor_height:
                        quad([(ax, ay, height), (ax, ay, neighbor_height),
                              (bx, by, neighbor_height), (bx, by, height)],
                             (0.16, 0.29, 0.10))
        geometry = Geom(data)
        geometry.addPrimitive(triangles)
        node = GeomNode("terrain")
        node.addGeom(geometry)
        self.terrain = self.world.attachNewNode(node)
        # Small crossed grass blades distributed over the field, outside the spawn.
        for _ in range(650):
            x, y = rng.uniform(-98, 98), rng.uniform(-98, 98)
            cm = CardMaker("grass-blade")
            cm.setFrame(-0.07, 0.07, 0, rng.uniform(0.20, 0.50))
            grass = self.world.attachNewNode(cm.generate())
            grass.setPos(x, y, terrain_height(x, y) + 0.01)
            grass.setH(rng.uniform(0, 360))
            grass.setTwoSided(True)
            grass.setColor(0.29, 0.52, 0.16, 1)
        fog = Fog("distance")
        fog.setColor(0.63, 0.80, 0.88)
        fog.setLinearRange(65, 145)
        self.world.setFog(fog)
        self.distance_fog = fog

    def make_scenery(self):
        ambient = AmbientLight("ambient")
        ambient.setColor((0.65, 0.65, 0.60, 1))
        sun = DirectionalLight("sun")
        sun.setColor((0.75, 0.72, 0.60, 1))
        ambient_node = self.render.attachNewNode(ambient)
        sun_node = self.render.attachNewNode(sun)
        sun_node.setHpr(-35, -55, 0)
        self.ambient_light = ambient
        self.sun_light = sun
        self.ambient_node = ambient_node
        self.sun_node = sun_node
        self.camera_obstacles = []
        self.camera_obstacle_nodes = []
        tree_template = load_tree(ROOT / "assets/img/low.obj")
        for index, (x, y) in enumerate(TREE_CLUSTERS):
            trees = tree_template.copyTo(self.world)
            trees.setPos(x, y, terrain_height(x, y))
            trees.setScale(TREE_SCALE)
            trees.setH(index * 47)
            start = index * len(LOCAL_TREE_OBSTACLES)
            for part, (ox, oy, _) in zip(trees.getChildren(),
                                        TREE_OBSTACLES[start:start + len(LOCAL_TREE_OBSTACLES)]):
                part.setZ((terrain_height(ox, oy) - terrain_height(x, y)) / TREE_SCALE)
                lower, upper = part.getTightBounds(self.render)
                self.camera_obstacles.append((tuple(lower), tuple(upper)))
                self.camera_obstacle_nodes.append(part)
            trees.setLight(ambient_node)
            trees.setLight(sun_node)
        tree_template.removeNode()
        self.make_enemy_nodes()

    def make_enemy_nodes(self):
        template = load_enemy(ROOT / "assets/models/stilagmate.json")
        self.enemy_nodes = []
        self.enemy_bars = []
        for enemy in self.encounter.enemies:
            node = template.copyTo(self.world)
            node.setLight(self.ambient_node)
            node.setLight(self.sun_node)
            self.enemy_nodes.append(node)
            cm = CardMaker("enemy-health")
            cm.setFrame(-0.43, 0.43, 0, 0.09)
            bar = self.world.attachNewNode(cm.generate())
            bar.setBillboardPointEye()
            bar.setColor(0.85, 0.15, 0.08, 1)
            self.enemy_bars.append(bar)
        template.removeNode()

    def make_sky(self):
        self.sky = self.render.attachNewNode("cloud-sky")
        self.sky.setLightOff()
        data = GeomVertexData("cloud-lobe", GeomVertexFormat.getV3c4(), Geom.UHStatic)
        vertex = GeomVertexWriter(data, "vertex")
        color = GeomVertexWriter(data, "color")
        triangles = GeomTriangles(Geom.UHStatic)
        rings, segments = 10, 20
        for ring in range(rings + 1):
            latitude = math.pi * ring / rings
            shade = 0.86 + 0.14 * (1 + math.cos(latitude)) / 2
            for index in range(segments + 1):
                angle = index * 2 * math.pi / segments
                vertex.addData3(math.sin(latitude) * math.cos(angle),
                                math.sin(latitude) * math.sin(angle), math.cos(latitude))
                color.addData4(shade, shade, min(1, shade + 0.025), 1)
        for ring in range(rings):
            for index in range(segments):
                a = ring * (segments + 1) + index
                b = a + segments + 1
                triangles.addVertices(a, b, a + 1)
                triangles.addVertices(a + 1, b, b + 1)
        geometry = Geom(data)
        geometry.addPrimitive(triangles)
        rng = random.Random(17)
        self.cloud_nodes = []
        for index in range(16):
            angle = index * 2 * math.pi / 16
            radius = rng.uniform(110, 145)
            cloud = self.sky.attachNewNode(f"cloud-{index}")
            cloud.setPos(math.cos(angle) * radius, math.sin(angle) * radius, rng.uniform(12, 18))
            # The long axis is tangent to the sky ring, broadside to the camera.
            cloud.setH(math.degrees(angle) + 90)
            cloud_scale = rng.uniform(0.75, 1.15)
            cloud.setScale(cloud_scale)
            lobes = [(-10, -1, (7, 4, 2)), (-5, 1, (9, 5, 3)),
                     (2, 2, (10, 5, 3.5)), (9, 0, (8, 4, 2.5)), (15, -1, (6, 3, 1.8))]
            for offset, height, scale in lobes:
                lobe = GeomNode("cloud-lobe")
                lobe.addGeom(geometry)
                node = cloud.attachNewNode(lobe)
                node.setPos(offset, 0, height)
                node.setScale(*scale)
                node.setTwoSided(True)
            self.cloud_nodes.append(cloud)

        moon = GeomNode("full-moon")
        moon.addGeom(geometry)
        self.moon = self.sky.attachNewNode(moon)
        self.moon.setPos(35, 125, 13)
        self.moon.setScale(9)
        self.moon.setColorScale(1, 0.98, 0.85, 1)
        self.moon.setFogOff()
        self.moon.setTwoSided(True)
        self.moon.hide()

    def apply_phase(self):
        themes = [
            ((0.63, 0.80, 0.88), (1, 1, 1, 1), (1, 1, 1, 1),
             (0.65, 0.65, 0.60, 1), (0.75, 0.72, 0.60, 1)),
            ((0.95, 0.42, 0.16), (1, 0.72, 0.46, 1), (1, 0.73, 0.52, 1),
             (0.70, 0.43, 0.30, 1), (0.90, 0.48, 0.22, 1)),
            ((0.025, 0.04, 0.11), (0.50, 0.58, 0.76, 1), (0.19, 0.24, 0.38, 1),
             (0.45, 0.50, 0.68, 1), (0.35, 0.40, 0.58, 1)),
        ]
        sky, ground, clouds, ambient, sun = themes[self.player.phase]
        self.setBackgroundColor(*sky)
        self.distance_fog.setColor(*sky)
        self.world.setColorScale(*ground)
        self.actor.setColorScale(*ground)
        self.ambient_light.setColor(ambient)
        self.sun_light.setColor(sun)
        for cloud in self.cloud_nodes:
            cloud.setColorScale(*clouds)
        self.moon.show() if self.player.phase == 2 else self.moon.hide()

    def update_enemies(self):
        for enemy, node, bar in zip(self.encounter.enemies, self.enemy_nodes, self.enemy_bars):
            if not enemy.health:
                node.hide()
                bar.hide()
                continue
            node.show()
            bar.show()
            ground = terrain_height(enemy.x, enemy.y)
            node.setPos(enemy.x, enemy.y, ground)
            node.setH(math.degrees(math.atan2(enemy.x - self.player.x, enemy.y - self.player.y)))
            if enemy.flash:
                node.setColorScale(1.8, 0.8, 0.7, 1)
            else:
                node.clearColorScale()
            bar.setPos(enemy.x, enemy.y, ground + 1.75)
            bar.setScale(enemy.health / 2, 1, 1)
        if self.encounter.damage_cooldown > 1:
            self.sprite.setColorScale(1.5, 0.55, 0.55, 1)
        else:
            self.sprite.clearColorScale()

    def make_coins(self):
        outline = [(0.45 * math.cos(index * 2 * math.pi / 32),
                    0.45 * math.sin(index * 2 * math.pi / 32)) for index in range(32)]
        geometry = pickup_geometry("gold-coin", outline)
        self.coin_nodes = []
        for _ in self.encounter.enemies:
            coin = GeomNode("gold-coin")
            coin.addGeom(geometry)
            node = self.world.attachNewNode(coin)
            node.setColorScale(1, 0.72, 0.08, 1)
            node.setTwoSided(True)
            node.hide()
            self.coin_nodes.append(node)
        self.make_clocks(outline)
        self.coin_angle = 0.0
        geometry = pickup_geometry("health-heart", [(x * 0.45 / 16, z * 0.45 / 16)
                                                      for x, z in heart_outline()])
        self.heart_nodes = []
        for _ in self.encounter.hearts:
            heart = GeomNode("health-heart")
            heart.addGeom(geometry)
            node = self.world.attachNewNode(heart)
            node.setColorScale(1, 0.16, 0.23, 1)
            node.setTwoSided(True)
            self.heart_nodes.append(node)

    def make_clocks(self, outline):
        geometry = pickup_geometry("clock-body", outline)
        # A procedural dial on both faces keeps the clock readable while rotating.
        image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((4, 4, 123, 123), fill=(240, 248, 246, 255),
                     outline=(35, 155, 185, 255), width=9)
        for hour in range(12):
            angle = hour * math.pi / 6
            draw.line([(64 + radius * math.sin(angle), 64 - radius * math.cos(angle))
                       for radius in (43, 49)], fill=(20, 50, 65, 255), width=3)
        draw.line((64, 64, 64, 29), fill=(20, 50, 65, 255), width=5)
        draw.line((64, 64, 89, 78), fill=(20, 50, 65, 255), width=6)
        draw.ellipse((59, 59, 69, 69), fill=(35, 155, 185, 255))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        pnm = PNMImage()
        pnm.read(StringStream(buffer.getvalue()))
        texture = Texture("clock-dial")
        texture.load(pnm)
        self.clock_nodes = []
        for _ in self.encounter.clocks:
            node = self.world.attachNewNode("time-clock")
            body = GeomNode("clock-body")
            body.addGeom(geometry)
            rim = node.attachNewNode(body)
            rim.setColorScale(0.15, 0.72, 0.88, 1)
            rim.setTwoSided(True)
            for side in (-1, 1):
                cm = CardMaker("clock-dial")
                cm.setFrame(-0.45, 0.45, -0.45, 0.45)
                face = node.attachNewNode(cm.generate())
                face.setY(side * 0.081)
                if side == 1:
                    face.setH(180)
                face.setTexture(texture)
                face.setTransparency(TransparencyAttrib.MAlpha)
            node.setLightOff()
            self.clock_nodes.append(node)

    def update_coins(self, dt=0.0):
        self.coin_angle = (self.coin_angle + dt * 150) % 360
        for enemy, node in zip(self.encounter.enemies, self.coin_nodes):
            if enemy.health > 0 or enemy.coin_collected:
                node.hide()
            else:
                node.show()
                node.setPos(enemy.x, enemy.y, terrain_height(enemy.x, enemy.y) + 0.65)
                node.setH(self.coin_angle)
        for heart, node in zip(self.encounter.hearts, self.heart_nodes):
            if heart.collected:
                node.hide()
            else:
                node.show()
                node.setPos(heart.x, heart.y, terrain_height(heart.x, heart.y) + 0.65)
                node.setH(self.coin_angle)

        for clock, node in zip(self.encounter.clocks, self.clock_nodes):
            if clock.collected:
                node.hide()
            else:
                node.show()
                node.setPos(clock.x, clock.y, terrain_height(clock.x, clock.y) + 0.65)
                node.setH(self.coin_angle)

    def jump(self):
        if self.mode in ("playing", "victory"):
            jump_player(self.player)

    def attack(self):
        if self.mode == "playing" and self.player.start_attack():
            self.encounter.attack(self.player)
            self.update_enemies()
            self.update_hud()
            self.update_minimap()
            self.update_coins()
            result = self.encounter.match_result(self.player)
            if result:
                self.finish_match(result)

    def load_sprites(self):
        path = ROOT / "assets/img/wolf_riders.png"
        self.textures = {}
        with Image.open(path) as sheet:
            if sheet.size != (5376, 1024):
                raise ValueError(f"Folha wolf_riders inesperada: {sheet.size}; esperado 5376×1024")
            # Keep the same crop/anchor for all frames to avoid animation jitter.
            for row in range(8):
                for column in (0, *range(4, 18)):
                    frame = sheet.crop((column * 128 + 24, row * 128 + 24,
                                        column * 128 + 104, row * 128 + 112)).convert("RGBA")
                    pnm = PNMImage()
                    buffer = BytesIO()
                    frame.save(buffer, format="PNG")
                    pnm.read(StringStream(buffer.getvalue()))
                    texture = Texture(f"rider-{row}-{column}")
                    texture.load(pnm)
                    texture.setMinfilter(Texture.FTNearest)
                    texture.setMagfilter(Texture.FTNearest)
                    self.textures[row, column] = texture

    def make_character(self):
        self.actor = self.render.attachNewNode("wolf-rider")
        cm = CardMaker("rider-sprite")
        cm.setFrame(-1.55, 1.55, -0.35, 3.06)
        self.sprite = self.actor.attachNewNode(cm.generate())
        self.sprite.setTransparency(TransparencyAttrib.MAlpha)
        self.sprite.setBillboardPointEye()
        self.sprite.setDepthWrite(False)
        self.sprite.setTexture(self.textures[6, 0])
        # Elliptical ground shadow, independent of the billboard.
        cm = CardMaker("shadow")
        cm.setFrame(-1, 1, -1, 1)
        shadow = self.actor.attachNewNode(cm.generate())
        self.shadow = shadow
        shadow.setP(-90)
        shadow.setZ(0.025)
        shadow.setScale(1.2, 1, 0.55)
        image = PNMImage(64, 64, 4)
        for x in range(64):
            for y in range(64):
                distance = math.hypot((x - 31.5) / 31.5, (y - 31.5) / 31.5)
                image.setXelA(x, y, 0.02, 0.06, 0.01, max(0, 1 - distance) * 0.4)
        texture = Texture("shadow")
        texture.load(image)
        shadow.setTexture(texture)
        shadow.setTransparency(TransparencyAttrib.MAlpha)
        shadow.setDepthWrite(False)

    def clear_ui(self):
        for element in self.ui:
            element.destroy()
        self.ui.clear()
        self.menu_focus = None

    def label(self, text, z, scale=0.055, color=(0.90, 0.92, 0.82, 1)):
        element = DirectLabel(text=text, text_font=self.ui_font if scale >= 0.09 else self.body_font, text_scale=max(scale, 0.036), text_fg=color,
                              text_align=TextNode.ACenter, frameColor=(0, 0, 0, 0), pos=(0, 0, z))
        self.ui.append(element)
        return element

    def button(self, text, z, command, enabled=True, *, x=0, width=0.65, scale=0.060, compact=False):
        element = DirectButton(text=text, text_font=self.body_font, text_scale=scale,
                               text_fg=(0.95, 0.94, 0.84, 1),
                               frameSize=(-width, width, -0.05 if compact else -0.065, 0.06 if compact else 0.085),
                               frameColor=((0.16, 0.25, 0.19, 1), (0.11, 0.18, 0.13, 1),
                                           (0.27, 0.39, 0.23, 1), (0.15, 0.17, 0.15, 1)),
                               pos=(x, 0, z), relief=1, command=command,
                               state="normal" if enabled else "disabled")
        self.ui.append(element)
        if self.menu_focus is None and enabled:
            self.menu_focus = element
            element.setColorScale(1.15, 1.20, 1.25, 1)

    def panel(self):
        self.clear_ui()
        self.ui.append(DirectFrame(parent=self.render2d, frameColor=(0.025, 0.045, 0.055, 0.97),
                                   frameSize=(-1, 1, -1, 1)))
        self.label("WOLF RIDERS", 0.78, 0.12, (0.82, 0.76, 0.44, 1))
        self.label("Os campos verdes", 0.64, 0.052)

    def save(self):
        return self.storage.save_player(self.player, self.encounter.snapshot(),
                                        self.encounter.heart_snapshot(),
                                        self.encounter.clock_snapshot())

    def main_menu(self):
        self.pending_gamepad_action = None
        self.local_binding = None
        self.set_mouse_capture(False)
        if self.mode in ("playing", "victory"):
            self.save()
        self.mode = "menu"
        self.binding_action = None
        self.binding_message = ""
        self.keys.clear()
        self.panel()
        saved_player = self.storage.load_player()
        self.menu_coin_icon = self.gold_coin_icon(self.aspect2d, (-0.11, 0, 0.30), 0.075)
        self.ui.append(self.menu_coin_icon)
        self.menu_coins_label = DirectLabel(text_font=self.ui_font, text=str(saved_player.coins if saved_player else 0),
                                           text_scale=0.075, text_align=TextNode.ALeft,
                                           text_fg=(1, 0.81, 0.24, 1),
                                           frameColor=(0, 0, 0, 0), pos=(0.01, 0, 0.275))
        self.ui.append(self.menu_coins_label)
        self.button("Novo jogo", 0.09, self.new_game)
        self.button("Continuar", -0.12, self.continue_game, saved_player is not None)
        self.button("Dois jogadores", -0.33, self.two_player_menu)
        self.button("Opções", -0.54, self.options)
        self.button("Sair", -0.75, self.userExit)
        self.label(self.storage.last_error or "WASD / setas | Shift para correr", -0.94, 0.035)

    def two_player_menu(self):
        self.mode = "two_players"
        self.local_binding = None
        self.keys.clear()
        self.panel()
        self.label("CAPTURE A BANDEIRA", 0.43, 0.07)
        self.label("Encontre todas as bandeiras da sua cor", 0.31, 0.043)
        self.button("Jogar", 0.10, self.new_capture, x=-0.76)
        self.button("Nível: " + DIFFICULTIES[self.difficulty][0], 0.10, self.cycle_local_difficulty, x=0.76)
        self.button("Retomar partida", -0.10, self.resume_capture, self.capture_match is not None)
        self.button("Configurar Verde", -0.32, lambda: self.local_controls_menu(0), x=-0.76)
        self.button("Configurar Azul", -0.32, lambda: self.local_controls_menu(1), x=0.76)
        self.button("USB Verde / Azul", -0.55, lambda: self.controller_options(team=0), x=-0.76)
        self.button("Voltar", -0.55, self.main_menu, x=0.76)
        self.label("Dois controles USB ou teclados — sem limite de tempo", -0.82, 0.041)

    def cycle_local_difficulty(self):
        modes = list(DIFFICULTIES)
        self.difficulty = modes[(modes.index(self.difficulty) + 1) % len(modes)]
        self.save_settings()
        self.two_player_menu()

    def local_controls_menu(self, team):
        self.mode = "local_controls"
        self.local_team = team
        self.keys.clear()
        self.panel()
        self.label("CONTROLES — " + ("VERDE" if team == 0 else "AZUL"), 0.43, 0.07)
        for index, (action, title) in enumerate(LOCAL_ACTIONS.items()):
            column, row = index // 4, index % 4
            self.button(title + ": " + key_label(self.local_controls[team][action]),
                        0.19 - row * 0.20,
                        lambda action=action: self.begin_local_binding(action),
                        x=-0.76 if column == 0 else 0.76, width=0.69, scale=0.052)
        self.button("Voltar", -0.70, self.two_player_menu)
        self.label("Pressione a nova tecla; Esc cancela" if self.local_binding
                   else self.binding_message or "Selecione a ação para substituir a tecla", -0.90, 0.04)

    def begin_local_binding(self, action):
        self.local_binding = action
        self.local_controls_menu(self.local_team)

    def close_capture(self):
        if self.second_camera is not None:
            for region in list(self.second_camera.node().getDisplayRegions()):
                self.win.removeDisplayRegion(region)
            if self.second_camera in self.camList:
                self.camList.remove(self.second_camera)
            self.second_camera.removeNode()
            self.second_camera = None
            self.cam.node().getDisplayRegion(0).setDimensions(0, 1, 0, 1)
            self.camLens.setAspectRatio(self.getAspectRatio())
            self.camLens.setFov(75 if self.camera_mode == "first_person" else 60)
            self.cam.node().setCameraMask(self.original_camera_mask)
        for node in self.capture_nodes:
            node.removeNode()
        self.capture_nodes = []
        self.capture_match = None
        self.actor.clearColorScale()
        self.actor.show()
        self.sprite.show()
        self.shadow.show()

    def new_capture(self):
        self.close_capture()
        self.capture_match = CaptureMatch(difficulty=self.difficulty)
        self.player = self.capture_match.players[0]
        self.player.phase = 0
        self.apply_phase()
        self.second_actor = self.actor.copyTo(self.render)
        self.second_sprite = self.second_actor.find("**/rider-sprite")
        self.second_actor.setColorScale(0.55, 0.75, 1, 1)
        self.capture_nodes.append(self.second_actor)
        self.capture_flags = []
        for index, flag in enumerate(self.capture_match.flags):
            team = flag.team
            root = self.render.attachNewNode("bandeira-" + str(index))
            # Poste de 4 unidades: metade da altura de 3,41 do sprite.
            root.setScale(0.42625)
            root.setBillboardAxis()
            root.setLightOff()
            pole = CardMaker("poste")
            pole.setFrame(-0.06, 0.06, 0, 4)
            node = root.attachNewNode(pole.generate())
            node.setColor(0.8, 0.8, 0.8, 1)
            node.setTwoSided(True)
            cloth = CardMaker("bandeira")
            cloth.setFrame(0, 2, 2.5, 4)
            node = root.attachNewNode(cloth.generate())
            node.setColor(*( (0.1, 0.95, 0.25, 1) if team == 0 else (0.12, 0.4, 1, 1)))
            node.setTwoSided(True)
            self.capture_flags.append(root)
            self.capture_nodes.append(root)
        self.local_previous = [{}, {}]
        self.local_camera_mode = "third_person"
        self.cam.node().setCameraMask(BitMask32.bit(0))
        self.cam.node().getDisplayRegion(0).setDimensions(0, 1, 0.5, 1)
        self.camLens.setAspectRatio(self.getAspectRatio() * 2)
        self.camLens.setFov(90)
        lens = self.camLens.makeCopy()
        self.second_camera = self.makeCamera(self.win, displayRegion=(0, 1, 0, 0.5), lens=lens)
        self.second_camera.reparentTo(self.render)
        self.second_camera.node().setCameraMask(BitMask32.bit(1))
        self.local_headings = [90.0, 270.0]
        for player, heading in zip(self.capture_match.players, self.local_headings):
            player.direction = facing_direction(heading)
        self.resume_capture()

    def resume_capture(self):
        if self.capture_match is None:
            return
        self.mode = "capture"
        self.local_binding = None
        self.keys.clear()
        self.set_mouse_capture(False)
        self.clear_ui()
        self.capture_scores = []
        for team in range(2):
            label = DirectLabel(parent=self.a2dTopCenter, text_font=self.body_font,
                text="", text_scale=0.045, text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1), frameColor=(0, 0, 0, 0), pos=(0, 0, -0.10 - team))
            self.capture_scores.append(label)
            self.ui.append(label)
        self.capture_score = self.capture_scores[0]
        self.ui.append(DirectFrame(parent=self.render2d, frameColor=(0.01, 0.02, 0.03, 1),
                                   frameSize=(-1, 1, -0.005, 0.005)))
        for node in self.enemy_nodes + self.enemy_bars + self.coin_nodes + self.heart_nodes + self.clock_nodes:
            node.hide()
        self.sprite.show()
        self.shadow.show()
        self.update_capture(0, {})

    def update_capture(self, dt, pad, second_pad=None):
        pads = [pad, second_pad or {}]
        match = self.capture_match
        for team, player in enumerate(match.players):
            actions = {action: bool(self.keys.get(key, False) or pads[team].get(action, False))
                       for action, key in self.local_controls[team].items()}
            edges = {action for action, pressed in actions.items()
                     if pressed and not self.local_previous[team].get(action, False)}
            self.local_previous[team] = actions
            if match.winner is None:
                if "jump" in edges:
                    jump_player(player)
                if "attack" in edges:
                    match.attack(team)
                update_player_actions(player, dt)
                self.local_headings[team] = (self.local_headings[team] + 120 * dt *
                    (int(pads[team].get('look_right', False)) - int(pads[team].get('look_left', False)))) % 360
                heading = self.local_headings[team]
                dx, dy = relative_movement(int(actions['right']) - int(actions['left']),
                                          int(actions['up']) - int(actions['down']), heading)
                old_x, old_y = player.x, player.y
                player.move(dx, dy, actions['run'], dt)
                move_on_terrain(player, old_x, old_y, [])
                if player.health <= 0:
                    player.x, player.y = match.bases[team]
                    player.health = 5
                    player.z = player.vertical_speed = 0
            actor = self.actor if team == 0 else self.second_actor
            sprite = self.sprite if team == 0 else self.second_sprite
            ground = player_ground_height(player.x, player.y)
            actor.setPos(player.x, player.y, ground)
            sprite.setZ(player.z)
            row = (player.direction - round(self.local_headings[team] / 45)) % 8
            sprite.setTexture(self.textures[row, player.frame])
        self.actor.setColorScale(0.65, 1, 0.65, 1)
        match.update()
        for flag, node in zip(match.flags, self.capture_flags):
            if flag.captured:
                node.hide()
                continue
            height = terrain_height(flag.x, flag.y)
            node.setPos(flag.x, flag.y, height)
        for team, player in enumerate(match.players):
            camera = self.camera if team == 0 else self.second_camera
            angle = math.radians(self.local_headings[team])
            foot = player_ground_height(player.x, player.y) + player.z
            desired = (player.x - math.sin(angle) * 12, player.y - math.cos(angle) * 12, foot + 4.5)
            actor = self.actor if team == 0 else self.second_actor
            if self.local_camera_mode == "first_person":
                actor.hide(BitMask32.bit(team))
                camera.setPos(player.x, player.y, foot + 2)
                camera.lookAt(player.x + math.sin(angle), player.y + math.cos(angle), foot + 2)
            else:
                actor.show(BitMask32.bit(team))
                position = third_person_position((player.x, player.y, foot), desired, self.camera_obstacles, terrain_height)
                camera.setPos(*position)
                camera.lookAt(player.x, player.y, foot + 1.8)
            if self.local_camera_mode == "third_person":
                self.local_headings[team] = math.degrees(math.atan2(player.x - camera.getX(), player.y - camera.getY())) % 360
        self.sky.setPos(match.players[0].x, match.players[0].y, 0)
        for obstacle, node in zip(self.camera_obstacles, self.camera_obstacle_nodes):
            obscures = any(segment_box_hit(tuple(self.camera.getPos()),
                            (p.x, p.y, player_ground_height(p.x, p.y) + p.z + 1.5), obstacle)
                           for p in match.players) or any(segment_box_hit(tuple(self.second_camera.getPos()),
                            (p.x, p.y, player_ground_height(p.x, p.y) + p.z + 1.5), obstacle)
                           for p in match.players)
            if obscures:
                node.setTransparency(TransparencyAttrib.MAlpha)
                node.setColorScale(1, 1, 1, 0.15)
                node.setDepthWrite(False)
            else:
                node.clearColorScale()
                node.clearTransparency()
                node.clearDepthWrite()
        for team, label in enumerate(self.capture_scores):
            label['text'] = ("VERDE" if team == 0 else "AZUL") + f" {match.scores[team]}/{match.flag_count}"
            if match.winner is not None:
                label['text'] += " — " + ("VERDE" if match.winner == 0 else "AZUL") + " VENCEU"

    def new_game(self, difficulty=None):
        self.close_capture()
        self.player = Player(difficulty=difficulty or self.difficulty)
        self.encounter = Encounter(difficulty=self.player.difficulty)
        self.save()
        self.start_game()

    def continue_game(self):
        self.close_capture()
        player = self.storage.load_player()
        if player is not None:
            self.player = player
            self.encounter = Encounter(difficulty=player.difficulty)
            self.encounter.restore(self.storage.read("save.json").get("enemies"))
            self.encounter.restore_hearts(self.storage.read("save.json").get("hearts"))
            self.encounter.restore_clocks(self.storage.read("save.json").get("clocks"))
            self.start_game()

    def start_game(self):
        if len(self.enemy_nodes) != len(self.encounter.enemies):
            for node in self.enemy_nodes + self.enemy_bars + self.coin_nodes + self.heart_nodes + self.clock_nodes:
                node.removeNode()
            self.make_enemy_nodes()
            self.make_coins()
        self.apply_phase()
        self.player.x, self.player.y = safe_position(self.player.x, self.player.y)
        self.mode = "playing"
        self.keys.clear()
        self.clear_ui()
        self.make_hud()
        self.make_minimap()
        self.save_timer = 0
        self.update_character()
        self.update_enemies()
        self.update_coins()
        ground = player_ground_height(self.player.x, self.player.y)
        self.sky.setPos(self.player.x, self.player.y, ground)
        self.update_camera(snap=True)
        self.set_mouse_capture(self.camera_mode == "first_person")
        result = self.encounter.match_result(self.player)
        if result:
            self.finish_match(result)

    def finish_match(self, result):
        if result == "victory" and self.player.phase < PHASE_COUNT - 1:
            self.player = Player(health=self.player.health, coins=self.player.coins,
                                 phase=self.player.phase + 1, difficulty=self.player.difficulty)
            self.encounter = Encounter(difficulty=self.player.difficulty)
            self.save()
            self.start_game()
            return
        self.mode = result
        self.keys.clear()
        self.save()
        if result == "victory":
            self.clear_ui()
            self.make_hud()
            self.make_minimap()
            self.label("VITÓRIA! Todos os monstros derrotados!", 0.72, 0.05)
            return
        self.set_mouse_capture(False)
        self.panel()
        self.label("VITÓRIA!" if result == "victory" else "TEMPO ESGOTADO!", 0.20, 0.065)
        self.label(f"Monstros: {self.encounter.defeated}/{len(self.encounter.enemies)}   Moedas: {self.player.coins}", 0.04, 0.04)
        self.button("Novo jogo", -0.18, self.new_game)
        self.button("Menu", -0.39, self.main_menu)
        self.label(self.storage.last_error or "Derrote os monstros antes de o tempo acabar.", -0.63, 0.032)

    def gold_coin_icon(self, parent, position, scale):
        image = Image.new("RGBA", (64, 64))
        draw = ImageDraw.Draw(image)
        draw.ellipse((3, 3, 60, 60), fill=(255, 192, 28, 255),
                     outline=(184, 117, 10, 255), width=3)
        draw.ellipse((10, 10, 53, 53), outline=(255, 225, 112, 255), width=2)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        pnm = PNMImage()
        pnm.read(StringStream(buffer.getvalue()))
        coin = Texture("hud-gold-coin")
        coin.load(pnm)
        icon = DirectFrame(parent=parent, image=coin, image_scale=scale,
                           frameColor=(0, 0, 0, 0), pos=position)
        icon.setTransparency(TransparencyAttrib.MAlpha)
        return icon

    def make_hud(self):
        panel = DirectFrame(parent=self.a2dTopLeft, pos=(0.04, 0, -0.04),
                            frameSize=(0, 0, 0, 0),
                            frameColor=(0, 0, 0, 0))
        self.ui.append(panel)
        image = Image.new("RGBA", (128, 128))
        draw = ImageDraw.Draw(image)
        points = [(64 + x * 3.5, 57 - y * 3.5) for x, y in heart_outline()]
        draw.polygon(points, fill="white")
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        pnm = PNMImage()
        pnm.read(StringStream(buffer.getvalue()))
        heart = Texture("hud-heart")
        heart.load(pnm)
        self.heart_icons = []
        for index in range(5):
            icon = DirectFrame(parent=panel, image=heart, image_scale=0.047,
                               frameColor=(0, 0, 0, 0), pos=(0.075 + index * 0.115, 0, -0.09))
            icon.setTransparency(TransparencyAttrib.MAlpha)
            self.heart_icons.append(icon)
        self.hud_coin_icon = self.gold_coin_icon(panel, (0.70, 0, -0.09), 0.047)
        self.coins_display = SevenSegmentDisplay(panel, (0.77, 0, -0.09))
        self.timer_display = SevenSegmentDisplay(panel, (1.0, 0, -0.09))
        self.crosshair = self.label("+", 0, 0.035, (1, 1, 1, 1))
        self.crosshair.hide()
        self.update_hud()

    def update_hud(self):
        for index, icon in enumerate(self.heart_icons):
            icon.setColorScale((0.95, 0.16, 0.23, 1) if index < self.player.health
                               else (0.28, 0.31, 0.30, 1))
        self.coins_display.set_value(str(self.player.coins))
        self.timer_display.setX(self.coins_display.getX() + self.coins_display.width + 0.13)
        seconds = math.ceil(self.player.time_remaining)
        self.timer_display.set_value(f"{seconds // 60:02d}:{seconds % 60:02d}")

    def make_minimap(self):
        self.minimap_texture = Texture("minimap")
        self.minimap_texture.setMinfilter(Texture.FTLinear)
        self.minimap_texture.setMagfilter(Texture.FTLinear)
        self.minimap = DirectFrame(parent=self.a2dTopRight, pos=(-0.22, 0, -0.22),
                                   image=self.minimap_texture, image_scale=0.18,
                                   frameColor=(0, 0, 0, 0))
        self.minimap.setTransparency(TransparencyAttrib.MAlpha)
        self.ui.append(self.minimap)
        self.minimap_timer = 0.0
        self.update_minimap()

    def update_minimap(self):
        # North is up. The full square field fits inside the circular map.
        image = Image.new("RGBA", (192, 192))
        draw = ImageDraw.Draw(image)
        draw.ellipse((2, 2, 189, 189), fill=(18, 40, 27, 230),
                     outline=(210, 206, 162, 255), width=3)
        draw.text((93, 8), "N", fill=(235, 235, 210, 255),
                  font=ImageFont.truetype(str(ROOT / "assets/fonts/goblin-digital.ttf"), 12))
        scale = 80 / (FIELD_LIMIT * math.sqrt(2))

        def marker(x, y, radius, color):
            cx, cy = 96 + x * scale, 96 - y * scale
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         fill=color, outline=(0, 0, 0, 255), width=1)

        for enemy in self.encounter.enemies:
            if enemy.health > 0:
                marker(enemy.x, enemy.y, 3, (255, 75, 65, 255))
        marker(self.player.x, self.player.y, 4, (240, 245, 255, 255))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        pnm = PNMImage()
        pnm.read(StringStream(buffer.getvalue()))
        self.minimap_texture.load(pnm)

    def options(self):
        self.set_mouse_capture(False)
        self.mode = "options"
        self.keys.clear()
        self.panel()
        self.label("OPÇÕES", 0.43, 0.07)
        self.button("Som: " + ("ativado" if self.sound_enabled else "desativado"), 0.08, self.toggle_sound, x=-0.76)
        self.button("Dificuldade: " + DIFFICULTIES[self.difficulty][0], 0.08, self.cycle_difficulty, x=0.76)
        self.button("Pulo: " + key_label(self.jump_key), -0.20, lambda: self.begin_binding("jump"), x=-0.76)
        self.button("Ataque: " + key_label(self.attack_key), -0.20, lambda: self.begin_binding("attack"), x=0.76)
        self.button("Controle USB", -0.48, self.controller_options, x=-0.76)
        self.button("Voltar", -0.48, self.main_menu, x=0.76)
        self.label(self.storage.last_error or self.binding_message or self.audio_error
                   or "Dificuldade aplicada ao novo jogo", -0.82, 0.042)

    def scan_gamepad(self):
        devices = InputDeviceManager.getGlobalPtr().getDevices()
        candidates = [device for device in devices if device.connected and device.device_class in
                      (InputDevice.DeviceClass.gamepad, InputDevice.DeviceClass.unknown)]
        available = candidates.copy()
        device = next((item for item in available if item == self.gamepad_device), None)
        fallback = [item for item in available if item != self.second_gamepad_device]
        device = device or (fallback[0] if fallback else None)
        available = [item for item in available if item != device]
        second = next((item for item in available if item == self.second_gamepad_device), None)
        second = second or (available[0] if available else None)
        changed = device != self.gamepad_device or second != self.second_gamepad_device
        if changed:
            self.gamepad_device, self.second_gamepad_device = device, second
            self.gamepad_previous = {}
            self.second_gamepad_previous = {}
            self.pending_gamepad_action = None
            self.gamepad_baseline = set()
            if self.mode == "controller_options":
                self.controller_options(scan=False)

    def configured_device(self):
        return self.gamepad_device if self.controller_team == 0 else self.second_gamepad_device

    def configured_bindings(self):
        return self.gamepad_bindings if self.controller_team == 0 else self.second_gamepad_bindings

    def switch_controller_team(self):
        self.pending_gamepad_action = None
        self.gamepad_message = ""
        self.controller_options(scan=False, team=1 - self.controller_team)

    def controller_options(self, *, scan=True, team=None):
        if team is not None:
            self.controller_team = team
        self.set_mouse_capture(False)
        self.keys.clear()
        if scan:
            self.scan_gamepad()
        self.mode = "controller_options"
        self.panel()
        self.button("USB " + ("VERDE" if self.controller_team == 0 else "AZUL") + " — trocar jogador",
                    0.47, self.switch_controller_team, width=1.0, scale=0.045, compact=True)
        device = self.configured_device()
        connected = device is not None and device.connected
        name = device.name if connected else "Nenhum controle USB detectado"
        self.label(name[:60], 0.35, 0.042)
        for index, (action, title) in enumerate(GAMEPAD_ACTIONS.items()):
            column, row = ((0, index) if index < 4 else
                           (0, index - 5) if index >= 9 else (1, index - 4))
            text = f"{title}: {binding_label(self.configured_bindings()[action])}"
            self.button(text, 0.20 - row * 0.17,
                        lambda action=action: self.begin_gamepad_binding(action), connected,
                        x=-0.78 if column == 0 else 0.78, width=0.70, scale=0.053, compact=True)
        self.button("Voltar", -0.83, self.leave_controller_options)
        if self.pending_gamepad_action:
            message = self.gamepad_message or "Mova/pressione o controle. Esc cancela."
        else:
            message = self.gamepad_message or "Escolha uma ação para configurar"
        self.label(self.storage.last_error or message, -0.96, 0.038)

    def leave_controller_options(self):
        self.pending_gamepad_action = None
        self.gamepad_message = ""
        self.options()

    def begin_gamepad_binding(self, action):
        device = self.configured_device()
        if device is None or not device.connected:
            return
        self.pending_gamepad_action = action
        self.menu_input_block = 0.25
        self.gamepad_message = ""
        self.gamepad_baseline = read_device(device)
        self.controller_options(scan=False)

    def poll_gamepad(self, elapsed):
        self.gamepad_scan_time -= elapsed
        if self.gamepad_scan_time <= 0:
            self.gamepad_scan_time = 0.5
            self.scan_gamepad()
        active = read_device(self.gamepad_device)
        if self.mode == "controller_options" and self.pending_gamepad_action:
            capture_active = read_device(self.configured_device())
            fresh = capture_active - self.gamepad_baseline
            self.gamepad_baseline.intersection_update(capture_active)
            if fresh:
                binding = sorted(fresh)[0]
                action = self.pending_gamepad_action
                bindings = replace_binding(self.configured_bindings(), action, binding)
                if self.controller_team == 0:
                    self.gamepad_bindings = bindings
                else:
                    self.second_gamepad_bindings = bindings
                self.save_settings()
                self.pending_gamepad_action = None
                self.menu_input_block = 0.25
                self.gamepad_message = "Configuração substituída e salva"
                self.controller_options(scan=False)
        actions = mapped_actions(active, self.gamepad_bindings)
        edges = {action for action, pressed in actions.items()
                 if pressed and not self.gamepad_previous.get(action, False)}
        self.gamepad_previous = actions
        second_actions = mapped_actions(read_device(self.second_gamepad_device), self.second_gamepad_bindings)
        self.second_gamepad_edges = {action for action, pressed in second_actions.items()
                                    if pressed and not self.second_gamepad_previous.get(action, False)}
        self.second_gamepad_previous = second_actions
        return actions, edges

    def cycle_difficulty(self):
        modes = list(DIFFICULTIES)
        self.difficulty = modes[(modes.index(self.difficulty) + 1) % len(modes)]
        self.save_settings()
        self.options()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.save_settings()
        self.apply_audio()
        self.options()

    def apply_audio(self):
        if self.music:
            if self.sound_enabled:
                self.music.play()
            else:
                self.music.stop()

    def escape(self):
        if self.mode == "local_controls":
            if self.local_binding:
                self.local_binding = None
                self.local_controls_menu(self.local_team)
            else:
                self.two_player_menu()
            return
        if self.mode == "controller_options":
            if self.pending_gamepad_action:
                self.pending_gamepad_action = None
                self.gamepad_message = "Escolha cancelada"
                self.controller_options(scan=False)
            else:
                self.leave_controller_options()
            return
        if self.mode == "options" and self.binding_action is not None:
            self.binding_action = None
            self.binding_message = "Escolha cancelada."
            self.options()
            return
        if self.mode in ("playing", "capture", "two_players", "local_controls", "options", "victory", "defeat"):
            self.main_menu()
        else:
            self.continue_game()

    def update_character(self):
        ground = player_ground_height(self.player.x, self.player.y)
        self.actor.setPos(self.player.x, self.player.y, ground)
        self.sprite.setZ(self.player.z)
        self.shadow.setZ(terrain_height(self.player.x, self.player.y) - ground + 0.025)
        self.shadow.setScale(1.2 / (1 + self.player.z * 0.15), 1, 0.55 / (1 + self.player.z * 0.15))
        view = self.player.x - self.camera.getX(), self.player.y - self.camera.getY()
        self.sprite_direction = (self.player.direction - round(math.atan2(*view) / (math.pi / 4))) % 8
        self.sprite.setTexture(self.textures[self.sprite_direction, self.player.frame])

    def set_mouse_capture(self, enabled):
        self.mouse_captured = False
        if not self.win or not hasattr(self.win, "requestProperties"):
            return
        properties = WindowProperties()
        properties.setCursorHidden(enabled)
        properties.setMouseMode(WindowProperties.M_confined if enabled else WindowProperties.M_absolute)
        self.win.requestProperties(properties)
        if enabled:
            self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2)
        self.mouse_captured = enabled

    def turn_fps_view(self, dx, dy):
        self.fps_heading = (self.fps_heading + dx * 0.15) % 360
        self.fps_pitch = max(-75, min(75, self.fps_pitch - dy * 0.15))
        self.player.direction = facing_direction(self.fps_heading)

    def update_mouse_look(self):
        if not self.mouse_captured:
            return
        pointer = self.win.getPointer(0)
        if not pointer.getInWindow():
            return
        center_x, center_y = self.win.getXSize() // 2, self.win.getYSize() // 2
        self.turn_fps_view(pointer.getX() - center_x, pointer.getY() - center_y)
        self.win.movePointer(0, center_x, center_y)

    def begin_camera_orbit(self):
        if self.mode in ("playing", "victory") and self.camera_mode == "third_person":
            self.third_orbit_drag = True
            self.fps_heading = self.follow_heading
            self.set_mouse_capture(True)

    def end_camera_orbit(self):
        self.third_orbit_drag = False
        if self.camera_mode == "third_person":
            self.set_mouse_capture(False)

    def view_heading(self):
        if self.camera_mode == "first_person":
            return self.fps_heading
        return (math.degrees(math.atan2(self.player.x - self.camera.getX(),
                                       self.player.y - self.camera.getY())) + 360) % 360

    def toggle_camera(self):
        if self.mode == "capture" and self.camera_switch_cooldown <= 0:
            self.camera_switch_cooldown = 0.35
            self.local_camera_mode = "first_person" if self.local_camera_mode == "third_person" else "third_person"
            self.update_capture(0, {}, {})
            return
        if self.mode not in ("playing", "victory") or self.camera_switch_cooldown > 0:
            return
        self.camera_switch_cooldown = 0.35
        self.third_orbit_drag = False
        if self.camera_mode == "third_person":
            self.fps_heading = self.view_heading()
            self.camera_mode = "first_person"
            self.fps_pitch = 0
            self.player.direction = facing_direction(self.fps_heading)
        else:
            self.camera_mode = "third_person"
            self.follow_heading = self.fps_heading
        self.set_mouse_capture(self.camera_mode == "first_person")
        self.update_camera(snap=True)
        self.update_character()

    def update_camera(self, dt=0.0, *, snap=False):
        foot_height = player_ground_height(self.player.x, self.player.y) + self.player.z
        if self.camera_mode == "first_person":
            self.sprite.hide()
            self.shadow.hide()
            self.crosshair.show()
            self.camLens.setFov(75)
            self.camera.setPos(self.player.x, self.player.y, foot_height + 2)
            self.camera.lookAt(self.camera.getPos() + Vec3(*view_direction(self.fps_heading, self.fps_pitch)))
            for node in self.camera_obstacle_nodes:
                node.clearTransparency()
                node.clearColorScale()
                node.setDepthWrite(True)
            return
        self.sprite.show()
        self.shadow.show()
        self.crosshair.hide()
        self.camLens.setFov(60)
        self.camera_heading = (self.follow_heading if snap else
                               follow_heading(self.camera_heading, self.follow_heading, dt))
        angle = math.radians(self.camera_heading)
        desired = (self.player.x - 20 * math.sin(angle),
                   self.player.y - 20 * math.cos(angle), foot_height + 7)
        position = third_person_position((self.player.x, self.player.y, foot_height),
                                         desired, self.camera_obstacles, terrain_height)
        self.camera.setPos(*position)
        distance = math.hypot(position[0] - self.player.x, position[1] - self.player.y)
        look_height = 1.5 + 1.5 * min(1.0, distance / 20)
        self.camera.lookAt(self.player.x, self.player.y, foot_height + look_height)
        for node, bounds in zip(self.camera_obstacle_nodes, self.camera_obstacles):
            obstructs = any(segment_box_hit((self.player.x, self.player.y, foot_height + height),
                                           position, bounds, margin=0) is not None
                           for height in (0.3, 1.5, 2.8))
            if obstructs:
                node.setTransparency(TransparencyAttrib.MAlpha)
                node.setAlphaScale(0.15)
                node.setDepthWrite(False)
            else:
                node.clearTransparency()
                node.clearColorScale()
                node.setDepthWrite(True)


    def navigate_menu(self, pad, elapsed):
        actions = {action: bool(pad.get(action)) or self.keys.get(key, False)
                   for action, key in [('up', 'arrow_up'), ('down', 'arrow_down'),
                                       ('left', 'arrow_left'), ('right', 'arrow_right'), ('confirm', 'enter')]}
        fresh = {action for action, pressed in actions.items()
                 if pressed and not self.menu_previous_actions.get(action)}
        self.menu_previous_actions = actions
        if self.mode in ("playing", "capture", "victory") or self.pending_gamepad_action or self.local_binding or self.menu_input_block > 0:
            return
        buttons = [item for item in self.ui if isinstance(item, DirectButton) and item['state'] != 'disabled']
        if not buttons:
            return
        if self.menu_focus not in buttons:
            self.menu_focus = buttons[0]
        self.menu_repeat_time = max(0.0, self.menu_repeat_time - elapsed)
        directions = {'up': (0, 1), 'down': (0, -1), 'left': (-1, 0), 'right': (1, 0)}
        for action, (dx, dz) in directions.items():
            if action not in fresh and not (actions[action] and self.menu_repeat_time == 0):
                continue
            self.menu_repeat_time = 0.30 if action in fresh else 0.14
            origin = self.menu_focus.getPos()
            candidates = []
            for item in buttons:
                delta = item.getPos() - origin
                forward = delta.x * dx + delta.z * dz
                if forward > 0.01:
                    sideways = abs(delta.x * dz - delta.z * dx)
                    candidates.append((sideways * 4 + forward, item))
            if candidates:
                self.menu_focus.clearColorScale()
                self.menu_focus = min(candidates, key=lambda item: item[0])[1]
                self.menu_focus.setColorScale(1.15, 1.20, 1.25, 1)
            break
        if 'confirm' in fresh:
            command = self.menu_focus['command']
            if command:
                command(*self.menu_focus['extraArgs'])

    def update(self, task):
        elapsed = max(0.0, self.clock.getDt())
        dt = min(elapsed, 0.1)
        self.camera_switch_cooldown = max(0.0, self.camera_switch_cooldown - elapsed)
        self.menu_input_block = max(0.0, self.menu_input_block - elapsed)
        pad, pad_edges = self.poll_gamepad(elapsed)
        if "menu" in (pad_edges | self.second_gamepad_edges) and self.mode in ("playing", "capture", "victory"):
            self.main_menu()
        menu_pad = {action: pad.get(action, False) or self.second_gamepad_previous.get(action, False) for action in GAMEPAD_ACTIONS}
        self.navigate_menu(menu_pad, elapsed)
        if self.mode == "capture":
            self.update_capture(dt, pad, self.second_gamepad_previous)
            return task.cont
        if self.mode in ("playing", "victory"):
            if self.mode == "playing":
                self.player.advance_match_time(elapsed)
                result = self.encounter.match_result(self.player)
                if result:
                    self.finish_match(result)
                    return task.cont
            pressed = lambda *names: any(self.keys.get(name, False) for name in names)
            turn = (int(pad.get("look_right", False)) - int(pad.get("look_left", False))) * 120 * dt
            if self.camera_mode == "first_person":
                self.fps_heading = (self.fps_heading + turn) % 360
            else:
                self.follow_heading = (self.follow_heading + turn) % 360
            if "jump" in pad_edges:
                self.jump()
            if "attack" in pad_edges:
                self.attack()
            pad_right, pad_left = pad.get("right", False), pad.get("left", False)
            dx = int(pressed("d", "arrow_right") or pad_right) - int(pressed("a", "arrow_left") or pad_left)
            dy = int(pressed("w", "arrow_up") or pad.get("up", False)) - int(pressed("s", "arrow_down") or pad.get("down", False))
            if self.camera_mode == "first_person" or self.third_orbit_drag:
                self.update_mouse_look()
                if self.third_orbit_drag and self.camera_mode == "third_person":
                    self.follow_heading = self.fps_heading
            dx, dy = relative_movement(dx, dy, self.view_heading())
            update_player_actions(self.player, dt)
            old_x, old_y = self.player.x, self.player.y
            self.player.move(dx, dy, pressed("shift") or pad.get("run", False), dt)
            if self.camera_mode == "first_person":
                self.player.direction = facing_direction(self.fps_heading)
            move_on_terrain(self.player, old_x, old_y, self.encounter.enemies)
            self.encounter.update(self.player, dt)
            if self.encounter.restart_requested:
                self.new_game(difficulty=self.player.difficulty)
                self.encounter.message_time = 3.0
                return task.cont
            self.update_character()
            self.update_enemies()
            self.update_coins(dt)
            self.update_hud()
            self.minimap_timer += dt
            if self.minimap_timer >= 0.2:
                self.update_minimap()
                self.minimap_timer = 0.0
            ground = player_ground_height(self.player.x, self.player.y)
            foot_height = ground + self.player.z
            self.sky.setPos(self.player.x, self.player.y, ground)
            self.update_camera(dt)
            self.save_timer += dt
            if self.save_timer >= 5:
                self.save()
                self.save_timer = 0
        return task.cont

    def userExit(self):
        self.set_mouse_capture(False)
        if self.mode in ("playing", "victory"):
            self.save()
        if self.music:
            self.music.stop()
        super().userExit()
