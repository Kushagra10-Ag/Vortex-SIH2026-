from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_migration_chain_has_single_head_and_telemetry_revision():
    root = Path(__file__).resolve().parents[1]
    config = Config(str(root / "migrations" / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_heads() == ["7d4e1d2c9f10"]
    revisions = {revision.revision for revision in scripts.walk_revisions()}
    assert "13083c76a3b5" in revisions
    assert "7d4e1d2c9f10" in revisions