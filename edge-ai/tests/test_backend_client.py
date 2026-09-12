from communication.backend_client import BackendClient


def test_offline_buffer_flush_preserves_order():
    client = BackendClient(base_url="http://example.test", retry_attempts=1)
    client._buffer_offline("/first", {"id": 1})
    client._buffer_offline("/second", {"id": 2})
    sent = []

    def fake_post(endpoint, payload, _is_retry=False):
        sent.append((endpoint, payload["id"], _is_retry))
        return True, {}

    client._post = fake_post

    assert client.flush_offline_buffer() == 2
    assert sent == [
        ("/first", 1, True),
        ("/second", 2, True),
    ]
    assert client.offline_buffer_size() == 0


def test_offline_buffer_requeues_failed_events():
    client = BackendClient(base_url="http://example.test", retry_attempts=1)
    client._buffer_offline("/first", {"id": 1})
    client._post = lambda endpoint, payload, _is_retry=False: (False, None)

    assert client.flush_offline_buffer() == 0
    assert client.offline_buffer_size() == 1