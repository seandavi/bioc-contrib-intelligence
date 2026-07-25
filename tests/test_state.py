from bcintel.state import State

REPO = "Bioconductor/Contributions"


def test_state_roundtrip_and_persist(tmp_path):
    path = tmp_path / "nested" / "state.db"  # parent dirs created on open
    st = State(path)
    assert st.seen(REPO, 1, "abc123") is False
    st.record(REPO, 1, "abc123", stage="review", action="review",
              briefing_path="x.md")
    assert st.seen(REPO, 1, "abc123") is True
    assert st.seen(REPO, 1, "def456") is False  # new sha, same issue -> not seen
    st.close()

    st2 = State(path)  # reopening the same file persists
    assert st2.seen(REPO, 1, "abc123") is True
    st2.close()
