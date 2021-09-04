# Прототип дашборда члена консорциума Салюс
import numpy as np
import pandas as pd
import datetime
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

# Формируем таблицу плановых показателей проектного портфеля из случайных значений
df = pd.DataFrame(np.random.randint(1,100,size=(20, 4)), columns=['ТМЦ', 'ФОТ', 'РИД', 'Студенты'])

df['ТМЦ'] = 347 * (df['ТМЦ'] + 5)
df['ФОТ'] = 347 * (df['ФОТ'] + 5)
df['РИД'] = df['РИД']/7
df['РИД'] = df['РИД'].astype(int) + 1
df['Студенты'] = df['Студенты']/10
df['Студенты'] = df['Студенты'].astype(int) + 1
df['Фирма'] = np.arange(len(df))
df['Фирма'] = df['Фирма'] + 1
df['Фирма'] = df['Фирма'].astype(str)
df['Фирма'] = 'Фирма' + df['Фирма']

cols = df.columns.tolist()
cols = cols[-1:] + cols[:-1]
df = df[cols]

todays_date = datetime.datetime.now().date()
index = pd.date_range(todays_date-datetime.timedelta(200), periods=50, freq='W')

cols = ['Дата', 'Фирма', 'Бетон', 'Металл', 'ФОТ', 'РИД', 'Студенты']

df_tmc = pd.DataFrame(columns=cols)

# Формируем таблицу фактических показателей проектного портфеля из случайных значений
for f in df['Фирма']:
    for data in index:
        beton = random.randrange(5) * random.randrange(300)
        metal = random.randrange(3) * random.randrange(300)
        fot = random.randrange(3) * random.randrange(400)
        rid = random.randrange(2)
        stud = random.randrange(2)
        df_tmp = df_tmc.loc[df_tmc['Фирма'] == f]
        beton_sum = df_tmp['Бетон'].sum()
        metal_sum = df_tmp['Металл'].sum()
        fot_sum = df_tmp['ФОТ'].sum()
        rid_sum = df_tmp['РИД'].sum()
        stud_sum = df_tmp['Студенты'].sum()
        
        df_tmp_main = df.loc[df['Фирма'] == f]
        
        if int(df_tmp_main['ТМЦ'].values) < int(beton + metal + beton_sum + beton_sum):
            beton = 0
            metal = 0            
        
        if int(df_tmp_main['ФОТ'].values) < int(fot + fot_sum):
            fot = 0

        if int(df_tmp_main['РИД'].values) - 2 < int(rid + rid_sum):
            rid = 0

        if int(df_tmp_main['Студенты'].values) - 2 < int(stud + stud_sum):
            stud = 0
        
        df_tmc = df_tmc.append({'Дата' : data,
                                'Фирма' : f,
                                'Бетон' : beton,
                                'Металл' : metal,
                                'ФОТ' : fot,
                                'РИД' : rid,
                                'Студенты' : stud}, 
                            ignore_index=True)
        

df_temp = df_tmc.groupby(['Фирма']).agg({'Бетон':'sum', 'Металл':'sum', 'ФОТ':'sum', 'РИД':'sum', 'Студенты':'sum'}).reset_index()

df_temp.columns = ['Фирма', 'Бетон факт', 'Металл факт', 'ФОТ факт', 'РИД факт', 'Студенты факт']

# Формируем итоговую таблицу показателей проектного портфеля
result = pd.concat([df, df_temp], axis=1)

result['ТМЦ факт'] = result['Бетон факт'] + result['Металл факт']
result = result.loc[:,~result.columns.duplicated()]
result.drop(result.columns[[5,6]], axis=1, inplace = True)
result['ТМЦ %'] = ((result['ТМЦ факт']/result['ТМЦ'])*100).round(2)
result['ФОТ %'] = ((result['ФОТ факт']/result['ФОТ'])*100).round(2)
result['РИД %'] = ((result['РИД факт']/result['РИД'])*100).round(2)
result['Студенты %'] = ((result['Студенты факт']/result['Студенты'])*100).round(2)
result = result[['Фирма', 'ТМЦ', 'ТМЦ факт', 'ТМЦ %', 'ФОТ', 'ФОТ факт', 'ФОТ %', 'РИД', 'РИД факт', 'РИД %', 'Студенты', 'Студенты факт', 'Студенты %']]

# Считаем итоговые цифры
tmc_fact = result['ТМЦ факт'].sum()
tmc_plan = result['ТМЦ'].sum()
fot_fact = result['ФОТ факт'].sum()
fot_plan = result['ФОТ'].sum()
nalog_fact = 400946000*(tmc_fact/tmc_plan)

# Рисуем сам дашборд
app = dash.Dash(__name__)

app.layout = html.Div([
       dcc.Tabs([
       dcc.Tab(label='Главная', children=[
            dash_table.DataTable(
                columns=[
                    {"name": ["", ""], "id": "pf"},
                    {"name": ["", "Государство"], "id": "gov"},
                    {"name": ["", "Консорциум"], "id": "cons"},
                    {"name": ["Затраты на администрирование", "Налоги"], "id": "tax"},
                    {"name": ["Затраты на администрирование", "ФОТ"], "id": "fot"},
                    {"name": ["KPI", "SALUS"], "id": "salus"},
                    {"name": ["KPI", "Консорциум"], "id": "cons_kpi"},
                    {"name": ["KPI", "Администрация"], "id": "adm"},
                ],
                style_cell={'textAlign': 'center'},
                data=[
                        {
                            "pf": "План",
                            "gov": tmc_plan,
                            "cons": round(tmc_plan * 2.34, 2),
                            "tax": "400 946 000.00",
                            "fot": "2 200 000.00",
                            "salus": round(fot_plan * 0.33, 2),
                            "cons_kpi": round(fot_plan * 0.33, 2),
                            "adm": round(fot_plan * 0.33, 2)
                        },
                        {
                            "pf": "Фкат",
                            "gov": tmc_fact,
                            "cons": round(tmc_fact * 2.34, 2),
                            "tax": '{:,}'.format(round(nalog_fact ,2)).replace(',', ' '),
                            "fot": "2 200 000.00",
                            "salus": round(fot_fact * 0.33, 2),
                            "cons_kpi": round(fot_fact * 0.33, 2),
                            "adm": round(fot_fact * 0.33, 2)
                        },
                        

                    ],
                    merge_duplicate_headers=True,
            )
            ]),
       dcc.Tab(label='Пректный портфель', children=[
            dash_table.DataTable(
            id='table main',
            columns=[{"name": i, "id": i} for i in result.columns],
            style_cell={'textAlign': 'center'},
            data=result.to_dict('records'),
            filter_action='native',
            sort_action="native",
            sort_mode="multi",
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'ТМЦ %',
                        'filter_query': '{ТМЦ %} > 100' 
                    },
                    'backgroundColor': 'tomato',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'ФОТ %',
                        'filter_query': '{ФОТ %} > 100' 
                    },
                    'backgroundColor': '#85144b',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'РИД %',
                        'filter_query': '{РИД %} > 100' 
                    },
                    'backgroundColor': 'RebeccaPurple',
                    'color': 'white'
                },
                {
                    'if': {
                        'column_id': 'Студенты %',
                        'filter_query': '{Студенты %} > 100' 
                    },
                    'backgroundColor': 'hotpink',
                    'color': 'white'
                },
            ]
            ),
            html.H1('Движение средств', style={'textAlign': 'center'}),
            dash_table.DataTable(
            id='table tmc',
            columns=[{"name": i, "id": i} for i in df_tmc.columns],
            style_cell={'textAlign': 'center'},
            data=df_tmc.to_dict('records'),
            filter_action='native',
            sort_action="native",
            sort_mode="multi"
            )])
        ])

])

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
