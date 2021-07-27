from pyspark.sql import Row
import pyspark
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import pyspark.sql.functions as f
from splink_graph.cc import (
    _find_graphframes_jars,
    graphframes_connected_components,
    pyspark_connected_components,
)
from graphframes import GraphFrame


@pytest.mark.order(1)
def test_cc_simple(sparkSessionwithgraphframes, graphframes_tmpdir):

    # Create an Edge DataFrame with "src" and "dst" columns
    e2_df = sparkSessionwithgraphframes.createDataFrame(
        [
            ("a", "b", 0.4),
            ("b", "c", 0.56),
            ("d", "e", 0.84),
            ("e", "f", 0.65),
            ("f", "d", 0.67),
            ("f", "g", 0.34),
            ("g", "h", 0.99),
            ("h", "i", 0.5),
            ("h", "j", 0.8),
        ],
        ["src", "dst", "weight"],
    )

    assert _find_graphframes_jars(sparkSessionwithgraphframes) == 0

    sparkSessionwithgraphframes.sparkContext.setCheckpointDir("graphframes_tempdir/")
    df_result = graphframes_connected_components(
        e2_df, src="src", dst="dst", weight_colname="weight", cc_threshold=0.82
    ).toPandas()

    assert df_result["cluster_id"].unique().size == 2
    assert df_result["node_id"].unique().size == 4

    df_result2 = graphframes_connected_components(
        e2_df, src="src", dst="dst", weight_colname="weight", cc_threshold=0.2
    ).toPandas()
    assert df_result2["cluster_id"].unique().size == 2
    assert df_result2["node_id"].count() == 10

@pytest.mark.skip(reason="still WIP")
@pytest.mark.order(2)
def test_cc_pyspark_simple(spark, graphframes_tmpdir):

    # Create an Edge DataFrame with "src" and "dst" columns
    e2_df = spark.createDataFrame(
        [
            ("a", "b", 0.4),
            ("b", "c", 0.56),
            ("d", "e", 0.84),
            ("e", "f", 0.65),
            ("f", "d", 0.67),
            ("f", "g", 0.34),
            ("g", "h", 0.99),
            ("h", "i", 0.5),
            ("h", "j", 0.8),
        ],
        ["src", "dst", "weight"],
    )

    # spark.sparkContext.setCheckpointDir("graphframes_tempdir/")
    df_result = pyspark_connected_components(
        spark,
        edges_df=e2_df,
        src="src",
        dst="dst",
        weight_colname="weight",
        cc_threshold=0.82,
    ).toPandas()

    assert df_result["cluster_id"].unique().size == 2
    assert df_result["node_id"].unique().size == 4

    df_result2 = pyspark_connected_components(
        spark,
        edges_df=e2_df,
        src="src",
        dst="dst",
        weight_colname="weight",
        cc_threshold=0.2,
    ).toPandas()
    assert df_result2["cluster_id"].unique().size == 2
    assert df_result2["node_id"].count() == 10
