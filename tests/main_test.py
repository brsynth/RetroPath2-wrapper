import os
import unittest


class Main_test(unittest.TestCase):
    dataset_path = os.path.join(os.path.dirname(__file__), "data")

    # preferences
    preference = os.path.join(dataset_path, "preference.epf")

    # rules
    rules_csv = os.path.join(dataset_path, "rules.csv.gz")
    rulesd12_csv = os.path.join(dataset_path, "rules_d12.csv.gz")

    # empty
    empty_csv = os.path.join(dataset_path, "empty_file.csv")
    empty_sink_csv = os.path.join(dataset_path, "empty_sink.csv")
    source_weird_csv = os.path.join(dataset_path, "source.weird.csv")
    johndoe = os.path.join(dataset_path, "johndoe")

    # source
    source_csv = os.path.join(dataset_path, "source.csv")
    source_dat = os.path.join(dataset_path, "source.dat")
    source_mnxm790_csv = os.path.join(dataset_path, "source.mnxm790.csv")

    # sink
    sink_csv = os.path.join(dataset_path, "sink.csv")
    sink_dat = os.path.join(dataset_path, "sink.dat")

    # scope
    scope_csv = os.path.join(dataset_path, "scope.csv")
    scoped12_csv = os.path.join(dataset_path, "scope_d12.csv")

    # inchi
    inchi_csv = os.path.join(dataset_path, "inchi_test_cases.csv")

    # alanine
    alanine_sink_csv = os.path.join(dataset_path, "alanine", "in", "sink.csv")
    alanine_source_csv = os.path.join(dataset_path, "alanine", "in", "source.csv")

    # lycopene
    lycopene_sink_csv = os.path.join(dataset_path, "lycopene", "in", "sink.csv")
    lycopene_source_csv = os.path.join(dataset_path, "lycopene", "in", "source.csv")
    lycopene_r20210127_results_csv = os.path.join(dataset_path, "lycopene", "out", "r20210127", "results.csv")
    lycopene_r20210127_source_csv = os.path.join(dataset_path, "lycopene", "out", "r20210127", "source-in-sink.csv")
    lycopene_r20210127_target_csv = os.path.join(dataset_path, "lycopene", "out", "r20210127", "target_scope.csv")
    lycopene_r20220104_results_csv = os.path.join(dataset_path, "lycopene", "out", "r20220104", "results.csv")
    lycopene_r20220104_source_csv = os.path.join(dataset_path, "lycopene", "out", "r20220104", "source-in-sink.csv")
    lycopene_r20220104_target_csv = os.path.join(dataset_path, "lycopene", "out", "r20220104", "target_scope.csv")
