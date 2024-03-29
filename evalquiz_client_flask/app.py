import json
from pathlib import Path
from flask import Flask, request
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from werkzeug.utils import secure_filename
from betterproto import Casing

from evalquiz_client_flask.material_client import MaterialClient
from evalquiz_client_flask.pipeline_client import PipelineClient
from evalquiz_proto.shared.exceptions import MimetypeNotDetectedException
from evalquiz_proto.shared.generated import InternalConfig, Metadata
from evalquiz_proto.shared.mimetype_resolver import MimetypeResolver

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

if __name__ == "__main__":
    app.run()

material_client = MaterialClient()
pipeline_client = PipelineClient()


@app.route("/api/get_material_name_hash_pairs")
async def get_material_name_hash_pairs() -> ResponseReturnValue:
    return await material_client.get_material_name_hash_pairs()


@app.route("/api/upload_material", methods=["POST"])
async def upload_material() -> ResponseReturnValue:
    if request.method == "POST":
        material = request.files["material"]
        if material.filename is not None:
            local_path = f"/tmp/{secure_filename(material.filename)}"
            suffix = Path(local_path).suffix
            mimetype = MimetypeResolver.fixed_guess_type(suffix)
            if mimetype is None:
                raise MimetypeNotDetectedException()
            material.save(local_path)
            name = request.form["name"]
            metadata = Metadata(mimetype, name)
            await material_client.upload_material(metadata, Path(local_path))
    return "Success"


@app.route("/api/delete_material/<hash>")
async def delete_material(hash: str) -> ResponseReturnValue:
    await material_client.delete_material(hash)
    return "Success"


@app.route("/api/iterate_config", methods=["POST"])
async def iterate_config() -> ResponseReturnValue:
    config = request.json["config"]
    config_json = json.dumps(config)
    internal_config = InternalConfig().from_json(config_json)
    internal_config.material_server_urls = _add_material_server_url(
        internal_config.material_server_urls
    )
    pipeline_status = await pipeline_client.iterate_config(internal_config)
    pipeline_status_json = pipeline_status.to_json(casing=Casing.SNAKE)
    return pipeline_status_json


def _add_material_server_url(material_server_urls: list[str]) -> list[str]:
    material_server_url = str(material_client.host)
    if len(material_server_urls) == 0:
        material_server_urls.append(material_server_url)
    else:
        material_server_urls[0] = material_server_url
    return material_server_urls
