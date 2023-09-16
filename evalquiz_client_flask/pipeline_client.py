from pathlib import Path
from grpclib.client import Channel
from evalquiz_proto.shared.generated import (
    InternalConfig,
    PipelineServerStub,
)


class PipelineClient:
    def __init__(self) -> None:
        self.channel = Channel(host="127.0.0.1", port=50051)
        self.service = PipelineServerStub(self.channel)

    def __del__(self) -> None:
        self.channel.close()

    async def iterate_config(self, internal_config: InternalConfig) -> None:
        async for pipeline_status in self.service.iterate_config(InternalConfig()):
            print(pipeline_status)
