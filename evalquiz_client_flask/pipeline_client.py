from typing import Optional
from grpclib.client import Channel
from evalquiz_proto.shared.generated import (
    InternalConfig,
    PipelineServerStub,
    PipelineStatus,
)


class PipelineClient:
    def __init__(self, host: str = "pipeline-server", port: int = 50051) -> None:
        self.host = host
        self.port = port

    async def iterate_config(
        self, internal_config: InternalConfig
    ) -> Optional[PipelineStatus]:
        channel = Channel(host=self.host, port=self.port)
        service = PipelineServerStub(channel)
        last_pipeline_status: Optional[PipelineStatus] = None
        async for pipeline_status in service.iterate_config(internal_config):
            print(pipeline_status, flush=True)
            last_pipeline_status = pipeline_status
        channel.close()
        return last_pipeline_status
