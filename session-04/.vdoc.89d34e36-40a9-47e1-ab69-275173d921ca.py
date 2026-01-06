# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
import polars as pl
from snowflake.snowpark import Session
import snowflake.snowpark.functions as f
import plotly.express as px
import chainladder as cl
import pandas as pd

## For working with Quarto documents
from IPython.display import Markdown
import itables
itables.init_notebook_mode()
#
#
#
if category == "Capped":
    sql_query = f"""
    SELECT c.Period,
           c.ReservingSegmentationGroup_Capped AS ReservingSegmentationGroup,
           c.UWY,
           c.FirstNotifiedFY,
           c.FirstNotifiedFYQuarter,
           c.ProcessingQuarter,
           SUM(c.ClaimCount) AS ClaimCount,
           SUM(c.Paid_Capped) AS Paid,
           SUM(c.CaseIncurred_Capped) AS Incurred,
           SUM(c.BuilderRecs_Capped) AS BuilderRecs
    FROM datastore.ClaimsData c
    WHERE c.Period = {xlPeriod.value}
      AND c.isExcludedReserving = 0
      AND c.UWY >= {xlUWYStart.value}
      AND c.ReservingSegmentationGroup_Capped = '{xlSegClass.value}'
      AND (
             c.ValidityIndicator = 'Y'
          OR c.Paid_Capped <> 0
          OR c.CaseIncurred_Capped <> 0
          OR c.BuilderRecs_Capped <> 0
      )
    GROUP BY c.Period, c.ReservingSegmentationGroup_Capped, c.UWY,
             c.FirstNotifiedFY, c.FirstNotifiedFYHalfYear, c.FirstNotifiedFYQuarter,
             c.FirstNotifiedMonth, c.ProcessingHalfYear, c.ProcessingQuarter, c.ProcessingMonth
    """
else:
    sql_query = f"""
    SELECT c.Period,
           c.ReservingSegmentationGroup_Excess AS ReservingSegmentationGroup,
           c.UWY,
           c.FirstNotifiedFY,
           c.FirstNotifiedFYQuarter,
           c.ProcessingQuarter,
           SUM(c.ClaimCount_Excess) AS ClaimCount,
           SUM(c.Paid_Excess) AS Paid,
           SUM(c.CaseIncurred_Excess) AS Incurred,
           SUM(c.BuilderRecs_Excess) AS BuilderRecs
    FROM datastore.ClaimsData c
    WHERE c.Period = {xlPeriod.value}
      AND c.isExcludedReserving = 0
      AND c.UWY >= {xlUWYStart.value}
      AND c.ReservingSegmentationGroup_Excess = '{xlSegClass.value}'
      AND (
             c.ValidityIndicator = 'Y'
          OR c.Paid_Excess <> 0
          OR c.CaseIncurred_Excess <> 0
          OR c.BuilderRecs_Excess <> 0
      )
    GROUP BY c.Period, c.ReservingSegmentationGroup_Excess, c.UWY,
             c.FirstNotifiedFY, c.FirstNotifiedFYHalfYear, c.FirstNotifiedFYQuarter,
             c.FirstNotifiedMonth, c.ProcessingHalfYear, c.ProcessingQuarter, c.ProcessingMonth
    """
#
#
#
#
#
# Connect to the database and set claims_data to the remote table
session = Session.builder.config("connection_name", "workbench").create()
claims_data = session.table("TEAM_SANDBOX.ACTUARIAL_RESERVING.CLAIMSDATA")
#
#
#
#
#
#
#
#
# Identify the latest period
latest_period_value = (
    claims_data
    .select(f.max(f.col("PERIOD")).alias("LATEST_PERIOD"))
    .collect()[0]["LATEST_PERIOD"]
)
latest_period_value
#
#
#
# filter claims data
claims_data = (
    claims_data.
    filter(
        (f.col("Period") == latest_period_value) &
        (f.col("isExcludedReserving") ==0)
    )
)
claims_data.count()
#
#
#
# Sanity checks

# Processing quarter always less than First Notified quarter?
claims_data.filter(f.col("PROCESSINGQUARTER") < f.col("FIRSTNOTIFIEDFYQUARTER")).count() / claims_data.count()

#
#
#
# Sanity checks

# Processing quarter always less than First Notified quarter?
claims_data.filter(f.col("UWY") > 2026).count()

#
#
#
# Sanity checks
# Max UWY
max_uwy= (
    claims_data
    .select(f.max(f.col("UWY")).alias("MAX_UWY"))
    .collect()[0]["MAX_UWY"]
)
max_uwy

#
#
#
# Sanity checks
# Min UWY
min_uwy= (
    claims_data
    .select(f.min(f.col("UWY")).alias("MIN_UWY"))
    .collect()[0]["MIN_UWY"]
)
min_uwy
#
#
#
#
# Sanity checks
# Processing quarter always less than First Notified quarter?
claims_data_validity = (
    claims_data
    .select(f.col("VALIDITYINDICATOR"))
    .distinct()
    .collect()
)

claims_data_validity
#
#
#
#
#
#
#
#
#
#
# Connect to the database and set claims_data to the remote table
session = Session.builder.config("connection_name", "workbench").create()
claims_data = session.table("TEAM_SANDBOX.ACTUARIAL_RESERVING.CLAIMSDATA")
#
#
#
#

from snowflake.snowpark.functions import udf
from snowflake.snowpark.types import StringType

## We NEED this set to declare and define the udf
session.use_database("TEAM_SANDBOX")
session.use_schema("ACTUARIAL_RESERVING")

@udf(return_type=StringType(), session=session)
def convert_calendar_to_fiscal_udf(calendar_quarter: str) -> str:
    ## YOUR FUNCTION GOES HERE

    # Extract year and quarter
    year, quarter = calendar_quarter.split('Q')
    year = int(year)
    quarter = int(quarter)  # e.g., 'Q1', 'Q2'

    if quarter == 1:
        fiscal_year = year
        fiscal_qtr = 4
    elif quarter == 2:
        fiscal_year = year + 1
        fiscal_qtr = 1
    elif quarter == 3:
        fiscal_year = year + 1
        fiscal_qtr = 2
    elif quarter == 4:
        fiscal_year = year + 1
        fiscal_qtr = 3
    else:
        raise ValueError("Invalid quarter format. Must be 1, 2, 3, or 4.")
    return f"{fiscal_year}Q{fiscal_qtr}"
#
#
#
claims_data = (
    claims_data
    .with_column(
        "ProcessingFYQuarter",
        convert_calendar_to_fiscal_udf(f.col("PROCESSINGQUARTER"))
    )
)

#
#
#
claims_data.select("ProcessingQuarter", "ProcessingFYQuarter").sample(n = 50).to_pandas()
#
#
#
#
#
#
#
#
#
#
#
# filter claims data
claims_data = (
    claims_data.
    filter(
        (f.col("Period") == latest_period_value) &
        (f.col("isExcludedReserving") ==0)
    )
)
#
#
#
#
###### Pandas is not working ###########
excess_groups = pl.from_pandas(
    (
        claims_data
        .filter(f.col("ReservingSegmentationGroup_Excess").is_not_null())
        .group_by(f.col("ReservingSegmentationGroup_Excess").alias('"Groups"'))
        .agg(
            f.count("*").alias("n")
        )
        .sort("n", ascending=False)
    ).to_pandas()
)
capped_groups = pl.from_pandas(
    (
        claims_data
        .filter(f.col("ReservingSegmentationGroup_Capped").is_not_null())
        .group_by(f.col("ReservingSegmentationGroup_Capped").alias('"Groups"'))
        .agg(
            f.count("*").alias("n")
        )
        .sort("n", ascending=False)
    ).to_pandas()
)
#
#
#
#
##### Done without using Pandas #############

excess_groups = (
    claims_data
    .filter(f.col("ReservingSegmentationGroup_Excess").is_not_null())
    .group_by(f.col("ReservingSegmentationGroup_Excess").alias('"Groups"'))
    .agg(f.count("*").alias("n"))
    .sort("n", ascending=False)
)

# Display Snowpark DataFrame
excess_groups.show()  # Shows the result in tabular format

capped_groups = (
    claims_data
    .filter(f.col("ReservingSegmentationGroup_Capped").is_not_null())
    .group_by(f.col("ReservingSegmentationGroup_Capped").alias('"Groups"'))
    .agg(f.count("*").alias("n"))
    .sort("n", ascending=False)
)

# Display Snowpark DataFrame
capped_groups.show()  # Shows the result in tabular format

#
#
#
#
# Plot claims by UWY
claims_data_uwy = (
    claims_data
    .group_by("UWY")
    .agg(
        f.sum(f.col("ClaimCount")).alias("ClaimCount")
    )
    .sort("UWY")
)

px.bar(
    claims_data_uwy,
    x="UWY",
    y="ClaimCount",
    title="Claims per UWY",
    text_auto=True
)

#
#
#
#

# Aggregate claims by UWY using Snowpark
claims_data_uwy = (
    claims_data
    .group_by("UWY")
    .agg(f.sum(f.col("CLAIMCOUNT")).alias("CLAIMCOUNT"))
    .sort("UWY")
)

# Collect data into Python lists
rows = claims_data_uwy.collect()
uwy = [row["UWY"] for row in rows]
claim_count = [row["CLAIMCOUNT"] for row in rows]

# Plot using Plotly without pandas
import plotly.express as px

fig = px.bar(
    x=uwy,
    y=claim_count,
    title="Claims per UWY",
    text=claim_count,
    labels={"x": "UWY", "y": "ClaimCount"}
)

fig.show()


#
#
#
#
#
#
#
#
#
#
#
