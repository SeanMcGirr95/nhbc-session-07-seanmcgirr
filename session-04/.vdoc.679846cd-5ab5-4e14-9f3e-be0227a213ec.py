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
# Min and Max UWY
max_uwy= (
    claims_data
    .select(f.max(f.col("UWY")).alias("MAX_UWY"))
    .collect()[0]["MAX_UWY"]
)
max_uwy
# Min and Max UWY
min_uwy= (
    claims_data
    .select(f.min(f.col("UWY")).alias("MIN_UWY"))
    .collect()[0]["MIN_UWY"]
)
min_uwy

```
#
#
#
# Min and Max UWY
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
