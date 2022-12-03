# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 11:14:44 2022

@author: wnosek
"""
import numpy as np
import PySimpleGUI as sg
import os.path
from shapely.ops import unary_union
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import geopandas as gpd

#------DEF---------------------------------------------------------------------
def read_files_shp(path_shp, files_shp, window):
    '''
    Parameters
    ----------
    path_shp : STRING
        Path to shapefiles folder
    files_shp : LIST
       List of shapefile files in path_shp


    Returns
    -------
    unique : LIST
        List of unique value in attributes
    data: DATAFRAME
        All data from shapefiles with all specyfic attributes

    '''
    
    #all data from files_shp
    unique = []
    data = gpd.GeoDataFrame()
    m=0
    for i in files_shp:
       path_shp_file = os.path.join(path_shp,i)
       file = gpd.read_file(path_shp_file, encoding="cp1250")
       file = file[file.geometry != None]
       m=m+1
       window['-PROGRESS_BAR-'].update((m*25)/(len(files_shp)))
       if hasattr(file, 'Name'): 
           data = data.append(file, ignore_index=True) 
           #unique value in column 
           p_nr = file.Name.unique().tolist()
           unique.append(p_nr)
        
           
    unique = [x for xs in unique for x in xs]
    # Using List comprehension to remove none values
    #unique = [ ele for ele in unique if ele is not None ]
    # remove duplicat
    unique = list( dict.fromkeys(unique) )
    return(unique, data)
def multipolygon(dataframes, y_pred, values):
    '''

    Parameters
    ----------
    dataframes : DATAFRAME
        Data of shapefiles
    y_pred : List
        List of cluster predictions.

    Returns
    -------
    union_polygon : geometry
        union shapefiles

    '''
    
    multi=[]
    for i in range(np.max(y_pred)+1):
        temp = dataframes['cluster']==i
        temp = dataframes[temp]
        temp = temp.buffer(1)
        temp = temp.unary_union.convex_hull
        temp = temp.buffer(float(values['-buffer-'].replace(',','.')))
        temp = temp.simplify(tolerance=0.5,preserve_topology=True)
        temp = gpd.GeoSeries(temp, index=["Geometry"])
        multi.append(temp)
        
    myGeomList = [x[0] for x in multi]
    union_polygon = unary_union(myGeomList)
    return(union_polygon)
def union_buffor_polygon(data, values):
    '''
    Parameters
    ----------
    data : DATAFRAME
        All shapefile to generate shapefile bounds.

    Returns
    -------
    union_polygon_buffor : dataset with output shapefile.

    '''
    union_polygon = data.buffer(1).unary_union.convex_hull
    union_polygon_buffor = union_polygon.buffer(float(values['-buffer-'].replace(',','.')), resolution =2, cap_style=3, join_style=2, mitre_limit=5)
    union_polygon_buffor = union_polygon_buffor.simplify(tolerance=0.5,preserve_topology=True)
    return(union_polygon_buffor)
def check_multipolygon(y_pred, lista, window, data_selected, values):
    if np.max(y_pred) > 0:
        polygon_buffor = multipolygon(data_selected, y_pred, values)
    else:
        try:
            polygon_buffor = union_buffor_polygon(data_selected, values)
        except:
            lista.append(f'Błędne dane dla : {data_selected.Name[0]}\n')
            window['-Error-'].update(lista)
            polygon_buffor = None 
    return(polygon_buffor, lista, window)
def geoseries_attributes(data_polygon, amz, dataframe, lista, window):
    '''

    Parameters
    ----------
    data_polygon : DATAFRAME
        output bounds shapefiles.
    amz : DATAFRAME
        Attributes data from excel, whose should be merged to output shapefiles.
    dataframe : DATAFRAME
        all data of shapes.
    lista : LIST
        List of errors

    Returns
    -------
    data_polygon : DATAFRAME
        Dataframe of bound shapefile, which is filled by necessery attributes.

    '''
    data_polygon = gpd.GeoSeries(data_polygon,  index=["Geometry"])
    
    data_polygon['creation_date'] = None
    data_polygon['modification_date'] = None
    

    try: 
        if dataframe['Name'][0]:
             if dataframe['Name_2'][0]:
                 data_polygon['Sekcja'] = amz[(amz['ID_materiału'] == dataframe['Name']) & (amz['Name_2'] == dataframe['Name_2'][0])]['Sekcja'].values[0][0:29]
             else:
                 data_polygon['Sekcja'] =amz[(amz['ID_materiału'] == dataframe['Name'][0]) & (amz['Name_2'].isnull())]['Sekcja'].values[0][0:29]
        else:
             if dataframe['Name_2'][0]:
                 data_polygon['JSG'] = amz[(amz['ID_materiału'].isnull()) & (amz['Name_2'] == dataframe['Name_2'][0]) ]['Sekcja'].values[0][0:29]

             else:
                 data_polygon['JSG'] = None                
    except:
        data_polygon['JSG'] = None
        
    try:
        data_polygon['Name_2'] = dataframe['Name_2'][0]
    except:
        data_polygon['Name_2'] = None

    try:
        data_polygon['Name'] = dataframe['Name'][0]
    except:
        data_polygon['Name'] = None

        
    data_polygon['attributes'] = 'new'
    data_polygon['VERSION_1'] = 1          
    return(data_polygon, lista, window)  
def check_elements_cluster(data, window, lista, values):
    '''

    Parameters
    ----------
    data : DATAFRAME
        Data from all shapefiles.
    lista : LIST
        List of errors
        
    Returns
    -------
    None.

    '''
    if len(data)>1:
        #check the clustering
        centers = [p.centroid for p in data.geometry]
        X = [[c.x, c.y] for c in centers]
        
        clustering = AgglomerativeClustering(distance_threshold=5000, n_clusters=None, compute_distances=True).fit(X)
        y_pred = clustering.labels_
        
        data['cluster'] = y_pred.tolist()
        
        poligon_bufor, lista, window= check_multipolygon(y_pred, lista, window, data, values)
       
    else:
         poligon_bufor = union_buffor_polygon(data, values)
    return(poligon_bufor)
def save_output_shp(all_zasiegi, outputshp, values, lista, window):
    '''

    Parameters
    ----------
    all_zasiegi : DATAFRAME
         Dataframe contains all the shapefile bounds.
    outputshp : STRING
        Path to save output shapefile
    lista : LIST
        List of errors

    Returns
    -------
    None.

    '''
     #save to shp
    all_zasiegi = gpd.GeoDataFrame(all_zasiegi, geometry='Geometry')
     
    if values['2176']:
         all_zasiegi = all_zasiegi.set_crs('epsg:2176')    
    elif values['2177']:
         all_zasiegi = all_zasiegi.set_crs('epsg:2177')  
    elif values['2178']:
         all_zasiegi = all_zasiegi.set_crs('epsg:2178')
    elif values['2179']:
         all_zasiegi = all_zasiegi.set_crs('epsg:2179') 
               
    all_zasiegi.to_file(outputshp, encoding="cp1250")
     
    with open('error_zasiegi.txt', 'w', encoding='utf-8') as f:
         for line in lista:
             f.write(line)
    window['-Error-'].update(f'END')
def make_polygon_area(all_zasiegi, dane_sel, amz,  lista, window, values):
    '''

    Parameters
    ----------
    all_zasiegi : DATAFRAME
        Dataframe of output shapefiles
    dane_sel : DATAFRAME
        All data to make bounds shapefile
    amz : DATAFRAME
        Attributes data from excel, whose should be merged to output shapefiles.
    lista : LIST
        List of errors

    Returns
    -------
    all_zasiegi : DATAFRAME
        Dataframe of output shapefiles.

    '''
    dane_sel = dane_sel.reset_index()

    con_krg = check_elements_cluster(dane_sel, window, lista, values)
    
    #bounds as polygon
    con_krg, lista, window = geoseries_attributes(con_krg, amz, dane_sel, lista, window)
    all_zasiegi = all_zasiegi.append(con_krg, ignore_index=True)
    
    return( all_zasiegi )  
def check_unique_p(all_p, amz, lista, all_zasiegi, window, values):
    '''
    Parameters
    ----------
    all_p : DATAFRAME
        Selected data prepared for output shapefile bounds.
    amz : DATAFRAME
        Attributes data from excel, whose should be merged to output shapefiles.
    lista : LIST
        List of errors
    all_zasiegi : DATAFRAME
        Dataframe of output shapefiles.


    Returns
    -------
    all_zasiegi : DATAFRAME
        Dataframe of output shapefiles.

    '''
    #unique k- value
    k_unique = all_p['Name_2'].unique()
    for k in k_unique:
        if k:
            all_k_p = all_p.loc[all_p['Name_2'] == k ]
            
            all_zasiegi = make_polygon_area(all_zasiegi, all_k_p, amz, lista, window, values)

        else:
            all_k_p = all_p[all_p.Name_2.isna()]

            all_zasiegi = make_polygon_area(all_zasiegi, all_k_p, amz, lista, window, values)
            
    return(all_zasiegi) 
    
def zasieg(path, files, outputshp, window, values):
    '''

    Parameters
    ----------
    path : STRING
        Path to shapefiles folder.
    files : LIST
        List of shapefiles path.
    outputshp : STRING
        Path to output shapefile.

    Returns
    -------
    None.

    '''
    #sekcje 
    amz_pierwotna = pd.read_excel(values['-Sekcje Folder-'])
    amz = amz_pierwotna[['ID_materiału','Sekcja','Name_2']]
    #amz = amz.dropna(subset = ['ID_materiału'])



    uniqe_p, data = read_files_shp(path, files, window)
    
    
    #all bounds 
    all_zasiegi = gpd.GeoDataFrame()
    n=0
    lista=[]
    for p in uniqe_p:
        if p:
            #check if attributes have more values
            if ',' in p:
                lista.append(f"Wiele Name: {p}\n")
                window['-Error-'].update(lista)
            else:
                #all rows with specyfic column
                all_p = data.loc[data['Name'] == p]
               
                all_zasiegi =  check_unique_p(all_p, amz, lista, all_zasiegi, window, values)
               
        else:
            all_p = data[data.Name.isna()]
            all_zasiegi =  check_unique_p(all_p, amz, lista, all_zasiegi, window, values)
 
        n=n+1
        window['-PROGRESS_BAR2-'].update((n*25)/(len(uniqe_p)))
     

    save_output_shp(all_zasiegi, outputshp, values, lista, window)           
#------------------------------------------------------------------------------

def main():
    sg.theme('Reddit')
    
    file_list_column =[
        [
         sg.Text("Shapefile Folder"),
         sg.In(size=(25,1), enable_events=True, key='-Folder-'),
         sg.FolderBrowse(),
         ],
        [
         sg.Listbox(
             values=[], enable_events=True, size=(40,20),
             key='-File List-'
             )
            ],
            ]
    
    file_end_column =[
        [
         sg.Text("Folder Sekcje"),
         sg.Input(key='-Sekcje Folder-', size=(110,1)),
         sg.FileBrowse(file_types=("XLSX Files", "*.xlsx")),
         ],
        
         [sg.Text(f"Size of Buffer [meters]"),
                 sg.InputText('5',
                         key='-buffer-',),],
                
         [sg.Text("Output Shapefile Folder"),
              sg.In(size=(100,1), enable_events=True, key='-Output Folder-'),
         #sg.FolderBrowse(),
             sg.FileSaveAs(
                  key='-fig_save-',
                  initial_folder='/tmp',
                  file_types=(('.SHP', '.shp'),),  
       )],    
         [sg.Frame('Choose coordinate system', [ [
                sg.Radio('EPSG: 2176','epsg', key='2176'),
                sg.Radio('EPSG: 2177','epsg',key='2177'),
                sg.Radio('EPSG: 2178', 'epsg',key='2178'),
                sg.Radio('EPSG: 2179','epsg', key='2179')]])],
            
            [sg.Submit(), sg.Cancel()],
            [sg.Frame("Open all shapefiles", [ 
                [sg.ProgressBar(25, orientation='h', size=(100, 20), border_width=4, key='-PROGRESS_BAR-')]])],
                
            [sg.Frame("Generate all bounds", [ 
                [sg.ProgressBar(25, orientation='h', size=(100, 20), border_width=4, key='-PROGRESS_BAR2-')]])],
                
            
             [sg.Frame('K Error', [
                       [sg.Listbox(
                             values=[], enable_events=False, size=(100,5),
                             key='-Error-')] ])         
                            ],]
    
    
    
    #--------------full layout-----------------------------------------------------
    layout = [
        [sg.Column(file_list_column),
         sg.VSeparator(),
         sg.Column(file_end_column),
         ]
        ]
    
    window = sg.Window('Generate bounds', layout)
    
    
    #create an event loop
    while True:
        event, values = window.read()
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        
        elif event == '-Folder-':
            folder = values['-Folder-']
            try:
                file_list = os.listdir(folder)
            except:
                file_list =[]    
                
            fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder,f))
                and f.lower().endswith(('.shp'))
                ]
        
            window['-File List-'].update(fnames)
            
        elif event == '-fig_save-':
            filename = values['-fig_save-']
            if filename:
               window['-Output Folder-'].update(value=filename)
               print('Save As')
         
        elif event == 'Submit':
            zasieg(folder, fnames, values['-Output Folder-'], window, values)
            
    window.close()

    
if __name__ == "__main__":
    main()
