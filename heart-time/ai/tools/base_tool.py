class BaseTool:

    name = ""

    description = ""

    parameters = {}

    def execute(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")