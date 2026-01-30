from firebase_admin import messaging


def fcm_push(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> messaging.BatchResponse | None:

    if not tokens:
        return None

    # FCM requires string values for data payloads
    payload_data: dict[str, str] | None = (
        {k: str(v) for k, v in data.items()} if data else None
    )

    msg = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=payload_data,
        tokens=list(tokens),
    )

    return messaging.send_each_for_multicast(msg)


def fcm_push_batched(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
    batch_size: int = 500,
) -> list[messaging.BatchResponse]:

    results = []

    if not tokens:
        return []

    batch_size = max(1, min(batch_size, 500))

    for i in range(0, len(tokens), batch_size):
        batch_tokens = tokens[i : i + batch_size]
        resp = fcm_push(batch_tokens, title, body, data)
        if resp is not None:
            results.append(resp)

    return results
