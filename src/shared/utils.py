import orjson


def load_json(path: str) -> dict:
    with open(path, "rb") as f:
        return orjson.loads(f.read())


def save_json(path: str, data: dict) -> None:
    with open(path, "wb") as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
