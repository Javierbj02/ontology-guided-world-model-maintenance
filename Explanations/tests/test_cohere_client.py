import pytest

from benchmark.cohere_client import (
    CohereClientError,
    build_generation_messages,
    extract_text_from_cohere_response,
    extract_usage_metrics,
)


class FakeContentItem:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeResponse:
    def __init__(self, content):
        self.message = FakeMessage(content)
        
        
class FakeUsageResponse:
    def __init__(self):
        self.usage = {
            "input_tokens": 123,
            "output_tokens": 45,
            "total_tokens": 168,
        }


def test_build_generation_messages():
    messages = build_generation_messages("Generate candidates as JSON.")

    assert messages == [
        {"role": "user", "content": "Generate candidates as JSON."}
    ]


def test_build_generation_messages_rejects_empty_prompt():
    with pytest.raises(CohereClientError):
        build_generation_messages("   ")


def test_extract_text_from_cohere_response():
    response = FakeResponse([FakeContentItem('{"case_id":"CG1","condition":"PC1","candidates":[1]}')])
    text = extract_text_from_cohere_response(response)

    assert text == '{"case_id":"CG1","condition":"PC1","candidates":[1]}'


def test_extract_text_from_cohere_response_rejects_empty_content():
    response = FakeResponse([])

    with pytest.raises(CohereClientError):
        extract_text_from_cohere_response(response)
        


def test_extract_usage_metrics():
    response = FakeUsageResponse()
    input_tokens, output_tokens, total_tokens = extract_usage_metrics(response)

    assert input_tokens == 123
    assert output_tokens == 45
    assert total_tokens == 168
