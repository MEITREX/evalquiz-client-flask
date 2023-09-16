from pathlib import Path
from typing import Optional
from grpclib.client import Channel
from evalquiz_proto.shared.generated import (
    InternalConfig,
    PipelineServerStub,
    PipelineStatus,
)


class PipelineClient:
    def __init__(self) -> None:
        self.channel = Channel(host="127.0.0.1", port=50051)
        self.service = PipelineServerStub(self.channel)

    def __del__(self) -> None:
        self.channel.close()

    async def iterate_config(self, internal_config: InternalConfig) -> InternalConfig:
        last_pipeline_status: Optional[PipelineStatus] = None
        async for pipeline_status in self.service.iterate_config(InternalConfig()):
            print(pipeline_status)
            last_pipeline_status = pipeline_status
        return last_pipeline_status
