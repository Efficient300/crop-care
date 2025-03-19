import json
from pathlib import Path
import aiofiles

class JSONDatabase:

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True) 
        if not self.file_path.exists():
            self.file_path.write_text("{}")

    async def read(self) -> dict:
        try:
            async with aiofiles.open(self.file_path, mode='r') as f:
                content = await f.read()
                return json.loads(content) if content else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    async def write(self, data: dict):
        async with aiofiles.open(self.file_path, mode='w') as f:
            await f.write(json.dumps(data, indent=4))

    async def exists(self, key: str) -> bool:
        data = await self.read()
        return key in data

    async def get(self, key: str):
        data = await self.read()
        return data.get(key)

    async def add(self, key: str, value):
        data = await self.read()
        data[key] = value
        await self.write(data)