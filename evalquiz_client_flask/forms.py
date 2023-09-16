from wtforms import (
    Form,
    StringField,
    FileField,
    validators,
    FieldList,
    FormField,
    SelectField,
    BooleanField,
)

from evalquiz_proto.shared.generated import (
    EducationalObjective,
    QuestionType,
    Relationship,
)

supported_upload_types = (
    "md|pptx|"
    + "bibtex|biblatex|commonmark|commonmark_x|creole|csljson|csv|tsv|docbook|docx|dokuwiki|endnotexml|epub|fb2|gfm|haddock|html|ipynb|jats|jira|json|latex|markdown|markdown_mmd|markdown_phpextra|markdown_strict|mediawiki|man|muse|native|odt|opml|org|ris|rtf|rst|t2t|textile|tikiwiki|twiki|typst|vimwiki"
)

question_types = [(question_type, question_type.name) for question_type in QuestionType]

educational_objectives = [
    (educational_objective, educational_objective.name)
    for educational_objective in EducationalObjective
]

relationships = [(relationship, relationship.name) for relationship in Relationship]


class MaterialUploadForm(Form):
    reference = StringField("reference")
    file = FileField("data")


class BatchForm(Form):
    def __init__(self, lecture_materials: list[tuple[str]]):
        self.lecture_materials = SelectField(
            "Lecture Materials", choices=lecture_materials
        )
        self.question_to_generate
        self.capabilites = FieldList(FormField(CapabilityForm))


class InternalConfigForm(Form):
    batches = FieldList(FormField(BatchForm))


class QuestionForm(Form):
    question_type = SelectField("Question Type", choices=question_types)
    generation_result = StringField("Generation Result")
    regenerate = BooleanField("Regenerate Question")


class CapabilityForm(Form):
    keywords = FieldList(StringField("Keywords", validators.regexp("^[a-zA-Z0-9_]+$")))
    educational_objective = SelectField(
        "Eductional Objectives", choices=educational_objectives
    )
    relationship = SelectField("Relationships", choices=relationships)
