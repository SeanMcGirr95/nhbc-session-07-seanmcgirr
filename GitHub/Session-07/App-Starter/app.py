from shiny import App, render, ui, reactive
import polars as pl
import numpy as np
import plotly.express as px
from scipy.optimize import curve_fit
import json
from pathlib import Path
from shinywidgets import output_widget, render_widget

############################################################################

# --- 1. SETUP & DATA LOADING ---

# TODO: Load Data
# We need to load Policy_Book.parquet and Claims_Transaction.parquet
# and calculate the df_acph (Average Cost Per Home) just like in Session 6.
# For now, we will just put a placeholder.


def load_data():
    # Adjust path to point to the root of the repo
    # Assuming we run this from the repo root or Session-7 folder
    # We'll look for the files in the parent directory or current
    
    # Try to find the data files
    possible_paths = [Path("."), Path(".."), Path("../..")]
    data_dir = None
    for p in possible_paths:
        if (p / "Policy_Book.parquet").exists():
            data_dir = p
            break
            
    if data_dir is None:
        # Fallback for demo purposes if files missing
        return pl.DataFrame()

    df_policies = pl.read_parquet(data_dir / "Policy_Book.parquet")
    df_claims = pl.read_parquet(data_dir / "Claims_Transaction.parquet")

    # 1. Exposure
    df_exposure = (
        df_policies
        .group_by("CohortYear")
        .agg(pl.col("NumHomes").sum().alias("TotalHomes"))
    )

    # 2. Claims Dev
    df_dev = (
        df_claims
        .join(df_policies.select(["PolicyID", "CohortYear", "ProductType"]), on="PolicyID")
        .with_columns(
            (pl.col("ReportDate").dt.year() - pl.col("CohortYear")).alias("DevYear")
        )
        .group_by(["CohortYear", "DevYear", "ProductType"])
        .agg(pl.col("PaymentAmount").sum().alias("TotalClaims"))
    )

    # 3. ACPH
    df_acph = (
        df_dev
        .join(df_exposure, on="CohortYear")
        .with_columns(
            (pl.col("TotalClaims") / pl.col("TotalHomes")).alias("ACPH")
        )
        .sort(["ProductType", "CohortYear", "DevYear"])
    )
    
    return df_acph
 
############################################################################


# --- 2. UI DEFINITION ---

# --- 2. UI DEFINITION ---

app_ui = ui.page_fluid(
    ui.panel_title("The Outlier Excluder"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "product", 
                "Select Product:",
                choices=["Detached", "Semi-detached", "Flat", "Social Housing"]
            ),
            
            ui.card(
                ui.card_header("Select Points to Exclude"),
                ui.output_data_frame("exclusion_grid"),
                height="400px"
            ),
            
            ui.input_action_button("save_btn", "Save Assumptions", class_="btn-success"),
            # ui.output_text_verbatim("save_status")
        ),
        
        ui.card(
            ui.card_header("Curve Fit Analysis"),
            output_widget("main_plot")
        ),
        
        ui.card(
            ui.card_header("Fitted Parameters"),
            ui.output_table("params_table")
        )
    )
)
 

# --- 3. SERVER LOGIC ---

def server(input, output, session):
    
    # TODO: Reactive Data Filter
    # @reactive.Calc
    # def filtered_data():
    #     ... return df_acph filtered by input.product() ...
    @reactive.Calc
    def filtered_data():
        # Get the input
        selected_product = input.product()
        
        # Filter Polars DataFrame
        df = df_acph.filter(pl.col("ProductType") == selected_product)
        return df

    # TODO: Reactive Curve Fit
    # @reactive.Calc
    # def fitted_curve():
    #     ... get filtered_data() ...
    #     ... remove input.excluded_years() ...
    #     ... run curve_fit ...
    #     ... return parameters ...
 
    @render.data_frame
    def exclusion_grid():
        df = filtered_data()
        if df.is_empty(): return render.DataGrid(pl.DataFrame())
        
        # Show relevant columns for selection
        display_df = df.select(["CohortYear", "DevYear", "ACPH"]).to_pandas()
        
        return render.DataGrid(
            display_df,
            selection_mode="rows",
            summary=False,
            filters=True
        )
    
    @reactive.Calc
    def fitted_curve():
        df = filtered_data()
        if df.is_empty(): return None
        
        # Get selected rows to exclude
        # input.exclusion_grid.selected_rows() returns a tuple of row indices
        selected_indices = input.exclusion_grid_selected_rows()
        
        # Create a boolean mask for inclusion
        # Default is include all
        include_mask = np.ones(len(df), dtype=bool)
        
        if selected_indices:
            include_mask[list(selected_indices)] = False
            
        df_clean = df.filter(pl.Series(include_mask))
        
        # Aggregate to get the pattern to fit
        df_pattern = (
            df_clean
            .group_by("DevYear")
            .agg(pl.col("ACPH").mean().alias("AvgACPH"))
            .sort("DevYear")
            .filter(pl.col("DevYear") <= 10)
        )
        
        if df_pattern.height < 3: return None # Not enough points
        
        x_data = df_pattern["DevYear"].to_numpy()
        y_data = df_pattern["AvgACPH"].to_numpy()
        
        try:
            popt, _ = curve_fit(actuarial_curve, x_data, y_data, p0=[100, 2, 0.5], maxfev=5000)
            return popt
        except:
            return None


    @render_widget
    def main_plot():
        # Placeholder plot
        return px.scatter(title="Please implement data loading first!")
    
    @render.table
    def params_table():
        # Placeholder table
        return pl.DataFrame({"Parameter": ["A", "B", "C"], "Value": [0, 0, 0]})
    
    # TODO: Save Button Logic
    # @reactive.Effect
    # @reactive.event(input.save_btn)
    # def save():
    #     ... write to assumptions.json ...

    @reactive.Effect
    @reactive.event(input.save_btn)
    def save_assumptions():
        # ... logic to save JSON ...
        ui.notification_show("Saved!", type="success")


app = App(app_ui, server)
