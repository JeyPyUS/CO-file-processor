import configparser
import pandas as pd
from datetime import datetime, timedelta
import os

CONFIG_PATH = 'src/config.ini'
DATE_FORMAT = '%d/%m/%Y %H:%M'


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


    # Fill date column adding 215 days
    df_crew_list.iloc[:, dbkg_col] = pd.to_datetime(df_crew_list.iloc[:, dbkg_col], format='%Y-%d-%m %H:%M', errors='coerce')
    df_crew_list.iloc[:, join_col] = pd.to_datetime(df_crew_list.iloc[:, join_col], format='%Y-%d-%m %H:%M', errors='coerce')
    # df_crew_list.iloc[:, exp_col] = pd.to_datetime(df_crew_list.iloc[:, exp_col], format='%Y-%m-%d', errors='coerce')
    # df_crew_list.iloc[:, brd_col] = pd.to_datetime(df_crew_list.iloc[:, brd_col], format='%Y-%m-%d', errors='coerce')
    print('--------Fechas como se reciben:')
    print(df_crew_list.iloc[3, join_col])
    print(type(df_crew_list.iloc[3, join_col]))
    print(df_crew_list.iloc[3, dbkg_col])
    print(type(df_crew_list.iloc[3, dbkg_col]))

    
    # print(df_crew_list.iloc[:, [join_col, dbkg_col]])

    df_crew_list.iloc[:, dbkg_col] = df_crew_list.iloc[:, dbkg_col].fillna(df_crew_list.iloc[:,join_col] + pd.Timedelta(1, unit='days'))

    # print(df_crew_list.iloc[:, [join_col, dbkg_col]])
    print('--------Fechas tras hacer la suma:')
    print(df_crew_list.iloc[3, join_col])
    print(type(df_crew_list.iloc[3, join_col]))
    print(df_crew_list.iloc[3, dbkg_col])
    print(type(df_crew_list.iloc[3, dbkg_col]))


    df_crew_list.iloc[:, dbkg_col] = df_crew_list.iloc[:, dbkg_col].dt.strftime(DATE_FORMAT)
    df_crew_list.iloc[:, join_col] = df_crew_list.iloc[:, join_col].dt.strftime(DATE_FORMAT)
    # df_crew_list.iloc[:, exp_col] = df_crew_list.iloc[:, exp_col].dt.strftime('%Y/%m/%d')
    # df_crew_list.iloc[:, brd_col] = df_crew_list.iloc[:, brd_col].dt.strftime('%Y/%m/%d')

    # print(df_crew_list.iloc[:, [join_col, dbkg_col]])
    print('--------Fechas al corregir formato:')
    print(df_crew_list.iloc[3, join_col])
    print(type(df_crew_list.iloc[3, join_col]))
    print(df_crew_list.iloc[3, dbkg_col])
    print(type(df_crew_list.iloc[3, dbkg_col]))

    df_crew_list_2 = df_crew_list[df_crew_list.iloc[:, e_s_col] == 'E & S']

    df_crew_list.iloc[:, e_s_col] = df_crew_list.iloc[:, e_s_col].replace('E & S', 'E')
    df_crew_list_2.iloc[:, e_s_col] = df_crew_list_2.iloc[:, e_s_col].replace('E & S', 'S')

    df_crew_list = pd.concat([df_crew_list, df_crew_list_2], ignore_index=True)

    # df_to_csv(df_crew_list, local_config['output'] + csv_config['output_cl'])
    



if __name__ == "__main__":
    main()