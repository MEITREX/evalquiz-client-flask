from pathlib import Path
from grpclib.client import Channel
from evalquiz_proto.shared.generated import (
    Empty,
    MaterialServerStub,
    MaterialUploadData,
    Metadata,
    String,
)
import asyncio


class MaterialClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 50051) -> None:
        self.host = host
        self.port = port

    async def upload_material(
        self,
        metadata: Metadata,
        local_path: Path,
        content_partition_size: int = 5 * 10**8,
    ) -> None:
        channel = Channel(host=self.host, port=self.port)
        service = MaterialServerStub(channel)
        material_upload_data = [MaterialUploadData(metadata=metadata)]
        with open(local_path, "rb") as local_file:
            while content_partition := local_file.read(content_partition_size):
                material_upload_data.append(MaterialUploadData(data=content_partition))
        await service.upload_material(material_upload_data)
        channel.close()

    async def get_material_hash_name_pairs(self) -> list[tuple[str, str]]:
        channel = Channel(host=self.host, port=self.port)
        service = MaterialServerStub(channel)
        hashes = await service.get_material_hashes(Empty())
        hash_name_pairs: list[tuple[str, str]] = []
        for hash in hashes.values:
            name = await service.get_material_name(String(hash))
            hash_name_pairs.append((hash, name.value))
        channel.close()
        return hash_name_pairs


async def main() -> None:
    material_client = MaterialClient()
    await material_client.upload_material(
        Metadata("text/markdown"), Path("./compose.yaml")
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
