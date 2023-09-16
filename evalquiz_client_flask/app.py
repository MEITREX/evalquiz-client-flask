from pathlib import Path
from flask import redirect, Flask, request, url_for
from flask.typing import ResponseReturnValue
from markupsafe import escape
from werkzeug.utils import secure_filename

from evalquiz_client_flask.material_client import MaterialClient
from evalquiz_client_flask.pipeline_client import PipelineClient
from evalquiz_proto.shared.exceptions import MimetypeNotDetectedException
from evalquiz_proto.shared.generated import InternalConfig, Metadata
from evalquiz_proto.shared.mimetype_resolver import MimetypeResolver

app = Flask(__name__)
material_client = MaterialClient()
pipeline_client = PipelineClient()


@app.route("/api/get_material_hash_name_pairs")
async def get_material_hash_name_pairs() -> ResponseReturnValue:
    return await material_client.get_material_hash_name_pairs()


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
    return redirect(url_for("index"))


app.route("/api/delete_config/<hash_value>")
async def delete_material() -> None:
    await material_client.delete_material(hash_value)


@app.route("/api/iterate_config", methods=["POST"])
async def iterate_config() -> ResponseReturnValue:
    internal_config = InternalConfig()
    iterated_internal_config = await pipeline_client.iterate_config(internal_config)
    iterated_internal_config_json = iterated_internal_config.to_json()
    return iterated_internal_config_json
