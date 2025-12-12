from shiny import App, ui, render, run_app

app_ui = ui.page_fluid(
    ui.h2("Widget Showcase"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("var", "Select Variable", choices=["Premium", "Claims", "Expenses"]),
            # Task 1: Add Radio Buttons
            ui.input_radio_buttons("dist", "Distribution", 
                                 choices=["Normal", "Uniform", "Exponential"]),
            ui.input_date("date", "Valuation Date"),
            ui.input_checkbox("flag", "Include IBNR?", True),
        ),
        ui.output_text_verbatim("summary")
    )
)

def server(input, output, session):
    @render.text
    def summary():
        return (
            f"Variable: {input.var()}\n"
            f"Distribution: {input.dist()}\n" # Task 2: Show selection
            f"Date: {input.date()}\n"
            f"IBNR: {input.flag()}"
        )

app = App(app_ui, server)

if __name__ == "__main__":
    run_app(app, launch_browser=True)