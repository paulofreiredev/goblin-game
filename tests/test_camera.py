import pytest
from game.camera import clear_view, follow_heading, segment_box_hit, third_person_position


def flat_ground(x, y):
    return 0.0


def test_segment_box_contact_parallel_miss_and_inside():
    box = ((-1, -11, 0), (1, -9, 10))
    assert segment_box_hit((0, 0, 1.5), (0, -20, 7), box, margin=0) == pytest.approx(0.45)
    assert segment_box_hit((4, 0, 1.5), (4, -20, 7), box) is None
    assert segment_box_hit((0, -10, 2), (0, -20, 7), box) == 0


def test_camera_keeps_normal_distance_in_clear_field():
    assert third_person_position((0, 0, 0), (0, -20, 7), [], flat_ground) == pytest.approx((0, -20, 7))


def test_camera_goes_around_tree_without_hovering_over_player():
    box = ((-1, -11, 0), (1, -9, 10))
    position = third_person_position((0, 0, 0), (0, -20, 7), [box], flat_ground)
    assert clear_view((0, 0, 1.5), position, [box], flat_ground)
    assert position[2] == 7
    assert position[0] ** 2 + position[1] ** 2 == pytest.approx(400)
    hill = lambda x, y: 8 if y < -9 else 0
    position = third_person_position((0, 0, 0), (0, -20, 7), [], hill)
    assert clear_view((0, 0, 1.5), position, [], hill)
    assert position[2] >= hill(*position[:2]) + 0.5


def test_closed_space_keeps_camera_behind_and_fall_target():
    box = ((-30, -30, -10), (30, 30, 20))
    assert third_person_position((0, 0, 0), (0, -20, 7), [box], flat_ground) == pytest.approx((0, -20, 7))
    assert third_person_position((0, 0, 3), (0, -20, 10), [], flat_ground)[2] == 10


def test_follow_heading_wraps_and_is_time_based():
    assert follow_heading(179, -179, 0.1) > 179
    split = 0
    for _ in range(10):
        split = follow_heading(split, 90, 0.1)
    assert split == pytest.approx(follow_heading(0, 90, 1))


def test_fps_relative_movement_and_facing():
    from game.camera import facing_direction, relative_movement, view_direction
    assert relative_movement(0, 1, 90) == pytest.approx((1, 0))
    assert relative_movement(1, 0, 90) == pytest.approx((0, -1))
    assert facing_direction(0) == 2 and facing_direction(90) == 4
    assert view_direction(90, 0) == pytest.approx((1, 0, 0))
    assert view_direction(0, 75)[2] > 0.9
