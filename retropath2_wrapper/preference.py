import datetime
import tempfile


class Preference(object):
    def __init__(self, *args, **kwargs) -> None:
        self.path = kwargs.get("path", tempfile.NamedTemporaryFile(suffix=".epf").name)
        self.rdkit_timeout_minutes = kwargs.get("rdkit_timeout_minutes")

    def is_init(self) -> bool:
        if self.rdkit_timeout_minutes:
            return True
        return False

    def to_file(self) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)
        with open(self.path, "w") as fod:
            fod.write("#")
            fod.write(now.strftime("%a %b %d %H:%M:%S %Z %Y"))
            fod.write("\n")
            fod.write("\\!/=")
            fod.write("\n")
            if self.rdkit_timeout_minutes:
                fod.write("/instance/org.rdkit.knime.nodes/mcsAggregation.timeout=")
                fod.write(str(int(self.rdkit_timeout_minutes) * 60))
                fod.write("\n")
