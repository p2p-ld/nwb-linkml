import pytest
import yaml

from nwb_linkml.io.yaml import yaml_peek

@pytest.fixture()
def yaml_file(tmp_path):
    data = {
        'key1': 'val1',
        'key2': 'val2',
        'key3': {
            'key1': 'val3',
            'key4': 'val4'
        }
    }
    out_file = tmp_path / 'test.yaml'
    with open(out_file, 'w') as yfile:
        yaml.dump(data, yfile)

    yield out_file

    out_file.unlink()



@pytest.mark.parametrize(
    'key,expected,root,first',
    [
        ('key1', 'val1', True, True),
        ('key1', 'val1', False, True),
        ('key1', ['val1'], True, False),
        ('key1', ['val1', 'val3'], False, False),
        ('key2', 'val2', True, True),
        ('key3', False, True, True),
        ('key4', False, True, True),
        ('key4', 'val4', False, True)
    ]
)
def test_peek_yaml(key, expected, root, first, yaml_file):
    if not expected:
        with pytest.raises(KeyError):
            _ = yaml_peek(key, yaml_file, root=root, first=first)
    else:
        assert yaml_peek(key, yaml_file, root=root, first=first)
