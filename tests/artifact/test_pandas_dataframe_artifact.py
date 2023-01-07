import numpy as np
import pandas as pd
import pytest

from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact


@pytest.fixture
def pandas_df():
    data = pd.DataFrame(
        data=[
            [1.2, 3, "a", True],
            [-0.1, 2, "b", False],
            [np.nan, np.nan, np.nan, np.nan],
        ],
        index=pd.Index(['I0', 'I1', 'I2'], name='foo_index'),
        columns=['C0', 'C1', 'C2', 'C3'],
    )
    return data


@pytest.fixture
def metadata():
    metadata = {
        'source': 'test_to_csv_stream a b',
        'm1': 12.3,
    }
    return metadata


def test_to_csv(tmp_path, pandas_df, metadata):
    expected = """
# source test_to_csv_stream a b
# m1 12.3
foo_index,C0,C1,C2,C3
I0,1.2,3.0,a,True
I1,-0.1,2.0,b,False
I2,,,,
""".lstrip()

    artifact = PandasDataFrameArtifact(pandas_df, metadata)
    with open(tmp_path / 'test.csv', 'w') as f:
        artifact.write(f)

    with open(tmp_path / 'test.csv', 'r') as f:
        content = f.read()
    assert content == expected


def test_from_csv(tmp_path, pandas_df, metadata):
    original = PandasDataFrameArtifact(pandas_df, metadata)
    with open(tmp_path / 'test.csv', 'w') as f:
        original.write(f)

    with open(tmp_path / 'test.csv', 'r') as f:
        artifact = PandasDataFrameArtifact.read(f, index_col=0)

    pd.testing.assert_frame_equal(artifact.data, original.data)
    assert artifact.metadata == {k: str(v) for k, v in original.metadata.items()}
