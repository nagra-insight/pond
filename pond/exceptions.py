class InvalidVersionName(Exception):
    def __init__(self, version_name: str):
        super().__init__(f'Invalid version name: {version_name}.')
