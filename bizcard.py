import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3
#from streamlit_html import html

def image_to_text(path):
    
    input_image = Image.open(path)

    #connvert image to array

    image_arr = np.array(input_image)

    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_arr, detail=0)
    
    return text, input_image


def extracted_text(texts):
    
    extracted_dict = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[],
                      "EMAIL":[], "WEBSITE":[], "ADDRESS":[], "PINCODE":[]}
    extracted_dict["NAME"].append(texts[0])
    extracted_dict["DESIGNATION"].append(texts[1])
    
    for i in range(2,len(texts)):
        
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and "-" in texts[i]):
            
            extracted_dict["CONTACT"].append(texts[i])
            
        elif "@" in texts[i] and ".com" in texts[i]:
           
           extracted_dict["EMAIL"].append(texts[i]) 
           
        elif "WWW" in texts[i] or  "www" in texts[i] or "Www" in texts[i] or  "wWw" in texts[i] or "wwW" in texts[i]:
            
            small = texts[i].lower()
            extracted_dict["WEBSITE"].append(small)
            
        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or "TN" in texts[i] or texts[i].isdigit():
            
            extracted_dict["PINCODE"].append(texts[i])
            
        elif re.match(r'^[A-Za-z]', texts[i]):
            
            extracted_dict["COMPANY_NAME"].append(texts[i])
            
        else:
            remove_colon = re.sub(r'[,;]', '', texts[i])
            extracted_dict["ADDRESS"].append(remove_colon)     
            
    for key,value in extracted_dict.items():  
        #print(key,":", value, len(value))     
        if len(value)>0:
            concadenate = " ".join(value)
            extracted_dict[key] = [concadenate]
            
        else:
            value = "NA"
            extracted_dict[key] = [value]
     
    return extracted_dict





# streamlit creation

st.set_page_config(layout="wide")

st.title(":violet[EXTRACTING BUSINESS CARD DATA WITH 'OCR' 💰]")

with st.sidebar:
    
    select = option_menu("Main Menu", ["Home 🏠", "Upload & Modify 🌀", "Delete ❌"])
    
    
    
if select == "Home 🏠":
    
    st.subheader(":green['OCR' - Optical Character Recognition ]")
    st.write(" * Optical Character Recognition (OCR) is a technology that converts printed or handwritten text into machine-readable text.")
    st.write(" * When applied to business card data extraction, OCR enables the digitization of contact information such as names, phone numbers, email addresses, company names, and addresses from the scanned image or photograph of a business card.")
    st.write(" *** :blue[  Upload your Bizcard and extracting the datas through the project] 🎯")
elif select == "Upload & Modify 🌀":
    
    img = st.file_uploader(":orange[**Upload Image Here 👇**]", type=["jpg", "png", "jpeg"])
    
    
    if img is not None:
        
        col1,col2,col3 = st.columns(3)
        
        with col2:
            st.image(img, width=800)
            
            text_image, input_image = image_to_text(img)
            
            text_dict = extracted_text(text_image)
        
        if text_dict:
            st.success("TEXT IS  SUCCUFULLY EXTRACTED FROM THE IMAGE 👍")
            
        df = pd.DataFrame(text_dict)
        
        # converting image to bytes

        Image_bytes = io.BytesIO()
        input_image.save(Image_bytes, format= "PNG")

        image_data = Image_bytes.getvalue()
        


        #creating dictionary

        data = {"IMAGE":[image_data]}
        df_1 = pd.DataFrame(data)

        concat_df = pd.concat([df,df_1], axis=1)
        st.dataframe(concat_df)
        
        col1,col2,col3 =st.columns(3)
        with col2:
        
          button_1 = st.button(":orange[Save]", use_container_width = True)
        
        if button_1:
            
            # sql connection

            mydb = sqlite3.connect("bizcardx.db")
            cursor = mydb.cursor()

            #Table creation

            create_table_query = '''CREATE TABLE IF NOT EXISTS bizcardx_details(name VARCHAR(255),
                                                                                designation VARCHAR(255),
                                                                                company_name VARCHAR(255),
                                                                                contact VARCHAR(255),
                                                                                email VARCHAR(255),
                                                                                website TEXT,
                                                                                address TEXT,
                                                                                pincode VARCHAR(255),
                                                                                image text)'''
                                                                                
            cursor.execute(create_table_query)
            mydb.commit()
            
            #insert queries

            insert_query = '''INSERT INTO bizcardx_details(name, designation, company_name, contact, email, 
                                                        website, address, pincode, image )
                                                        
                                                        VALUES(?,?,?,?,?,?,?,?,?)'''
                                                        
            datas = concat_df.values.tolist()[0]
            cursor.execute(insert_query, datas)
            mydb.commit()
            
            st.success("Successfully Saved 👍")

    col1,col2,col3 = st.columns(3)
    with col2:       
     method = st.radio(":orange[SELECT THE METHOD] 🔎", ["None", "Preview", "Modify"])
    

    if method == "None":
        col1,col2,col3 = st.columns(3)
        with col2:
        
              st.write("")

    if method == "Preview":
        
        #select query 
        mydb = sqlite3.connect("bizcardx.db")
        cursor = mydb.cursor()

        select_query = "SELECT * FROM bizcardx_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                                "ADDRESS", "PINCODE", "IMAGE"))
        st.dataframe(table_df)

    elif method == "Modify":
        
        #select query 
        mydb = sqlite3.connect("bizcardx.db")
        cursor = mydb.cursor()

        select_query = "SELECT * FROM bizcardx_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        mydb.commit()

        table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                                "ADDRESS", "PINCODE", "IMAGE"))
        
        col1,col2 = st.columns(2)
        with col1:
            
            selected_name = st.selectbox(":orange[SELECT THE NAME] 🔎", table_df["NAME"])
            
        df_3 = table_df[table_df["NAME"] == selected_name]

        
        df_4 = df_3.copy()
        
        
        
        col1 ,col2 = st.columns(2)
        
        with col1:
            modify_name = st.text_input(":blue[NAME]",df_3["NAME"].unique()[0])
            modify_degi = st.text_input(":blue[DESIGNATION]",df_3["DESIGNATION"].unique()[0])
            modify_com_name = st.text_input(":blue[COMPANY_NAME]",df_3["COMPANY_NAME"].unique()[0])
            modify_contact = st.text_input(":blue[CONTACT]",df_3["CONTACT"].unique()[0])
            modify_email = st.text_input(":blue[EMAIL]",df_3["EMAIL"].unique()[0])
            
            df_4["NAME"] = modify_name
            df_4["DESIGNATION"] = modify_degi
            df_4["COMPANY_NAME"] = modify_com_name
            df_4["CONTACT"] = modify_contact
            df_4["EMAIL"] = modify_email
            
            
        with col2:
            modify_web = st.text_input(":blue[WEBSITE]",df_3["WEBSITE"].unique()[0])
            modify_address = st.text_input(":blue[ADDRESS]",df_3["ADDRESS"].unique()[0])
            modify_pin = st.text_input(":blue[PINCODE]",df_3["PINCODE"].unique()[0])
            modify_image = st.text_input(":blue[IMAGE]",df_3["IMAGE"].unique()[0])
            
            df_4["WEBSITE"] = modify_web
            df_4["ADDRESS"] = modify_address
            df_4["PINCODE"] = modify_pin
            df_4["IMAGE"] = modify_image
            
        st.dataframe(df_4)
        
        col1,col2,col3 = st.columns(3)
        with col2:
            button_2 = st.button(":orange[Modify]", use_container_width=True)
            
        if button_2:
                
            mydb = sqlite3.connect("bizcardx.db")
            cursor = mydb.cursor()
            
            cursor.execute("DELETE FROM bizcardx_details WHERE NAME = '{selected_name}'")
            mydb.commit()
            
            insert_query = '''INSERT INTO bizcardx_details(name, designation, company_name, contact, email, 
                                                                website, address, pincode, image )
                                                                
                                                                VALUES(?,?,?,?,?,?,?,?,?)'''
                                                                
            datas = df_4.values.tolist()[0]
            cursor.execute(insert_query, datas)
            mydb.commit()
            
            st.success("Successfully Modified 👍")
                                                
                                               
            
            
elif select == "Delete ❌":
    
    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()
    
    col1,col2 = st.columns(2)
    with col1:
        
        #select query 
        select_query = "SELECT NAME FROM bizcardx_details"

        cursor.execute(select_query)
        table1 = cursor.fetchall()
        mydb.commit()

        names = []

        for i in table1:
            names.append(i[0])
            
        names_selected = st.selectbox(":orange[SELECT THE NAME] 🔎", names)
    
    with col2:
        
        #select query 
        select_query = "SELECT DESIGNATION FROM bizcardx_details"

        cursor.execute(select_query)
        table1 = cursor.fetchall()
        mydb.commit()

        designations = []

        for i in table1:
            designations.append(i[0])
            
        designation_selected = st.selectbox(":orange[SELECT THE DESIGNATION] 🔎", designations)
        
    if names_selected and designation_selected:
        col1,col2,col3 = st.columns(3)
        
        with col1:
            st.write(f":blue[SELECTED NAME] : {names_selected}")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
        with col3:
            st.write(f":blue[SELECTED DESIGNATION] : {designation_selected}")
            
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
        
            
            remove = st.button(":orange[Delete]", use_container_width= True)
            
            if remove:
                
                cursor.execute(f"DELETE FROM bizcardx_details WHERE NAME = '{names_selected}' AND DESIGNATION = '{designation_selected}' ")
                mydb.commit()
                
                st.warning("Deleted")





