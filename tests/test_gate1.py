from bcintel.gate1 import auc, baseline, split_of


def test_auc_mann_whitney():
    assert auc([0.9, 0.8, 0.1], [1, 1, 0]) == 1.0
    assert auc([0.1, 0.9], [1, 0]) == 0.0
    assert auc([0.5, 0.5], [1, 0]) == 0.5        # ties count half
    assert auc([0.5], [1]) is None               # one class only


def test_baseline_reads_multiline_imports():
    d = ("Package: x\nImports: stats,\n    SummarizedExperiment,\n    ggplot2\n"
         "Suggests: GenomicRanges\n")
    assert baseline(d) == 1.0
    assert baseline("Package: x\nImports: ggplot2\nSuggests: GenomicRanges\n") == 0.0


def test_split_is_stable():
    assert {split_of(n) for n in range(200)} == {"dev", "test"}
    assert [split_of(n) for n in range(50)] == [split_of(n) for n in range(50)]
