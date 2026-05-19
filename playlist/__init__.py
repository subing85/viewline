import resources


class Projects(object):
    """Project data provider."""

    @classmethod
    def get(cls):
        """
        Return project data.

        Notes:
            This is example data only. Replace this implementation
            with database, API, or ShotGrid/FTrack queries.
        """

        result = resources.getPreset("projects")

        return result


class Versions(object):
    """Version data provider."""

    @classmethod
    def get(cls, project):
        """
        Return versions data.

        Notes:
            This is example data only. Replace this implementation
            with database, API, or ShotGrid/FTrack queries.
        """

        versions = resources.getPreset("versions")

        project_versions = list(
            filter(lambda x: x.get("project") and x["project"]["id"] == project["id"], versions)
        )

        result = sorted(project_versions, key=lambda k: (k["created_at"]), reverse=True)

        return result
