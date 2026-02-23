from typing import Protocol, TypedDict


class ISpriteFrame(TypedDict):
    x: int
    y: int
    w: int
    h: int


class ISpriteSourceSize(TypedDict):
    x: int
    y: int
    w: int
    h: int


class IAtlasEntry(TypedDict):
    filename: str
    frame: ISpriteFrame
    rotated: bool
    trimmed: bool
    sprite_source_size: list[int]
    source_size: list[int]


class IAtlasMeta(TypedDict, total=False):
    scale: float
    sprite_mapping: dict[str, str]
    custom_name: str
    app: str
    version: str
    image: str
    format: str
    size: dict[str, int]


class IAtlasData(TypedDict):
    frames: dict[str, IAtlasEntry]
    meta: IAtlasMeta


class IAtlasConfigEntry(TypedDict, total=False):
    atlas: str
    config: str
    scale: float
    auto_build: bool
    sprites: dict[str, str]
    custom: str


class IAtlasConfig(Protocol):
    def __getitem__(self, key: str) -> IAtlasConfigEntry: ...
    def __contains__(self, key: str) -> bool: ...
    def keys(self): ...
    def items(self): ...
    def values(self): ...
