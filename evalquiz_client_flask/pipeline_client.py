from typing import Optional
import betterproto
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

    async def iterate_config(self, internal_config: InternalConfig) -> InternalConfig:
        channel = Channel(host=self.host, port=self.port)
        service = PipelineServerStub(channel)
        last_pipeline_status: Optional[PipelineStatus] = None
        async for pipeline_status in service.iterate_config(internal_config):
            print(pipeline_status)
            last_pipeline_status = pipeline_status
        channel.close()
        if last_pipeline_status is None or last_pipeline_status.result is None:
            raise ValueError(
                "No PipelineStatus was returned from the config iteration or PipelineResult is empty."
            )
        _, result_internal_config = betterproto.which_one_of(
            last_pipeline_status.result, "pipeline_result"
        )
        if result_internal_config is None or not isinstance(
            result_internal_config, InternalConfig
        ):
            raise ValueError("PipelineResult is either empty or not a InternalConfig.")
        return result_internal_config
