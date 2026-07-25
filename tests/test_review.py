import subprocess

from bcintel import review

KEYS = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "LLM_PROVIDER"]


def test_static_checks(tmp_path):
    pkg = tmp_path / "pkg"
    (pkg / "R").mkdir(parents=True)
    (pkg / "DESCRIPTION").write_text("Package: X\nVersion: 1.0.0\nRemotes: foo/bar\n")
    (pkg / "NAMESPACE").write_text('exportPattern("^[[:alpha:]]+")\n')
    (pkg / "R" / "a.R").write_text("f <- function(x) sapply(x, identity)\n")

    msgs = " ".join(f["msg"] for f in review.static_checks(pkg))
    assert "must start 0.99" in msgs      # bad version
    assert "Remotes" in msgs
    assert "biocViews" in msgs            # missing
    assert "exportPattern" in msgs
    assert "vignettes/" in msgs           # no vignettes dir
    assert "sapply" in msgs


def test_build_comment_first_no_llm(tmp_path, monkeypatch):
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)
    findings = [{"severity": "ERROR", "area": "DESCRIPTION",
                 "msg": "Version is 1.0.0; ...", "fix": "Set 0.99.0"}]
    c = review.build_comment("pkgX", 5, "https://github.com/a/pkgX", "abcdef1234567",
                             findings, "SRC", first=True)
    assert "# Package review — pkgX" in c
    assert "abcdef12" in c                # short sha
    assert "[ERROR]" in c                 # static finding rendered
    assert "not enabled" in c             # llm placeholder path


def test_code_diff_local_repo(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()

    def g(*a):
        subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)

    g("init", "-q")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    (repo / "DESCRIPTION").write_text("Version: 0.99.0\n")
    g("add", ".")
    g("commit", "-qm", "one")
    prev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()
    (repo / "DESCRIPTION").write_text("Version: 0.99.1\n")
    g("add", ".")
    g("commit", "-qm", "two")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                          capture_output=True, text=True).stdout.strip()

    d = review.code_diff(repo, prev, head)
    assert d is not None and "0.99.1" in d
