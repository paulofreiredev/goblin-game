from types import SimpleNamespace
from game.gamepad import DEFAULT_BINDINGS, active_inputs, load_bindings, mapped_actions, read_device


def fake_gamepad():
    device = SimpleNamespace(name='Controle USB de teste', connected=True,
                             buttons=[SimpleNamespace(pressed=False) for _ in range(8)],
                             axes=[SimpleNamespace(value=0.0) for _ in range(2)], poll=lambda: None)
    return device


def test_axes_buttons_dead_zone_and_disconnection():
    assert active_inputs([True, False], [0.2, -1]) == {'button:0', 'axis:1:-'}
    actions = mapped_actions(active_inputs([True, False, True], [0, 1]), DEFAULT_BINDINGS)
    assert actions['up'] and actions['jump'] and actions['run']
    assert not actions['attack']
    device = fake_gamepad()
    device.buttons[0].pressed = True
    assert read_device(device) == {'button:0'}
    device.connected = False
    assert read_device(device) == read_device(None) == set()


def test_invalid_bindings_default_and_saved_bindings_round_trip():
    for invalid in [None, [], {}, {'jump': 'wrong'}]:
        assert load_bindings({'gamepad_bindings': invalid}) == DEFAULT_BINDINGS
    bindings = DEFAULT_BINDINGS.copy()
    bindings['jump'] = 'button:6'
    assert load_bindings({'gamepad_bindings': bindings}) == bindings
    bindings['attack'] = bindings['jump']
    assert load_bindings({'gamepad_bindings': bindings}) == DEFAULT_BINDINGS


def test_replacement_swaps_occupied_buttons_axes_and_persists():
    from game.gamepad import replace_binding
    bindings = replace_binding(DEFAULT_BINDINGS, 'attack', 'button:0')
    assert bindings['attack'] == 'button:0'
    assert bindings['jump'] == bindings['confirm'] == 'button:1'
    assert load_bindings({'gamepad_bindings': bindings}) == bindings
    bindings = replace_binding(bindings, 'attack', 'button:6')
    assert bindings['attack'] == 'button:6'
    assert bindings['jump'] == 'button:1'
    bindings = replace_binding(bindings, 'up', bindings['down'])
    assert bindings['up'] == 'axis:1:-' and bindings['down'] == 'axis:1:+'
    assert load_bindings({'gamepad_bindings': bindings}) == bindings


def test_every_occupied_mapping_can_be_replaced_including_start_and_b():
    from game.gamepad import replace_binding
    for action in DEFAULT_BINDINGS:
        for binding in DEFAULT_BINDINGS.values():
            updated = replace_binding(DEFAULT_BINDINGS, action, binding)
            assert updated[action] == binding
            assert load_bindings({'gamepad_bindings': updated}) == updated
    assert DEFAULT_BINDINGS['attack'] == 'button:1'


def test_device_identity_distinguishes_equal_models_and_native_wrappers():
    from game.gamepad import same_device
    first, second = fake_gamepad(), fake_gamepad()
    second.poll = first.poll
    assert first == second
    assert not same_device(first, second)
    assert same_device(first, first)
    assert not same_device(first, None)
    assert same_device(None, None)
    assert same_device(SimpleNamespace(this=123), SimpleNamespace(this=123))
    assert not same_device(SimpleNamespace(this=123), SimpleNamespace(this=456))
