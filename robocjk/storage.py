from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class ManifestStaticFilesStorageNotStrict(ManifestStaticFilesStorage):
    # manifest_strict = False # not working

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content=content, filename=filename)
        except ValueError:
            return name
