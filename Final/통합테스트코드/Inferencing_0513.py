from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
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


## configure 불러오는 부분. 
## 이 부분은 configure에 넣어줄 필요는 없다. 다만, configure파일은 무조건 파이썬 파일과 동일 디렉터리에. 
f = pd.read_csv('/data01/CSB/CSB_Jupyter/ATVT/ariflow/dags/Inferencing_configure.csv', encoding='utf-8')
## configure에서 가져온 변수명과 configure data혹은 path들을 할당해준다. 
## 이 부분은 어차피 전역 변수라 모듈화에서 빼고 한다. 
variable = []
for i in range(len(f)):
    variable.append(f.Variable[i]) 

datav = []
for i in range(len(f)):
    datav.append(f.PATH[i]) 

for i in range(len(variable)):
    globals()[variable[i]] = datav[i] 
    

    
    
    

## db에서 데이터 호출하는 함수.     
def db_connect(command):
    
    if command == 'yys':
        
    
        conn = pymysql.connect(host=host, port=int(port),
                                           user=user, password=password, db=db, charset=charset,
                                           cursorclass=pymysql.cursors.DictCursor)
        curs = conn.cursor()

        sql1 = sql_1
        curs.execute(sql1)
        data1 = pd.DataFrame(curs.fetchall())

        sql2 = sql_2
        curs.execute(sql2)
        data2 = pd.DataFrame(curs.fetchall())


        sql3 = ''' SELECT * FROM t_points_atvt WHERE tagged ='y' AND changed = 'y' AND inferenced = 's';  '''
        curs.execute(sql3)
        data3 = pd.DataFrame(curs.fetchall())



        sql4 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'f';  '''
        curs.execute(sql4)
        data4 = pd.DataFrame(curs.fetchall())



        sql5 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'n' AND inferenced = 'f';  '''
        curs.execute(sql5)
        data5 = pd.DataFrame(curs.fetchall())



        data = pd.concat([data1,data2,data3,data4,data5])
        data = data.reset_index(drop=True)
        
        
        
        index = []

        for i in range(len(data)):
            if (data.loc[i, 'id'] == 'null') | (data.loc[i, 'description'] == 'null') | (data.loc[i, 'name'] == 'null') | (data.loc[i, 'present_value'] == 'null') | (data.loc[i, 'id'] == '') | (data.loc[i, 'description'] == '') | (data.loc[i, 'name'] == '') | (data.loc[i, 'present_value'] == '') | (data.loc[i, 'id'] == None) | (data.loc[i, 'description'] == None) | (data.loc[i, 'name'] == None) | (data.loc[i, 'present_value'] == None):  
                index.append(i)
        
        ## 이건 null 혹은 빈 string있는 data
        data_null = data.loc[index].reset_index(drop = True)
        ## 이건 정상 데이터.
        data_notnull = data.loc[list(set(list(data.index)) - set(index))].reset_index(drop=True)
        
        
              
        return data_null, data_notnull

    
    
    else:
        
        
        conn = pymysql.connect(host=host, port=int(port),
                                           user=user, password=password, db=db, charset=charset,
                                           cursorclass=pymysql.cursors.DictCursor)
        curs = conn.cursor()

        sql1 = sql_1
        curs.execute(sql1)
        data1 = pd.DataFrame(curs.fetchall())

        sql2 = sql_2
        curs.execute(sql2)
        data2 = pd.DataFrame(curs.fetchall())


        sql4 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'y' AND inferenced = 'f';  '''
        curs.execute(sql4)
        data4 = pd.DataFrame(curs.fetchall())



        sql5 = ''' SELECT * FROM t_points_atvt WHERE tagged ='n' AND changed = 'n' AND inferenced = 'f';  '''
        curs.execute(sql5)
        data5 = pd.DataFrame(curs.fetchall())



        data = pd.concat([data1,data2,data4,data5])
        data = data.reset_index(drop=True)
    
   
                     
            
            
        index = []
            
        for i in range(len(data)):
            if (data.loc[i, 'id'] == 'null') | (data.loc[i, 'description'] == 'null') | (data.loc[i, 'name'] == 'null') | (data.loc[i, 'present_value'] == 'null') | (data.loc[i, 'id'] == '') | (data.loc[i, 'description'] == '') | (data.loc[i, 'name'] == '') | (data.loc[i, 'present_value'] == '') | (data.loc[i, 'id'] == None) | (data.loc[i, 'description'] == None) | (data.loc[i, 'name'] == None) | (data.loc[i, 'present_value'] == None):  
                index.append(i)

        ## 이건 null 혹은 빈 string있는 data
        data_null = data.loc[index].reset_index(drop = True)
        ## 이건 정상 데이터.
        data_notnull = data.loc[list(set(list(data.index)) - set(index))].reset_index(drop=True)

        
        return data_null, data_notnull

    
## 결과 저장용 빈 데이터프레임 생성


def empty_dataframe(data):
    
        ## 결과저장용 빈 데이터프레임 생성. 
    string = data[column1] + '_' + data[column2] + '_' + data[column3]
    result = pd.DataFrame(index=range(0, len(data)),
                            columns=[column4, column5, column6, column7, column8, column9, column10])
    result[[column4, column5, column6, column7, column8, column9, column10]] = data[[column4, column5, column6, column7, column8, column9, column10]]
    string = pd.DataFrame(string)
    string.columns = ['data']

    return string, result



## nlpre이용하여 축약어 푸는 과정. 
def nlpre_execute(leng, f, f1):
    
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
        
        return 'nlpre Success'
    

    
    

    
    
    
    
## 실제 prediction하는 부분.
def predict(data, string, predictor, equip, result):
    
    
    
    for i in range(len(data)):

        prediction = predictor.predict(string.data[i])
        now = datetime.now()
        
       
    ## IDK로 예측해줄 경우는 Idk로 예측하도록 해주는 코드
    
        if prediction == 'idk':
            
            result.loc[i, [column9, column8,column10]] = 'idk', 'idk', now.strftime('%Y-%m-%d %H:%M:%S')

        ## IDK 외에 나머지 코드
        
        else:      
        
            for j in equip:
                if prediction.find(j) != -1:
                    test = prediction.lstrip(j)
                    test = test.lstrip()
                    break
            result.loc[i, [column9, column8,column10]] = j, test, now.strftime('%Y-%m-%d %H:%M:%S')


        
       
    ## IDK 있을 경우에는 자동으로 추론실패로 들어가도록 코드가 짜여 있다. 왜냐하면 IDK는 equip안에 없으므로. 
    ## yys가 있을 경우, 없을 경우 여기 코드에서 고칠건없다. 

    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='n')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='n')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'y') & (result['changed'] == 'y') & (result['inferenced'] =='s')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 'f'

    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='f')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='f')].index:
        if result[column9][i] in equip:
            result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 's'
        else:
            result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    
    data[[column4, column5, column6, column7, column8, column9, column10]] = result[[column4, column5, column6, column7, column8, column9, column10]]
    
    
    return result, data
    

    
### 4가지중에 하나라도 null 혹은 빈 string인 경우. 
def predict_null(result):
    
    
    
    now = datetime.now()
    
    for i in range(len(result)):
        result.inference_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='n')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='n')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'y') & (result['changed'] == 'y') & (result['inferenced'] =='s')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'y', 'n', 'f'

    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'y') & (result['inferenced'] =='f')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
    
    for i in result[(result['tagged'] == 'n') & (result['changed'] == 'n') & (result['inferenced'] =='f')].index:
        result[column4][i], result[column5][i], result[column6][i] = 'n', 'n', 'f'
            
    return result
    
    
    
    
    
## api에 json 보내는 부분
def API_Request(data):
    
    headers = {'Content-Type': content_type}
    for i in range(len(data)):
        res = requests.post(url, headers=headers, data=data.iloc[i, :].to_json())
        print(res)
    
    return 'API_Requested'







def at_gateway_inference_task():

    ## 예측모델 호출
    predictor = ktrain.load_predictor(predictor_path)    

    
    print(time.strftime('%c', time.localtime(time.time())))
    ## db에서 데이터 호출
    
    ## yys들어갈경우 command = yys
    ## 아닐경우 그냥 아무 값으로 
    
    data_null, data_notnull = db_connect(command = 'yys')
    


    ## db에 조건에 맞는 데이터 없을 경우에 Fail을 뜨게 한다. 
    if data_notnull.empty == True:
        
        
        if data_null.empty==True:
        
            return 'There is nothing to do'
        
        else:
            data_null = predict_null(data_null)
            data = data_null.copy()

    else: 

        os.chdir(PATH1)           
        ## 결과저장용 빈 데이터프레임 생성. 
        string, result = empty_dataframe(data_notnull)

        ## 데이터 조작하는 과정.        
        with open(infer_text,'w') as file:
            for line in string.data:
                file.writelines(line+'\n')
            file.close()

        leng = pd.read_csv(infer_text)
        f1 = open(infer_text,'rb')

        ## NLPRE 이용하여 축약어 푸는 과정
        nlpre_execute(leng, f, f1)

        ## 필요없는 폴더는 삭제한다.  
        os.remove(infer_text)
        os.remove(inferresult_text)

        ## 모델버전앞에 현재 날짜 써주기. 
        now = datetime.now()
        result.model_version = now.strftime('%Y.%m.%d.')+ version


        ## AHU, Boilers등    
        equip = ['vfds', 'elec', 'zones', 'ahus', 'vavs', 'chillers', 'boilers', 'tanks']

        ## null값들에 대해 예측하는 부분
        
        if data_null.empty ==True:
            
            result, data_notnull = predict(data_notnull, string, predictor, equip, result)
            data = data_notnull.copy()
            
        else:
            data_null = predict_null(data_null)
            result, data_notnull = predict(data_notnull, string, predictor, equip, result)
            data = pd.concat([data_null, data_notnull]).reset_index(drop=True)
            
           
        print(time.strftime('%c', time.localtime(time.time())))
    
    
    API_Request(data)


    return 'Inferencing is Done'
        
        
        

## airflow 함수의 시작. 

      
dag = DAG(dags_name, description=description,
          schedule_interval=schedule,
          start_date=datetime(int(now_year),int(now_month),int(now_date)), catchup=False)

dummy_operator = DummyOperator(task_id=dummytask_id, retries=1, dag=dag)

gateway_inference_operator = PythonOperator(task_id=pythontask_id,
                                            python_callable=at_gateway_inference_task, dag=dag)

dummy_operator >> gateway_inference_operator