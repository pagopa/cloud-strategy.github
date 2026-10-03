"""Defective SQS consumer: one bad record fails and replays the whole batch."""

import json


def process_message(message: dict) -> None:
    if "order_id" not in message:
        raise ValueError("missing order_id")


def handler(event: dict, context: object) -> dict:
    for record in event["Records"]:
        message = json.loads(record["body"])
        process_message(message)
    return {"batchItemFailures": []}
