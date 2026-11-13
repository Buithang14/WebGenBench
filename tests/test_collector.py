import json
from pathlib import Path
from collection.collector import ArtifactCollector


def test_collector_copies_files_and_calculates_metadata(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".gitkeep").write_text("", encoding="utf-8")
    (workspace / "index.html").write_text("<!DOCTYPE html>\n<html><body>Hello</body></html>\n", encoding="utf-8")
    (workspace / "style.css").write_text("body { color: red; }\n", encoding="utf-8")
    (workspace / "script.js").write_text("console.log('hi');\n", encoding="utf-8")

    out_base = tmp_path / "outputs"
    collector = ArtifactCollector(base_output_dir=out_base)

    meta_input = {
        "ide": "cursor",
        "agent": "cursor_agent",
        "model": "auto",
        "task_id": "T01",
        "condition": "text_only",
        "status": "SUCCESS",
        "duration_seconds": 15.5,
    }

    run_dir = collector.collect_run_artifacts(
        run_id="run_test_001",
        workspace_dir=workspace,
        metadata=meta_input,
    )

    project_dir = run_dir / "project"
    assert project_dir.exists()
    assert (project_dir / "index.html").exists()
    assert (project_dir / "style.css").exists()
    assert (project_dir / "script.js").exists()
    assert not (project_dir / ".gitkeep").exists()

    meta_file = run_dir / "run_metadata.json"
    assert meta_file.exists()

    with open(meta_file, "r", encoding="utf-8") as f:
        saved_meta = json.load(f)

    assert saved_meta["run_id"] == "run_test_001"
    assert saved_meta["ide"] == "cursor"
    assert saved_meta["task_id"] == "T01"
    assert saved_meta["entry_html"] == "index.html"
    assert "index.html" in saved_meta["files"]
    assert "style.css" in saved_meta["files"]
    assert "script.js" in saved_meta["files"]
    assert saved_meta["total_loc"] > 0
    assert len(saved_meta["sha256_hash"]) == 64

