import pytest
from io import StringIO
from unittest.mock import patch
from translator import parse_config

def test_parse_invalid_config():
    config_text = """
    valid_key = 123,
    invalid_key = q(InvalidValue)  # invalid value with uppercase letters
    """

    expected_output = {
        'valid_key': 123  # invalid_key должен быть проигнорирован
    }

    parsed_data = parse_config(config_text)
    
    assert parsed_data == expected_output

def test_parse_numbers_and_booleans():
    config_text = """
    var host q(localhost)
    {
        enable_feature = 1,
        disable_feature = 0,
        port = 8080
    }
    """
    
    expected_output = {
        'enable_feature': True,
        'disable_feature': False,
        'port': 8080
    }
    
    parsed_data = parse_config(config_text)
    
    assert parsed_data == expected_output


def test_parse_with_comments():
    config_text = """
    # This is a comment
    var host q(localhost)
    /* This is a block comment */
    {
        server_name = $[host],
        server_port = 8080
    }
    mode = 1
    """

    expected_output = {
        'server_name': 'localhost',
        'server_port': 8080,
        'mode': 1
    }
    
    parsed_data = parse_config(config_text)

    assert parsed_data == expected_output

