import solara
import plotly.express as px
import plotly.graph_objects as go
from solara.lab.components import use_dark_effective
from collections import Counter
import numpy as np

from numpy import nanmin, nanmax, isnan

def matching_cols(df, val, col, count = None):
    """
    Return a dictionary of columns and values for a given value of a column
    """
 
    out = {c:df[c][df[col]==val].to_list() for c in df.columns}
    out.update({'count':count or len(out[col])})
    out.update({col:val})
    return out

def aggregrate(dataframe, col):
    vals = Counter(dataframe[col])
    return {v:matching_cols(dataframe, v, col, count)  for v,count in vals.items()}


@solara.component
def AgeHoHistogram(data, selected = solara.Reactive(None), which = 'age', subset = None, subset_label = None, main_label = None, subset_color = '#0097A7', main_color = '#BBBBBB', title = None, merged_subset= None, merged_color = '#3e3e3e', show_merged = True, include_merged = True):
    # subset is boolean array which take subset of data
    
    
    df = data.copy()
    df['category'] = 'in_class'
    
    
    def sids_agg(sids):
        return '<br>'+ '<br>'.join(sids)
    def name_agg(names):
        return '<br>'+ '<br>'.join(names)
    
    # yeah, in this view we don't what they did or did not see
    subset = None
    

    def return_agged(data, which):
        return data.groupby([which, 'category'], as_index=False).agg(count=(which,'size'), student_id = ('student_id', sids_agg), name = ('name', name_agg))

    
    merged_mask = np.array(merged_subset) if merged_subset is not None else None

    if (merged_subset is not None) and (not include_merged):
        df = df[~merged_mask]
    elif (merged_subset is not None) and show_merged:
        df.loc[merged_mask, 'category'] = 'merged'

    if selected.value is not None:
        df.loc[df['student_id'] == str(selected.value), 'category'] = 'selected'

    df_agg = return_agged(df, which)
    
    if len(df_agg) == 0:
        xmin, xmax = 0, 1
    else:
        xmin, xmax = nanmin(df_agg[which]), nanmax(df_agg[which])

    labels = {'age':'Age of Universe (Gyr)', 'student_id':'Student', 'name': 'Student', 'h0':'Hubble Constant (km/s/Mpc)'}
    

    
    if use_dark_effective():
        plotly_theme = 'plotly_dark'
        axes_color = "#efefef"
        border_color = "#ccc"
        bgcolor = "#333"
        plot_bgcolor = "#111111"
    else:
        plotly_theme = 'simple_white'
        axes_color = "black"
        border_color = "#444"
        bgcolor = "#efefef"
        plot_bgcolor = "white"

    # Category display names, colors, and stack order (bottom -> top)
    cat_labels = {
        'merged': 'Merged Class',
        'in_class': 'Your Class',
        'selected': str(selected.value) if selected.value is not None else 'Selected',
    }
    cat_colors = {
        'merged': merged_color,
        'in_class': subset_color,
        'selected': '#FF8A65',
    }

    df_agg['category_label'] = df_agg['category'].map(cat_labels)
    stack_order = [cat_labels[c] for c in ('in_class', 'selected','merged') if c in df_agg['category'].values]
    color_map = {cat_labels[k]: v for k, v in cat_colors.items()}

    fig = px.bar(
        data_frame = df_agg, 
        x = which, 
        y='count', 
        color='category_label',
        custom_data=['name'], 
        labels = labels, 
        barmode='stack', 
        opacity=1,
        template=plotly_theme, 
        category_orders={'category_label': stack_order}, # not the value, but the "label" order !?
        color_discrete_map=color_map
        )

    hovertemplate = labels[which] + ': %{x}<br>' + 'count=%{y}<br>' + labels['name'] + ': %{customdata[0]}' + '<extra></extra>'
    fig.update_traces(hovertemplate=hovertemplate, width=0.8)
    fig.for_each_trace(
        lambda t: t.update(hovertemplate=labels[which] + ': %{x}<br>count=%{y}<br>Merged Students<extra></extra>'),
        selector=dict(name=cat_labels['merged'])
    )

    title = f'Class {which.capitalize()}<br>Distribution' if title is None else title
    fig.update_layout(showlegend=True, title_text=title, xaxis_showgrid=False, yaxis_showgrid=False, plot_bgcolor=plot_bgcolor)
    # show only integers on y-axis
    fig.update_yaxes(tick0=0, dtick=1, linecolor=axes_color)
    # show ticks every 1
    fig.update_xaxes(range=[xmin-1.5, xmax+1.5], linecolor=axes_color)
    
        
        # show legend
    fig.update_layout(
        legend = dict(
            orientation="v",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1,
            bordercolor=border_color,
            borderwidth=0,
            bgcolor=bgcolor,
            itemclick = False,
            itemdoubleclick = False,
            font=dict(size=11),
            title=dict(text='')
        ),
        margin=dict(l=0, r=25, t=50, b=0),
        title = dict(
            xref='container',
            x=0.05,
            xanchor='left',
            yref='container',
            yanchor='top',
            y=.95,
        )
    )
    
    

    solara.FigurePlotly(fig)