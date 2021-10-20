import pandas as pd
from scipy import interpolate
import numpy as np
import plotly.graph_objects as go


def get_display_customdata(df):
    display = '<extra>' + df.alpha_3 + '</extra><b>' + df.iso_names + ' (' + df.Year.astype(
        str) + ')</b><br><br>Medals:' + \
              '<br>Gold: ' + df.Gold.astype(str) + \
              '<br>Silver: ' + df.Silver.astype(str) + \
              '<br>Bronze: ' + df.Bronze.astype(str) + \
              '<br><br>Total medals collected: ' + df.TotalMedals.astype(str) + \
              '<br>Partecipated to ' + \
              df.events_partecipations_no.astype(str) + \
              ' events with ' + df.distinct_athletes_no.astype(str) + ' athletes' + \
              '<br><br>Country population: ' + df.population_display.astype(str)
    return display


def get_interpolation_coefficients(x, matrix_y, columns_names):
    n_cols = matrix_y.shape[1]
    interp = []
    for i in range(n_cols):
        interp.append(
            interpolate.splrep(x, matrix_y[:, i], s=0)
        )
    return interp


def get_derivatives(df, parameter='TotalMedals'):
    year_pivot_df = pd.pivot(df, index='Year', columns='NOC', values=parameter)
    year_pivot_df = year_pivot_df.fillna(value=0)
    velocity_df = pd.DataFrame(np.gradient(year_pivot_df.to_numpy(), 4, axis=0), columns=year_pivot_df.columns)
    velocity_df.set_index(year_pivot_df.index, inplace=True)
    vel_interpolations = get_interpolation_coefficients(velocity_df.index, velocity_df.to_numpy(), velocity_df.columns)

    acceleration_df = pd.DataFrame(np.gradient(velocity_df.to_numpy(), 4, axis=0), columns=year_pivot_df.columns)
    acceleration_df.set_index(year_pivot_df.index, inplace=True)
    acc_interpolations = get_interpolation_coefficients(acceleration_df.index, acceleration_df.to_numpy(),
                                                        acceleration_df.columns)
    return velocity_df, acceleration_df


def add_worldwide_derivatives_to_df(df):
    vel, acc = get_derivatives(df)
    vel = vel.reset_index()
    acc = acc.reset_index()
    vel_melt = pd.melt(vel, id_vars='Year', var_name='NOC', value_name='velocity')
    acc_melt = pd.melt(acc, id_vars='Year', var_name='NOC', value_name='acceleration')
    gold_derivatives_df = df.merge(vel_melt, on=['NOC', 'Year'], how='left')
    gold_derivatives_df = gold_derivatives_df.merge(acc_melt, on=['NOC', 'Year'], how='left')
    return gold_derivatives_df


def filter_by_year_my_country(df, my_country, my_year, threshold=0.2):
    # Get population of my country
    pop = df['Population'].loc[(df.NOC == my_country) & (df.Year == my_year)].iloc[0]

    # Define cut-off percentage threshold
    # pop_max = pop +- threshold%
    # threshold = 0.15 means pop +- 15%

    filtered_countries = df[df.Year == my_year]
    filtered_countries = filtered_countries[
        filtered_countries.Population.between(pop - pop * threshold, pop + pop * threshold)]
    filtered_countries = filtered_countries.sort_values(by='TotalMedals')
    return filtered_countries


# %%
def get_choropleth_title_starts_with(sorting_parameter):
    title_starts_with = ''
    if sorting_parameter == 'TotalMedals':
        title_starts_with = 'Total medals collected'
    elif sorting_parameter in ['Gold', 'Silver', 'Bronze']:
        title_starts_with = f'{sorting_parameter} medals collected'
    elif sorting_parameter == 'velocity':
        title_starts_with = f'Best trend'
    elif sorting_parameter == 'acceleration':
        title_starts_with = f'Fastest improving'
    elif sorting_parameter == 'AthletePerEventPartecipation':
        title_starts_with = f'Athletes per event'
    elif sorting_parameter == 'AthletePerMedal':
        title_starts_with = f'Athletes per medal'
    elif sorting_parameter == 'EventPartecipationPerMedal':
        title_starts_with = f'Event partecipations per medal'
    elif sorting_parameter == 'PopulationPerMedal_thousands':
        title_starts_with = 'Population (thousands) per medal'
    return title_starts_with


def get_choropleth_colormap_title(sorting_parameter):
    colormap_title = ''
    if sorting_parameter == 'TotalMedals':
        colormap_title = 'Total medals'
    elif sorting_parameter in ['Gold', 'Silver', 'Bronze']:
        colormap_title = f'{sorting_parameter}'
    elif sorting_parameter == 'velocity':
        colormap_title = f'Velocity'
    elif sorting_parameter == 'acceleration':
        colormap_title = f'Acceleration'
    elif sorting_parameter == 'AthletePerEventPartecipation':
        colormap_title = f'Athl/Event'
    elif sorting_parameter == 'AthletePerMedal':
        colormap_title = f'Athl/Medal'
    elif sorting_parameter == 'EventPartecipationPerMedal':
        colormap_title = f'Event/medal'
    elif sorting_parameter == 'PopulationPerMedal_thousands':
        colormap_title = 'Pop/Medal'
    return colormap_title


def get_choropleth_colormap(sorting_parameter):
    colormap = "Emrld"
    if sorting_parameter in ['Gold', 'Silver', 'Bronze', 'TotalMedals']:
        colormap = "Emrld"
    elif sorting_parameter in ['velocity', 'acceleration']:
        colormap = 'RdYlGn'
    return colormap


def get_fig_choropleth_similar_size(df, my_country, show_years, sort_by='TotalMedals', threshold=0.2):
    # Show only my country and similar sized ones
    fig_cho_size = go.Figure()

    first = True
    for year in show_years:
        starting_data = filter_by_year_my_country(df, my_country, year, threshold)

        visible = False
        if first:
            visible = True
            first = False

        fig_cho_size.add_trace( \
            go.Choropleth(
                locations=starting_data.alpha_3,
                z=starting_data[sort_by],
                colorscale=get_choropleth_colormap(sort_by),
                customdata=starting_data.display,
                hovertemplate='%{customdata}',
                text=starting_data.iso_names,
                marker_line_color='darkgray',
                marker_line_width=0.5,
                colorbar_title=get_choropleth_colormap_title(sort_by),
                visible=visible
            )
        )

    title_starts_with = get_choropleth_title_starts_with(sort_by)
    y_lab_height = 0.98
    fig_cho_size.update_layout(
        title={
            'text': f'{title_starts_with} in year {show_years[0]} by country<br>'
                    f'Countries with population similar to '
                    f'{starting_data["iso_names"].loc[starting_data.alpha_3 == my_country].iloc[0]} '
                    f'(&plusmn; 20%)',
            'y': 1,
            'x': 0.45,
            'xanchor': 'center',
            'yanchor': 'bottom',
            'xref': 'paper',
            'yref': 'paper',
            'pad': {"b": 40, "t": 10},
        },

        # list([{'label': i,
        #                     'args': [
        #                          {
        #                          'y':[df_select[i]],
        #                          }],
        #                     'method': 'restyle'} for i in df_select.columns[1:]]),
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label=str(show_years[0]),
                         method="update",
                         args=[{"visible": [True, False, False]},
                               {"title": f'{title_starts_with} in year {show_years[0]} by country<br>'
                                         f'Countries with population similar to '
                                         f'{starting_data["iso_names"].loc[starting_data.alpha_3 == my_country].iloc[0]} '
                                         f'(&plusmn; 20%)', }]),
                    dict(label=str(show_years[1]),
                         method="update",
                         args=[{"visible": [False, True, False]},
                               {"title": f'{title_starts_with} in year {show_years[1]} by country<br>'
                                         f'Countries with population similar to '
                                         f'{starting_data["iso_names"].loc[starting_data.alpha_3 == my_country].iloc[0]} '
                                         f'(&plusmn; 20%)', }]),
                    dict(label=str(show_years[2]),
                         method="update",
                         args=[{"visible": [False, False, True]},
                               {"title": f'{title_starts_with} in year {show_years[2]} by country<br>'
                                         f'Countries with population similar to '
                                         f'{starting_data["iso_names"].loc[starting_data.alpha_3 == my_country].iloc[0]} '
                                         f'(&plusmn; 20%)', }]),
                ]),
                x=0,
                xanchor='left',
                y=y_lab_height,
                yanchor='top',
                pad={"t": 10}
            )
        ],
        annotations=[
            dict(text="Select Olympic year:", x=0, xref="paper", y=1, yref="paper",
                 align="left", showarrow=False)]

    )
    return fig_cho_size


def get_fig_choropleth_world(df, show_years, sort_by='TotalMedals'):
    fig_world = go.Figure()

    first = True

    for year in show_years:
        year_df = df.loc[df.Year == year]
        dupes = year_df.loc[year_df.duplicated(subset=['Year', 'alpha_3'], keep=False)]

        visible = False
        if first:
            visible = True
            first = False

        fig_world.add_trace( \
            go.Choropleth(
                locations=year_df.alpha_3,
                z=year_df[sort_by],
                colorscale=get_choropleth_colormap(sort_by),
                customdata=year_df.display,
                hovertemplate='%{customdata}',
                text=year_df.iso_names,
                marker_line_color='darkgray',
                marker_line_width=0.5,
                colorbar_title=get_choropleth_colormap_title(sort_by),
                visible=visible,
            )
        )

    title_starts_with = get_choropleth_title_starts_with(sort_by)
    y_label_height = 0.98
    fig_world.update_layout(
        title={
            'text': f'{title_starts_with} in year {show_years[0]} worldwide',
            'y': 1,
            'x': 0.45,
            'xanchor': 'center',
            'yanchor': 'bottom',
            'xref': 'paper',
            'yref': 'paper',
            'pad': {"b": 20, "t": 10},
        },
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label=str(show_years[0]),
                         method="update",
                         args=[{"visible": [True, False, False]},
                               {"title": f'{title_starts_with} in year {show_years[0]} worldwide'}]),
                    dict(label=str(show_years[1]),
                         method="update",
                         args=[{"visible": [False, True, False]},
                               {"title": f'{title_starts_with} in year {show_years[1]} worldwide'}]),
                    dict(label=str(show_years[2]),
                         method="update",
                         args=[{"visible": [False, False, True]},
                               {"title": f'{title_starts_with} in year {show_years[2]} worldwide'}]),
                ]),
                x=0,
                xanchor='left',
                y=y_label_height,
                yanchor='top',
                pad={"t": 10}
            )
        ],
        annotations=[
            dict(text="Select Olympic year:", x=0, xref="paper", y=1, yref="paper",
                 align="left", showarrow=False)]

    )
    return fig_world
