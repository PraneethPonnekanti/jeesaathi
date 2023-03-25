# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 03:52:11 2021

@author: Praneeth Ponnekanti
"""

import pandas as pd
import streamlit as st 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64,io
import pygsheets as pyg
from datetime import date
import time 
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive
#from google.colab import auth
#from oauth2client.client import GoogleCredentials

    


# Data Preprocessing section starts here. 


##### JOSAA Round 1



r1 = pd.read_csv("./Inputs/Josaa_R1.csv")
r2 = pd.read_csv("./Inputs/Josaa_R2.csv")
r3 = pd.read_csv("./Inputs/Josaa_R3.csv")
r4 = pd.read_csv("./Inputs/Josaa_R4.csv")
r5 = pd.read_csv("./Inputs/Josaa_R5.csv")
r6 = pd.read_csv("./Inputs/Josaa_R6.csv")
college_states = pd.read_csv("./Inputs/Josaa_College_States.csv")
domicile_states = pd.read_csv("./Inputs/josaa_domicile_states.csv")
josaa_business_rules = pd.read_csv("./Inputs/josaa_business_rules.csv")
course_df = pd.read_csv("./Inputs/josaa_courses.csv")
#josaa_br_unstacked = josaa_business_rules.explode('Homestate')



r1['Round'] = 1
r2['Round'] = 2
r3['Round'] = 3
r4['Round'] = 4
r5['Round'] = 5
r6['Round'] = 6


def insti_type(df):
    if 'Indian Institute of Technology' in df:
        return "IIT"
    if 'National Institute of Technology' in df:
        return "NIT"
    if 'Indian Institute of Information Technology' in df:
        return "IIIT"
    if 'School of Planning & Architecture' in df:
        return "SPA"
    else :
        return "GFTI"
    
def is_barch(df):
    if 'Architecture' in df :
        return True
    else : 
        return False


def df_to_plotly(df):
    #col_list = list(df.columns)
    fig = go.Figure(data = go.Table(header = dict(values = list(df.columns),
                                                  align = 'left', fill_color = "#FD8E72"), 
                                    cells = dict(values = df.transpose().values ,
                                                 align = 'left', fill_color = "#E5ECF6"),
                                    )
                    )
    #fig.update_layout(margin = dict(l=5,r=5,b=5,t=5), paper_bgcolor = "#F5F5F5")
    fig.update_layout(margin = dict(l=5,r=5,b=5,t=5), paper_bgcolor = "#F5F5F5")
    
    
    st.write(fig)
    #return fig
    
def find_applicable_quotas(dom_state,df):
    '''

    Parameters
    ----------
    dom_state : String
        DESCRIPTION.
    df : Dataframe
        Check for the quotas in df['Quota'] and split Quotas into HS, Non HS.
        1. Candidate from AP should not see HS,JK,LA quotas in their search results. 

    Returns
    -------
    List of applicable quotas

    '''
    quota_list = list(df.Quota.unique()) #List of all quotas
    #non_hs_quota = quota_list.remove('HS') #remove all states
    special_quotas = {'GO','JK','LA'}
    special_states = ['Goa', 'Jammu and Kashmir', 'Ladakh']
    if dom_state not in special_states:
        appl_quota = [q for q in quota_list if q not in special_quotas] #all applicable quotas before homestate/non-homestate quota filtering 
    else :
        if dom_state == 'Goa' :
            appl_quota = [g for g in quota_list if g not in ['JK', 'LA']] #Goans shouldn't be displayed seats under JK,LA quota
        if dom_state == 'Jammu and Kashmir' :
            appl_quota = [j for j in quota_list if j not in ['GO', 'LA']] #Jammu Kashmir candidates can't be displayed seats under GO,LA quotas
        if dom_state == 'Ladakh' :
            appl_quota = [la for la in quota_list if la != 'GO'] #Ladkah candidates are eligible for JK quota, HS but can't be shown seats under GO quota. 
        #if dom_state in ['Arunachal Pradesh','Assam','Nagaland', 'Manipur', 'Meghalaya', 'Mizoram', 'Sikkim', 'Tripura']:
        #    if df['Institute'].str.contains('Ghani') :
        #        appl_quota = [i for i in quota_list if i not in special_quotas]
    return appl_quota
            
def eq_hs_nit (appl_state, df):
    eq_hs = df['josaa_hs_nit'][df['Domicile State'] == appl_state].reset_index(drop = True)
    print(type(eq_hs[0]))
    return eq_hs[0]

def search_results_adv(jee_rank,rank_var,inp_st,df,round_no,inst_bucket,locations):
    if int(jee_rank)< int(rank_var):
        rank_var = jee_rank
    
    result_df = pd.DataFrame(columns = df.columns)
    result_df = df[(df['Seat Type'] == inp_st) & (df['Institute Type'].isin(inst_bucket)) & (df['BArch'] == "No")].copy()
    #inp_inst_type = st.sidebar.selectbox("Select Institute Types : ", master_df['Institute Type'].unique())
    #result_df = result_df[result_df['Quota'].isin(app_quotas)]
    result_df = result_df[result_df['Round'].isin(round_no)]
    result_df = result_df[result_df['Location'].isin(locations)]
    #result_df = result_df[result_df['Branch_master'].isin(branch_bucket)]
    #print (result_df)
    result_df = result_df[result_df['Closing Rank'] >= (int(jee_rank) - int(rank_var))].copy()
    print(result_df)
    if (inp_gender == 'Male'):
        result_df = result_df[result_df['Gender'] == 'Gender-Neutral']
    
    # Split applicable homestate and other state quota into two different dataframes. 
    
    #result_hs_df = result_df[result_df['Location'] == dom_state]
    #elg_quotas = find_applicable_quotas(d_state,result_df)
    #elg_non_hs_quotas = [nhs for nhs in elg_quotas if nhs != 'HS']
    #result_hs_df = result_df[(result_df['Location'] == d_state)]
    #result_non_hs_df = result_df[result_df['Quota'].isin(elg_non_hs_quotas)]
    
    #final_result_df = pd.concat([result_hs_df,result_non_hs_df],ignore_index=True)
    
    final_result_df = result_df[['Institute', 'Academic Program Name', 'Course Duration', 'Seat Type','Quota', 'Gender', 'Round', 'Opening Rank', 'Closing Rank', 'Location']]
    final_result_df = final_result_df.sort_values(['Closing Rank','Opening Rank'],ascending=True)
    st.subheader("Your Search Results : ")
    st.dataframe(final_result_df)
    #df_to_plotly(final_result_df)
    return final_result_df
        #st.write(result_df)

def get_table_download_link(df,name):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    op_file = "JeeSaathi_SearchResults_"+name+"_.csv"
    csv = df.to_csv(op_file,index=False)
    st.success("Downloading of file : " + op_file + " is completed.")
    #b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    #print("b64", b64)
    #href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return op_file

def download_table(df,name):
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    op_file = "JeeSaathi_Adv_SearchResults_"+name+".xlsx"
    sheet_fmt = name+"_"+str(time.strftime('%d-%m-%Y'))
    output = io.BytesIO()
    # Use the BytesIO object as the filehandle
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    # Write the data frame to the BytesIO object and save it
    df.to_excel(writer, sheet_name = sheet_fmt,index = False)
    writer.save()
    output.seek(0)
    excel_data = output.getvalue()
    #b64 = base64.b64encode(excel_data)
    #payload = b64.decode()
    b64 = base64.urlsafe_b64encode(excel_data).decode()
    # Create a link to download the file
    
    #st.markdown("#### Download the above table as an excel file ###")
    #href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" target="_blank">Click here to download the table results in an Excel file!</a>'
    #html = f'<a download="{op_file}" href="data:text/xml;base64,{payload}" target="_blank">Click here to download the table results in an excel file !</a>'
    html = f'<a download="{op_file}" href="data:text/xml;base64,{b64}">Click here to download the table results in an excel file !</a>'
    #html = f'<a download="{op_file}" href="data:application/vnd.ms-excel.spreadsheetml.sheet;base64,{b64}">Click here to download the table results in an excel file !</a>'
    #html = f'<a download="{op_file}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(open(op_file, "rb").read()).decode()}">Click here to download the table results in an Excel file!</a>'
    #timestr = time.strf()
    #csv = df.to_csv(op_file,index=False)
    #df_dict = df.to_dict('list')
    #b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    #print("b64", b64)
    
    #href = f'<a href="data:file/csv;base64,{b64}" download = "csv">Download csv file</a>'
    st.markdown(html,unsafe_allow_html=True)
    #st.success("Downloading of file : " + op_file + " is completed.")
    return


def sort_list(_input):
    _input.sort()
    return _input

append_df = pd.concat([r1,r2,r3,r4,r5,r6],ignore_index=True)
append_df = append_df.dropna()

inst_list = pd.DataFrame(append_df.Institute.unique(),columns = ['Institute'])

gender_list = list(append_df.Gender.unique())

quota_list = list(append_df.Quota.unique())

append_df['Institute Type'] = append_df['Institute'].apply(insti_type)

append_df['Course Duration'] = append_df['Academic Program Name'].str.extract('(\d+)').astype(int)



#course_list = pd.DataFrame(append_df['Academic Program Name'].unique(),columns = ['Program'])
#append_df['BArch'] = append_df['Academic Program Name'].apply(is_barch)

append_df['BArch'] = np.where(append_df['Academic Program Name'].str.contains("of Architecture|Planning", regex=True), "Yes", "No")

append_df['Jee_Adv_flag'] = np.where(append_df['Institute Type'] == 'IIT', True,False)

master_df = append_df.merge(college_states, on = 'Institute').merge(course_df, on = 'Academic Program Name').copy()

#Clean Alphabets from the Opening and Closing Rank Columns
master_df['Opening Rank'] = master_df['Opening Rank'].str.replace(r'[^\d.]+', '').astype(int)
master_df['Closing Rank'] = master_df['Closing Rank'].str.replace(r'[^\d.]+', '').astype(int)
master_df['Institute'] = master_df['Institute'].str.replace('National Institute of Technology, ', 'NIT ').replace('Indian Institute of Technology,','IIT ')
master_df['Institute'] = master_df['Institute'].str.replace('Indian Institute of Information Technology,', 'IIIT ')
master_df['Institute'] = master_df['Institute'].str.replace("Indian institute of information technology,","IIIT ")
master_df['Institute'] = master_df['Institute'].str.replace('Indian Institute of Information Technology', 'IIIT ').replace("(IIIT)","")
master_df['Institute'] = master_df['Institute'].str.replace('National Institute of Technology', 'NIT ').replace('Indian Institute of Technology','IIT ')

master_df['Location'] = master_df['Location'].str.strip()
#master_df['Disability'] = np.where(master_df['Seat Type'].str.contains("(PwD)"), True, False) 
#course_list['Branch_master'] = course_list['Program'].str.extract(r'^(.*?)Engineering', expand = True)

#Convert relevant columns to int

int_columns = ['Opening Rank', 'Closing Rank', 'Round', 'Course Duration']
   
inst_type = list(master_df['Institute Type'].unique())

#Select only IIT's and SPA's for JEE Advanced Predictions
#unwanted_engg_adv_inst = {'IIT'}
wanted_engg_mains_inst = {'IIT'}
inst_type = [ele for ele in inst_type if ele in wanted_engg_mains_inst]



    
#Streamlit configuration goes in here.

st.cache(super)

st.header("Jee Advanced 2022 : College Predictor ")
st.markdown('''
            ###### College Predictor based on the data from [JOSAA 2021 Opening & Closing Ranks](https://josaa.admissions.nic.in/applicant/seatmatrix/OpeningClosingRankArchieve.aspx) 
              
             **Mobile user ?** please press the `>` button at the top-left corner on the page for the sidebar.  
               
             * Wanna checkout NIT/IIIT/GFTI's using your JEE Mains rank ? Checkout our [JEE Mains Predictor](https://share.streamlit.io/praneethponnekanti/jeesaathi/main/josaa_counselling.py)   
              
            **Credits :** App built in `Python` + `Streamlit` by [Praneeth Ponnekanti](https://www.linkedin.com/in/praneeth-ponnekanti/)  
              
              
            
            
            ''')
#@stcache;

col1, col2, col3 = st.columns(3)
name = col1.text_input("Your Name : ")
with open('user_name.txt', 'w') as r:
    r.write(",".join(name))
email = col2.text_input("Your Email ID : ")
phone = col3.text_input("Your Phone Number : ")

#st.session_state['name'] = name
#st.sesson_state['email'] = email
#st.session_state['phone'] = phone

_inp_rank = st.number_input("Type in your JEE Advanced category rank to search (CRL Rank for OPEN category). Default rank value is 1. ", min_value = 1,key = 'rank')
#inp_category = s1.selectbox("Select Your Category", master_df['Seat Type'].unique())
inp_category = st.sidebar.selectbox("Select Your Category", master_df['Seat Type'].unique(), key ='category')
#inp_gender = s1.radio("Select Your Gender : ", ('Male', 'Female'))
inp_gender = st.sidebar.radio("Select Your Gender : ", ('Male', 'Female'), key ='Gender')
#inp_dom_state = s1.selectbox("Select your domicile state : ",domicile_states['Domicile State'].unique())
#inp_dom_state = st.sidebar.selectbox("Select your domicile state : ",domicile_states['Domicile State'].unique(), key ='Domicile State')
#inp_inst_type = s1.multiselect("Select Institute Types : ", inst_type,default=['NIT'])
inp_inst_type = st.sidebar.multiselect("Select Institute Types : ", inst_type, default = inst_type)
#inp_round = s1.multiselect("Counselling Round : ", master_df['Round'].unique(),default=1)
inp_round = st.sidebar.multiselect("Counselling Round : ", master_df['Round'].unique(),default=1)
#inp_jee_flag = st.sidebar.radio('Have you qualified JEE Advanced ?', ('Yes', 'No'))
st.markdown(" **Closing ranks tend to vary each year by some number X.**")
inp_rank_var = st.slider("Select the number X from the slider",0,min(_inp_rank,3000), key = 'rank_Var')
#inp_branch_selector = s2.multiselect("Select Courses : ", master_df['Branch_master'].unique(), default = list(master_df['Branch_master'].unique()))
#inp_branch_selector = st.sidebar.multiselect("Select Courses : ", master_df['Branch_master'].unique(), default = list(master_df['Branch_master'].unique()))
location_master = list(master_df['Location'].unique())
location_sel = sort_list(location_master)
inp_loc_selector = st.sidebar.multiselect("Select your preferred institutes locations : ", location_sel, default = location_sel)
#sh = gc.open('JOSAA_Counsellor_subbase')


#sub_base = pd.DataFrame(columns = ['Name', 'Category', 'Date', 'E-mail', 'Phone', 'Domicile State'])
lines = [name,str(_inp_rank),inp_category,email,str(phone)]
with open('user_base.csv', 'w') as f:
    f.writelines(lines)
    

#wks.ins
#wks.set_dataframe(sub_base,(1,1))

def main():
    if _inp_rank == '' or name == '' : 
    #or not _inp_rank.isnumeric():
            st.warning("Please provide your name to proceed further.")
    else : 
        
        st.write ("Hi " + name + ", thanks for using JEE Counsellor.")
        st.write("Your Rank is " + str(_inp_rank) +" in " + str(inp_category) + " category. ")
        st.write("Selected rank variance value :" + str(inp_rank_var) + " . Hence, displaying search results from rank : ", int(_inp_rank) - int(inp_rank_var))
        
        col_e1,col_b1,col_e2 = st.columns(3)
        
        if col_b1.button("Submit and Search"):
        
            c_result_df = search_results_adv(_inp_rank,inp_rank_var,inp_category,master_df,inp_round,inp_inst_type,inp_loc_selector)
            
            col5,col6 = st.columns(2)
            
            #if(col5.button("Download the table results as an excel file.", )):
                #op_file = get_table_download_link(c_result_df,name)
            download_table(c_result_df,name)
            #if(col6.button("Send to email")):
            #body = "Hi " + name + ", thanks for using JEE Counsellor." +'\n' + "Your Rank is " + str(_inp_rank) +" in " + str(inp_category) + " category, Your domicile state is " + inp_dom_state +"."+"Selected rank variance value :" + str(inp_rank_var) + ". Hence, displaying search results from rank : ", int(_inp_rank) - int(inp_rank_var)
                #send_email(email,op_file,body)
            
        #col_dl,col_link = st.columns(2)
            #col_dl.markdown(get_table_download_link(c_result_df), unsafe_allow_html=True)
            #sub_base['Status'] = 'Downloaded result file.'
    #return c_result_df


main()


    
  



