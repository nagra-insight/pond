class InvalidVersionName(Exception):

    def __init__(self, version_name: str):
        super().__init__(f'Invalid version name: {version_name}.')


class ArtifactHasNoVersion(Exception):

    def __init__(self, artifact_location: str):
        super().__init__(f'The artifact at "{artifact_location}" has no versions.')


class ArtifactVersionDoesNotExist(Exception):

    def __init__(self, artifact_location: str, version_name: str):
        super().__init__(f'The artifact at "{artifact_location}" has no version "{version_name}".')


class ArtifactVersionAlreadyExists(Exception):

    def __init__(self, version_location: str):
        super().__init__(f'Version "{version_location}" already exists.')


class ArtifactVersionIsLocked(Exception):

    def __init__(self, version_location: str):
        super().__init__(
            f'Cannot create the new artifact version "{version_location}" because it is locked.')
