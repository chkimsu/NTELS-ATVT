from datetime import datetime
import os
import pandas as pd
import sys
import ktrain
from ktrain import text
import numpy as np
import pymysql
from datetime import datetime
import time
from nlpre import titlecaps, dedash, identify_parenthetical_phrases
from nlpre import replace_acronyms, replace_from_dictionary
from shutil import copyfile
import requests


def reinferencing(command):
    
    f = pd.read_csv('reinferencing_configure.csv')
    
    
    variable = []
    for i in range(len(f)):
        variable.append(f.Variable[i]) 

    data = []
    for i in range(len(f)):
        data.append(f.PATH[i]) 

    for i in range(len(variable)):
        globals()[variable[i]] = data[i] 
    
    
    predictor = ktrain.load_predictor(predictor_path)    
    
    if command == 'ALL':
               
        conn = pymysql.connect(host=host, port=int(port),
                                           user=user, password=password, db=db, charset=charset,
                                           cursorclass=pymysql.cursors.DictCursor)
        curs = conn.cursor()

        sql = sql_0
        curs.execute(sql)
        data0 = pd.DataFrame(curs.fetchall())

        sql = sql_1
        curs.execute(sql)
        data1 = pd.DataFrame(curs.fetchall())
        
        sql = sql_2
        curs.execute(sql)
        data2 = pd.DataFrame(curs.fetchall())
        
        data = pd.concat([data0, data1,data2])
        data = data.reset_index()
        
        
    
    elif command == 'CHANGED':
        
        
        conn = pymysql.connect(host=host, port=int(port),
                                           user=user, password=password, db=db, charset=charset,
                                           cursorclass=pymysql.cursors.DictCursor)
        curs = conn.cursor()

        sql = sql_2
        curs.execute(sql)
        data = pd.DataFrame(curs.fetchall())
        
     
        
        
    if data.empty == True:
        return 'There is no data'

    else: 

        os.chdir(PATH1)           

            ## 결과저장용 빈 데이터프레임 생성. 
        string = data[column1] + '_' + data[column2] + '_' + data[column3]
        result = pd.DataFrame(index=range(0, len(data)),
                                columns=[column4, column5, column6, column7, column8, column9, column10])
        result[[column4, column5, column6, column7, column8, column9, column10]] = data[[column4, column5, column6, column7, column8, column9, column10]]
        string = pd.DataFrame(string)
        string.columns = ['data']



        with open(infer_text,'w') as file:
            for line in string.data:
                file.writelines(line+'\n')
            file.close()


        leng = pd.read_csv(infer_text)
        f1 = open(infer_text,'rb')

        for i in range(len(leng)+1):
            text1 = str(f1.readline())


            ABBR = identify_parenthetical_phrases()(text1)
            parsers = [dedash(), titlecaps(), replace_acronyms(ABBR),
                        replace_from_dictionary(f_dict =dictionary ,prefix=prefix)]

            for f in parsers:
                text = f(text1)

            with open(inferresult_text, 'a') as file:
                file.writelines(text+'\n')
            file.close()


        os.remove(infer_text)
        os.remove(inferresult_text)


        now = datetime.now()
        result.model_version = now.strftime('%Y.%m.%d.')+ version



        equip = list(equipments)


        for i in range(len(data)):

            prediction = predictor.predict(string.data[i])
            now = datetime.now()

            for j in equip:
                if prediction.find(j) != -1:
                    test = prediction.lstrip(j)
                    test = test.lstrip()
                    break
            result.loc[i, [column9, column8,column10]] = j, test, now.strftime('%Y-%m-%d %H:%M:%S')


        for i in range(len(result)):
            if result[column9][i] in equip:
                result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
            else:
                result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'


        data[[column4, column5, column6, column7, column8, column9, column10]] = result[[column4, column5, column6, column7, column8, column9, column10]]
        


        headers = {'Content-Type': content_type}
        for i in range(len(data)):
            res = requests.post(url, headers=headers, data=data.iloc[i, :].to_json())
            
        return 'Reinferencing is Done'

