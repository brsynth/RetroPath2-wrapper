import os

import pytest

cur_dir = os.path.abspath(os.path.dirname(__file__))
dataset_dir = os.path.join(cur_dir, "data")


@pytest.fixture(scope="session")
def data_dir():
    return dataset_dir

@pytest.fixture(scope="session")
def preference_path(data_dir):
    return os.path.join(data_dir, "preference.epf")

# rules
@pytest.fixture(scope="session")
def rules_csv(data_dir):
    return os.path.join(data_dir, "rules.csv.gz")

@pytest.fixture(scope="session")
def rulesd12_csv(data_dir):
    return os.path.join(data_dir, "rules_d12.csv.gz")

@pytest.fixture(scope="session")
def rulesd12_7325_csv(data_dir):
    return os.path.join(data_dir, "rules_d12_7325.csv.gz")

# empty
@pytest.fixture(scope="session")
def empty_csv(data_dir):
    return os.path.join(data_dir, "empty_file.csv")

@pytest.fixture(scope="session")
def empty_sink_csv(data_dir):
    return os.path.join(data_dir, "empty_sink.csv")

@pytest.fixture(scope="session")
def source_weird_csv(data_dir):
    return os.path.join(data_dir, "source.weird.csv")

@pytest.fixture(scope="session")
def johndoe(data_dir):
    return os.path.join(data_dir, "johndoe")

# source
@pytest.fixture(scope="session")
def source_csv(data_dir):
    return os.path.join(data_dir, "source.csv")

@pytest.fixture(scope="session")
def source_dat(data_dir):
    return os.path.join(data_dir, "source.dat")

@pytest.fixture(scope="session")
def source_mnxm790_csv(data_dir):
    return os.path.join(data_dir, "source.mnxm790.csv")

# sink
@pytest.fixture(scope="session")
def sink_csv(data_dir):
    return os.path.join(data_dir, "sink.csv")

@pytest.fixture(scope="session")
def sink_dat(data_dir):
    return os.path.join(data_dir, "sink.dat")

# scope
@pytest.fixture(scope="session")
def scope_csv(data_dir):
    return os.path.join(data_dir, "scope.csv")

@pytest.fixture(scope="session")
def scoped12_csv(data_dir):
    return os.path.join(data_dir, "scope_d12.csv")

# inchi
@pytest.fixture(scope="session")
def inchi_csv(data_dir):
    return os.path.join(data_dir, "inchi_test_cases.csv")

# alanine
@pytest.fixture(scope="session")
def alanine_sink_csv(data_dir):
    return os.path.join(data_dir, "alanine", "in", "sink.csv")

@pytest.fixture(scope="session")
def alanine_source_csv(data_dir):
    return os.path.join(data_dir, "alanine", "in", "source.csv")

# lycopene
@pytest.fixture(scope="session")
def lycopene_sink_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "in", "sink.csv")

@pytest.fixture(scope="session")
def lycopene_source_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "in", "source.csv")

@pytest.fixture(scope="session")
def lycopene_r20210127_results_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20210127", "results.csv")

@pytest.fixture(scope="session")
def lycopene_r20210127_source_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20210127", "source-in-sink.csv")

@pytest.fixture(scope="session")
def lycopene_r20210127_target_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20210127", "target_scope.csv")

@pytest.fixture(scope="session")
def lycopene_r20220104_results_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20220104", "results.csv")

@pytest.fixture(scope="session")
def lycopene_r20220104_results_7325_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20220104", "results.7325.csv")

@pytest.fixture(scope="session")
def lycopene_r20220104_source_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20220104", "source-in-sink.csv")

@pytest.fixture(scope="session")
def lycopene_r20220104_target_csv(data_dir):
    return os.path.join(data_dir, "lycopene", "out", "r20220104", "target_scope.csv")
