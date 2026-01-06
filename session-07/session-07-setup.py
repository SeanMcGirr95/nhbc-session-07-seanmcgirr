
# run in termnial
#%%
uv add ipython
uv add ipykernel
uv add plotly
uv add polars
uv add pandas
uv add numpy
uv add plotly
uv add snowflake
uv add snowflake.snowpark
uv pip install snowflake-snowpark-python
uv add itables
uv add chainladder

# Quarto document: create code cell
# Ctrl + Shift + I


#%%
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import pandas as pd


#%%
import polars as pl
from snowflake.snowpark import Session
import snowflake.snowpark.functions as f
import plotly.express as px

## For working with Quarto documents
from IPython.display import Markdown
import itables
itables.init_notebook_mode()

###############################################################################

#%%
#Questions to put in the terminal using large language models:
ollama run llama3.2:3b "When is the 12th day of Christmas?"
 