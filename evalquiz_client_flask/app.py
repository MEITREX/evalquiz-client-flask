import asyncio
import os
from pathlib import Path
from flask import redirect, render_template, Flask, request, flash, url_for
from flask.typing import ResponseReturnValue
from evalquiz_client_flask.forms import InternalConfigForm
from werkzeug.utils import secure_filename

from evalquiz_client_flask.material_client import MaterialClient
from evalquiz_client_flask.pipeline_client import PipelineClient
from evalquiz_proto.shared.exceptions import MimetypeNotDetectedException
from evalquiz_proto.shared.generated import Metadata
from evalquiz_proto.shared.mimetype_resolver import MimetypeResolver

app = Flask(__name__)

material_client = MaterialClient()


@app.route("/")
async def index() -> ResponseReturnValue:
    material_hash_name_pairs = await material_client.get_material_hash_name_pairs()
    return render_template(
        "index.html",
        form=InternalConfigForm(),
        material_hash_name_pairs=material_hash_name_pairs,
    )


@app.route("/upload_material", methods=["GET", "POST"])
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


@app.route("/iterate_config", methods=["GET", "POST"])
def register() -> ResponseReturnValue:
    form = InternalConfigForm(request.form) or InternalConfigForm()
    if request.method == "POST" and form.validate():
        # Do something with form information.
        flash("Thanks for registering")
        # Update form
    return render_template("index.html", form=form)
