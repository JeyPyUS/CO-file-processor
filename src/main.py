import configparser
import pandas as pd
from datetime import datetime, timedelta
import os

CONFIG_PATH = 'src/config.ini'
DATE_FORMAT_L = '%d/%m/%Y %H:%M'
DATE_FORMAT_S = '%d/%m/%Y'


def get_config(file_path):
    '''
    This function reads the config file
    '''

    if not os.path.exists(file_path):
        print(f"El archivo {file_path} no se encuentra.")

    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    # Read the config.ini file
    config.read(file_path)
    
    # Convert the sections and their key-value pairs into a dictionary
    config_dict = {section: dict(config.items(section)) for section in config.sections()}
    
    return config_dict


def get_df_from_xlsx(input_file, sheet_name):
    '''
    This function extract a df from a specific sheet in the xlsx file
    '''
    
    # Read the specific sheet and save it into a DataFrame
    df = pd.read_excel(input_file, sheet_name=sheet_name)

    return df


def df_to_csv(df, file_name):
    '''
    This function generates csv files from df
    '''
    df.to_csv(file_name, sep=';', index=False)

    print(f'El archivo {file_name.split('\\')[-1]} se ha creado exitosamente.')


def date_format_update(df, col_num, info):
    '''
    This function updates date format depending of the columns in Excel
    '''
    if str(col_num) in info:
        dt_format = DATE_FORMAT_S
    elif str(col_num) in info:
        dt_format = DATE_FORMAT_L
    
    df['aux'] = df.iloc[:, col_num].dt.strftime(dt_format)
    df.iloc[:, col_num] = df.iloc[:, col_num].apply(lambda x: None)
    df.iloc[:, col_num] = df['aux']
    df.drop('aux', axis=1, inplace=True)


def main():
    '''
    Main process
    '''
    # Set configurtion dictionaries
    config_data = get_config(CONFIG_PATH)
    local_config = config_data['local']
    xlsx_config = config_data['xlsx_file']
    csv_config = config_data['csv_file']

    # Begins extraction from xlsx
    df_crew_list = get_df_from_xlsx(
        local_config['input'] + xlsx_config['input_file'], 
        xlsx_config['crew_list_sheet'])
    df_waste = get_df_from_xlsx(
        local_config['input'] + xlsx_config['input_file'], 
        xlsx_config['waste_sheet'])


    ### CREW LIST treatment ###
    zzzz_col = int(xlsx_config['zzzzz_col'])
    dbkg_col = int(xlsx_config['dissenbarkin_date_col'])
    join_col = int(xlsx_config['join_date_col'])
    e_s_col = int(xlsx_config['e_s_col'])
    exp_col = int(xlsx_config['exp_date_col'])
    brd_col = int(xlsx_config['birthday_date'])

    # Set 'Dissenbarking port LOCODE' column to 'ZZZZZ' when empty
    df_crew_list.iloc[:, zzzz_col] = df_crew_list.iloc[:, zzzz_col].fillna('ZZZZZ')

    print('--------Fechas como se reciben:')
    for i in range(len(df_crew_list.iloc[:, join_col])):
        d1 = df_crew_list.iloc[i, join_col]
        d2 = df_crew_list.iloc[i, dbkg_col]
        print(f'{d1.strftime("%Y")}-{d1.strftime("%m")}-{d1.strftime("%d")} -> {d2}')

    # Fill date column adding 215 days
    df_crew_list.iloc[:, dbkg_col] = df_crew_list.iloc[:, dbkg_col].fillna(df_crew_list.iloc[:,join_col] + pd.Timedelta(1, unit='days'))

    print('--------Fechas tras hacer la suma:')
    for i in range(len(df_crew_list.iloc[:, join_col])):
        d1 = df_crew_list.iloc[i, join_col]
        d2 = df_crew_list.iloc[i, dbkg_col]
        print(f'{d1.strftime("%Y")}-{d1.strftime("%m")}-{d1.strftime("%d")} -> {d2.strftime("%Y")}-{d2.strftime("%m")}-{d2.strftime("%d")}')

    date_format_update(df_crew_list, xlsx_config['join_date_col'], xlsx_config['long_date_cols'])
    date_format_update(df_crew_list, xlsx_config['dissenbarkin_date_col'], xlsx_config['long_date_cols'])
    date_format_update(df_crew_list, xlsx_config['exp_date_col'], xlsx_config['short_date_cols'])
    date_format_update(df_crew_list, xlsx_config['birthday_date'], xlsx_config['short_date_cols'])

    print('--------Fechas al corregir formato:')
    for i in range(len(df_crew_list.iloc[:, join_col])):
        d1 = df_crew_list.iloc[i, join_col]
        d2 = df_crew_list.iloc[i, dbkg_col]
        print(f'{d1} -> {d2}')
        print(f'{df_crew_list['aux_join_col'][i]} -> {df_crew_list['aux_dbkg_col'][i]}')

    df_crew_list_2 = df_crew_list[df_crew_list.iloc[:, e_s_col] == 'E & S']

    df_crew_list.iloc[:, e_s_col] = df_crew_list.iloc[:, e_s_col].replace('E & S', 'E')
    df_crew_list_2.iloc[:, e_s_col] = df_crew_list_2.iloc[:, e_s_col].replace('E & S', 'S')

    df_crew_list = pd.concat([df_crew_list, df_crew_list_2], ignore_index=True)

    # df_to_csv(df_crew_list, local_config['output'] + csv_config['output_cl'])
    



if __name__ == "__main__":
    main()