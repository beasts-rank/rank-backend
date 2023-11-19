from dataclasses import replace, asdict
from json import load, dump, JSONDecodeError
from pathlib import Path
from types import coroutine
from typing import Iterable, Iterator, Any
from functools import partial
from uuid import uuid4, UUID

from exceptions import BeastNotFoundError
from helper import default, debounce
from structures import Config, Beast, BeastMeta


class ConfigManager:
    def __init__(self, config_path: Path):
        self.config: Config = Config()
        self.config_path = config_path

    def load(self):
        if not self.config_path.is_file():
            self.write()
            return self.config

        config = self.config.to_json()
        try:
            with self.config_path.open('r', encoding='u8') as fp:
                config = load(fp)
        except JSONDecodeError:
            self.config_path.rename(self.config_path.with_suffix('.json.bak'))
            self.write()

        self.config = Config.from_json(config)

        return self.config

    def write(self):
        if not self.config_path.is_file():
            self.config_path.unlink(True)

        with self.config_path.open('w', encoding='u8') as fp:
            dump(self.config, fp, default=default)

    async def write_async(self):
        if not self.config_path.is_file():
            self.config_path.unlink(True)

        with self.config_path.open('w', encoding='u8') as fp:
            dump(self.config, fp, default=default)

    @debounce(5, lambda: coroutine(lambda: None))
    async def debounced_write_async(self):
        await self.write_async()


cfg = ConfigManager(Path("./instance/cfg.json"))


class BeastsCaller:
    def __init__(self, cm: ConfigManager = cfg):
        self.cm = cm

    @property
    def cfg(self):
        return self.cm.config

    def _get_from_to(self, start: int, end: int):
        values = tuple(self.cfg.beasts.values())
        for i in range(start, end):
            yield values[i]
        return None

    def paged_beasts(self, p: int, cnt: int = 8) -> Iterator[Beast]:
        if cnt >= self.cfg.max_pagesize:
            cnt = self.cfg.max_pagesize

        return iter(partial(self._get_from_to, p * cnt, (p + 1) * cnt), None)

    def get_beast(self, uuid: UUID):
        if uuid not in self.cfg.beasts:
            raise BeastNotFoundError(uuid)

        return self.cfg.beasts[uuid]

    def add_beast(self, beast: Beast, uuid: UUID = None):
        if not uuid:
            uuid = uuid4()

        beast.uuid = uuid
        self.cfg.beasts[uuid] = beast

        return beast

    def patch_beast(self, uuid: UUID, meta: dict[str, Any]):
        if uuid not in self.cfg.beasts:
            raise BeastNotFoundError(uuid)

        beast = self.cfg.beasts[uuid]

        tmp = asdict(beast.meta)
        tmp.update(meta)
        beast.meta = BeastMeta.from_json(tmp)

        return beast


bc = BeastsCaller(cfg)
