import pytest
from game.camera import segment_box_hit, third_person_position


def flat_ground(x, y):
    return 0.0


def test_segment_box_contact_parallel_miss_and_inside():
    box = ((-1, -11, 0), (1, -9, 10))
    assert segment_box_hit((0, 0, 1.5), (0, -20, 7), box, margin=0) == pytest.approx(0.45)
    assert segment_box_hit((4, 0, 1.5), (4, -20, 7), box) is None
    assert segment_box_hit((0, -10, 2), (0, -20, 7), box) == 0


def test_camera_keeps_normal_distance_in_clear_field():
    assert third_person_position((0, 0, 0), (0, -20, 7), [], flat_ground) == (0, -20, 7)


def test_camera_shortens_before_tree_and_stays_above_terrain():
    box = ((-1, -11, 0), (1, -9, 10))
    position = third_person_position((0, 0, 0), (0, -20, 7), [box], flat_ground)
    assert -9 < position[1] < -4
    assert segment_box_hit((0, 0, 1.5), position, box) is None
    hill = lambda x, y: 8 if y < -9 else 0
    position = third_person_position((0, 0, 0), (0, -20, 7), [], hill)
    assert position[1] > -9 and position[2] >= hill(*position[:2]) + 0.5


def test_close_obstruction_fallback_and_fall_target():
    box = ((-1, -3, 0), (1, -1, 10))
    assert third_person_position((0, 0, 0), (0, -20, 7), [box], flat_ground) == (0, -4, 7)
    assert third_person_position((0, 0, 3), (0, -20, 10), [], flat_ground)[2] == 10
