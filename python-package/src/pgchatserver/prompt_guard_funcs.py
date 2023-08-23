import json
from typing import Dict, Union

import promptguard as pg


def sanitize(
    input: Union[str, Dict[str, str]]
) -> Dict[str, Union[str, Dict[str, str]]]:
    """
    santize input string or dict of strings

    Parameters
    ----------
    input : Union[str, Dict[str, str]]
        input string or dict of strings

    Returns
    -------
    Dict[str, Union[str, Dict[str, str]]]
        sanitized input string or dict of strings and the secure context
        as a dict following the format:
        {
            "sanitized_input": <sanitized input string or dict of strings>,
            "secure_context": <secure context>
        }
    """
    if isinstance(input, str):
        sanitize_response: pg.SanitizeResponse = pg.sanitize(input)
        return {
            "sanitized_input": sanitize_response.sanitized_text,
            "secure_context": sanitize_response.secure_context,
        }

    if isinstance(input, dict):
        values = list()
        for key in input:
            values.append(input[key])
        input_value_str = json.dumps(values, ensure_ascii=False)
        sanitize_values_response: pg.SanitizeResponse = pg.sanitize(
            input_value_str
        )
        sanitized_input_values = json.loads(
            sanitize_values_response.sanitized_text
        )
        idx = 0
        sanitized_input = dict()
        for key in input:
            sanitized_input[key] = sanitized_input_values[idx]
            idx += 1
        return {
            "sanitized_input": sanitized_input,
            "secure_context": sanitize_values_response.secure_context,
        }

    raise ValueError(f"Unexpected input type {type(input)}")


def desanitize(sanitized_text: str, secure_context: bytes) -> str:
    """
    desanitize sanitized text

    Parameters
    ----------
    sanitized_text : str
        sanitized text
    secure_context : bytes
        secure context

    Returns
    -------
    str
    """
    desanitize_response: pg.DesanitizeResponse = pg.desanitize(
        sanitized_text, secure_context
    )
    return desanitize_response.desanitized_text
