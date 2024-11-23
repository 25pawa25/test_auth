import uvicorn
from core.config import settings
from management.base.base_command import BaseCommand


class Command(BaseCommand):
    help: str = "Run restapi"

    def add_arguments(self):
        self.parser.add_argument("--host", default=settings.project.api_host)
        self.parser.add_argument("--port", default=settings.project.api_port)

    def execute(self):
        uvicorn.run("core.app:app", port=self.args.port, host=self.args.host, reload=True)
