from . import create_app, db
from .models import Task

app = create_app()


@app.shell_context_processor
def make_shell_context():
    app.app_context().push()
    return dict(db=db, Task=Task)
