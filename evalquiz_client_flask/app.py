import json
from pathlib import Path
from flask import Flask, request
from flask.typing import ResponseReturnValue
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from betterproto import Casing

from evalquiz_client_flask.material_client import MaterialClient
from evalquiz_client_flask.pipeline_client import PipelineClient
from evalquiz_proto.shared.exceptions import MimetypeNotDetectedException
from evalquiz_proto.shared.generated import InternalConfig, Metadata
from evalquiz_proto.shared.mimetype_resolver import MimetypeResolver

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

material_client = MaterialClient()
pipeline_client = PipelineClient()


@app.route("/api/get_material_name_hash_pairs")
async def get_material_name_hash_pairs() -> ResponseReturnValue:
    return await material_client.get_material_name_hash_pairs()


@app.route("/api/upload_material", methods=["POST"])
async def upload_material() -> None:
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


@app.route("/api/delete_material/<hash>")
async def delete_material(hash: str) -> None:
    await material_client.delete_material(hash)


@app.route("/api/iterate_config", methods=["POST"])
async def iterate_config() -> ResponseReturnValue:
    config = request.json["config"]
    config_json = json.dumps(config)
    internal_config = InternalConfig().from_json(config_json)
    material_server_url = "evalquiz-material-server-app-1" + ":" + str(material_client.port)
    internal_config.material_server_urls.append(material_server_url)
    print(internal_config)
    iterated_internal_config = await pipeline_client.iterate_config(internal_config)
    iterated_internal_config_json = iterated_internal_config.to_json(include_default_values=True, casing=Casing.SNAKE)
    return iterated_internal_config_json