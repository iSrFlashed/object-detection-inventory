import streamlit as st
from PIL import Image
from app.Upload.Upload_ui import process_image,NumberImagesProcessedByDate,DetectedAndMissingProducts,TotalProductsDetected,ImageDetectionReport,ImageS3,ImageDetectionAll
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.express as px
import logging
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
LOGGER = logging.getLogger(__name__)
st.set_page_config(page_title="Image Classifier", page_icon="📷", layout="wide")

def decode_base64(base64_string):
    img_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(img_data))

st.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
            padding: 20px;
        }
        .report-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)


def show_sidebar():
    with st.sidebar:
        st.markdown("## 📌 Dashboard")
        menu = st.radio("Select section", ("🏞️ Image Detection", "📊 Reports"))
    return menu

def show_content(menu):
    if menu == "🏞️ Image Detection":
        st.session_state.dataframe = None
        st.session_state.selected_row = None
        st.markdown("# 📸 Image Detection")
        detection_option = st.selectbox("Select type", ("Image"))

        if detection_option == "Image":
            st.subheader("🖼️ Image analysys")
            uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

            if uploaded_file is not None:
                response = process_image(st.session_state.token, uploaded_file)
                if response.status_code == 200:
                    result = response.json()
                    if result["status_code"] == 200:
                        detected_image_base64 = result["detected_image"]

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("### Original")
                            original_image = Image.open(uploaded_file)
                            st.image(original_image, caption="Original", use_container_width=True)


                        with col2:
                            st.write("### Detected")
                            detected_image = decode_base64(detected_image_base64)
                            st.image(detected_image, caption="Detected", use_container_width=True)


                        st.write("### Statistics")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("#### Amount of images processed")

                            responsedf = NumberImagesProcessedByDate(st.session_state.token)

                            if responsedf.status_code == 200:
                                resultdf = responsedf.json()
                               
                                if resultdf["status_code"] == 200:
                                    df = df = pd.DataFrame(resultdf["df"])
                                    if not df.empty:
                                       
                                        latest_date = df.iloc[-1]["date"]
                                        #latest_total = df.iloc[-1]["total"]
                                        st.write(f"### 📅 Processed images on **{latest_date}**")


                                        #st.metric(label=f"Imágenes procesadas el {latest_date}", value=latest_total)

                                        fig, ax = plt.subplots(figsize=(10, 6))  # Tamaño de la figura más grande para mejor visibilidad
                                        ax.bar(df["date"], df["amount"], color='royalblue', edgecolor='darkblue', width=0.7, label="Processed Images")

                                        ax.set_xlabel("Date", fontsize=14, labelpad=15)
                                        ax.set_ylabel("Amount of images", fontsize=14, labelpad=15)
                                        ax.set_title("Images Processed per Day", fontsize=16, fontweight='bold', pad=20)

                                        plt.xticks(rotation=45, ha='right', fontsize=12)
                                        plt.yticks(fontsize=12)

                                        ax.grid(True, linestyle='--', alpha=0.7, axis='y', linewidth=0.7)

                                        for spine in ax.spines.values():
                                            spine.set_edgecolor('gray')
                                            spine.set_linewidth(0.5)

                                       
                                        ax.legend(fontsize=12)

                                       
                                        plt.tight_layout()

                                        
                                        st.pyplot(fig)
                        with col2:
                            st.write("#### Detected and missing products")
                            responsedf = DetectedAndMissingProducts(st.session_state.token,result["id_image"])
                            if responsedf.status_code == 200:
                               resultdf = responsedf.json()
                              
                               if resultdf["status_code"] == 200:
                                    df = df = pd.DataFrame(resultdf["df"])
                                    if not df.empty:
                                    
                                        st.write("### 📅 Processed image information:")
                                  

                                       
                                        df["total_detected"] = df["total_detected"].fillna(0).astype(float)
                                        df["total_missing"] = df["total_missing"].fillna(0).astype(float)

                                        
                                        total_detectados = df["total_detected"].sum()
                                        total_faltantes = df["total_missing"].sum()

                                      
                                        labels = ["Detected Products", "Missing Products"]
                                        sizes = [total_detectados, total_faltantes]
                                        colors = ["forestgreen", "firebrick"]

                                        
                                        fig, ax = plt.subplots(figsize=(10, 4))
                                        ax.pie(
                                            sizes,
                                            labels=labels,
                                            autopct="%1.1f%%",
                                            colors=colors,
                                            startangle=90,
                                            wedgeprops={"edgecolor": "black", "linewidth": 1},
                                            textprops={"fontsize": 12, "weight": "bold"}
                                        )

                                       
                                        ax.set_title("Distribution of Detected and Missing Products", fontsize=14, fontweight="bold")

                                       
                                        ax.text(1.2, 0.2, f"Amount Detected: {total_detectados:.0f}", 
                                                ha="left", va="center", fontsize=10, weight="normal", color="black")
                                        ax.text(1.2, 0.1, f"Amount Missing: {total_faltantes:.0f}", 
                                                ha="left", va="center", fontsize=10, weight="normal", color="black")

                                        st.pyplot(fig)


                        
                        st.write("### Amount of Detected Products")

                        responsedf = TotalProductsDetected(st.session_state.token,result["id_image"])
                        if responsedf.status_code == 200:
                           resultdf = responsedf.json()
                           if resultdf["status_code"] == 200:
                                df = pd.DataFrame(resultdf["df"])

                                if not df.empty:
                                    st.write("### 📊 Distribution of Detected Products")
                            
                                    
                                    df["total_detected"] = pd.to_numeric(df["total_detected"], errors="coerce").fillna(0)
                            
                                    
                                    df = df.sort_values(by="total_detected", ascending=True)
                            
                                   
                                    fig_height = max(0.5 * len(df), 6)  
                                    fig, ax = plt.subplots(figsize=(12, fig_height))
                            
                                  
                                    cmap = plt.cm.Blues
                                    colors = cmap(df["total_detected"] / df["total_detected"].max())
                            
                                 
                                    bars = ax.barh(df["product_name"], df["total_detected"], color=colors, edgecolor="black", linewidth=0.8)
                            
                                   
                                    ax.set_xlabel("Amount detected", fontsize=14, labelpad=10)
                                    ax.set_ylabel("Name of the product", fontsize=14, labelpad=10)
                                    ax.set_title("Detected products", fontsize=16, fontweight="bold", pad=15)
                            
                                    
                                    plt.xticks(fontsize=12)
                                    plt.yticks(fontsize=11)
                            
                                    
                                    for bar, value in zip(bars, df["total_detected"]):
                                        ax.text(value + 1, bar.get_y() + bar.get_height() / 2, f"{value:,}", 
                                                fontsize=10, verticalalignment="center", color="black", fontweight="bold")
                            
                                    
                                    ax.spines["top"].set_visible(False)
                                    ax.spines["right"].set_visible(False)
                                    ax.spines["left"].set_color("gray")
                                    ax.spines["bottom"].set_color("gray")
                            
                                   
                                    ax.xaxis.grid(True, linestyle="--", alpha=0.6)
                            
                                   
                                    plt.tight_layout()
                                    st.pyplot(fig)
        
                    else : 
                        st.write(f"Error: The classification was not performed correctly. Details: {result['status_code']}")
                else:
                    st.write(f"Error: The classification was not performed correctly. Posible error from bucket.")
            else:
                st.warning("Please upload an image before classifying.")
            
    elif menu == "📊 Reports":
        st.markdown("# 📋 Analysis Reports")
        report_option = st.selectbox("Select report type", (
            "Processed Product Information","Missing Products"))

        if "selected_row" not in st.session_state:
            st.session_state.selected_row = None

        if "dataframe" not in st.session_state:
            st.session_state.dataframe = None  # Inicializamos en None

        with st.container():
            if report_option == "Processed Product Information":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=pd.to_datetime("today").normalize())
                with col2:
                    end_date = st.date_input("End Date", value=pd.to_datetime("today").normalize())
                
                click = st.button("Search")
                if st.session_state.dataframe is not None:
                        st.title("📊 Report of Detected Images")
                        df= st.session_state.dataframe
                      
                        search_term = st.text_input("🔍 Search for file name:", "")

                   
                        if search_term:
                            df = df[df["NAME"].str.contains(search_term, case=False, na=False)]

                    
                        gb = GridOptionsBuilder.from_dataframe(df)
                        gb.configure_selection(selection_mode="single", use_checkbox=True)  # Selección de una fila
                        grid_options = gb.build()

                      
                        grid_response = AgGrid(df, gridOptions=grid_options, height=300, fit_columns_on_grid_load=True)
                        
                        if not grid_response.selected_rows.empty:
                            selected_row = grid_response.selected_rows.iloc[0]
                            numero = selected_row.get("N-REGISTER")  
                            responsedf = ImageDetectionReport(st.session_state.token,numero)
                            if responsedf.status_code == 200:
                                image_data = responsedf.json()
                                if image_data["status_code"] == 200:
                                    st.subheader("📌 Selected Product Information Report")
                                    if image_data:
                                        col1, col2 = st.columns([1.5, 2])
                                        with col1: 
                                            s3_url = image_data['df']["s3_url"] 
                                            responses3 = ImageS3(st.session_state.token,s3_url)
                                            if responses3.status_code == 200:
                                                s3 = responses3.json()
                                                if s3["status_code"] == 200: 
                                            
                                                    detected_image = decode_base64(s3["detected_image"])
                                                    st.image(detected_image, caption=image_data['df']["image_name"], width=300, use_container_width=True)
                                        with col2:
                                            st.write(f"**📅 Created at:** {image_data['df']['created_at']}")
                                            st.write(f"**🔗 Image URL:** {image_data['df']['s3_url']}")
                                            st.write(f"**✅ Detected products:** {image_data['df']['detected_products']}")
                                            st.write(f"**❌ Missing products:** {image_data['df']['missing_products']}")
                                            detection_rate = float(image_data['df']["detection_rate"].replace('%', '')) / 100
                                           
                                            st.markdown(
                                                f"""
                                                <style>
                                                    .progress-bar-container {{
                                                        width: 100%;
                                                        height: 30px;
                                                        background: linear-gradient(to right, green {detection_rate * 100}%, red {detection_rate * 100}%);
                                                        border-radius: 10px;
                                                        text-align: center;
                                                        font-size: 20px;
                                                        color: white;
                                                        line-height: 30px;
                                                    }}
                                                </style>
                                                <div class="progress-bar-container">{image_data['df']["detection_rate"]}</div>
                                                """, unsafe_allow_html=True)
                                        df_detected = pd.DataFrame(image_data['df']["detected_product_list"])
                                        df_detected["status"] = "OK"
                                        df_detected = df_detected.rename(columns={"product_name": "Product"})
                                        df_missing = pd.DataFrame(image_data['df']["missing_product_list"])
                                        df_missing["status"] = "FAIL"  
                                        df_missing = df_missing.rename(columns={"product_name": "Product"})
                                        df_combined = pd.concat([df_detected, df_missing], ignore_index=True)
                                        df_combined["status"] = df_combined["status"].apply(lambda x: "✅" if x == "OK" else "⚠️")
                                        st.table(df_combined)
                                        df_chart = pd.DataFrame({
                                            "Class": ["Detected", "Missing"],
                                            "Amount": [len(image_data['df']["detected_product_list"]), len(image_data['df']["missing_product_list"])]
                                        })
                                        fig = px.bar(df_chart, x="Class", y="Amount", color="Class",
                                                     color_discrete_map={"Detected": "green", "Missing": "red"},
                                                     text_auto=True)
                                        st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.warning("⚠️ No data found for this image.")
                            else:
                                st.warning("No records were found in the selected date range.")

                       
                elif click:
                    
                    st.spinner("Loading report...")
    
                    responsedall = ImageDetectionAll(st.session_state.token,start_date,end_date)
                    if responsedall.status_code == 200:
                        image_data_all = responsedall.json()
                        if image_data_all["status_code"] == 200:
                        
                            st.session_state.dataframe = pd.DataFrame(image_data_all["df"], columns=["N-REGISTER", "NAME", "DATE"])
                            df = st.session_state.dataframe
                            
                            if not df.empty:
                                st.title("📊 Report of Detected Images")

                               
                                search_term = st.text_input("🔍 Search for file name:", "")

                                
                                if search_term:
                                    df = df[df["NAME"].str.contains(search_term, case=False, na=False)]

                                
                                gb = GridOptionsBuilder.from_dataframe(df)
                                gb.configure_selection(selection_mode="single", use_checkbox=True)  
                                grid_options = gb.build()

                                
                                grid_response = AgGrid(df, gridOptions=grid_options, height=300, fit_columns_on_grid_load=True)
                                
                                if grid_response["selected_rows"]:
                                  
                                    st.session_state.selected_row = grid_response["selected_rows"][0]
                                    LOGGER.warning(f"Selected record: {st.session_state.selected_row}")
                                elif st.session_state.selected_row:
                                    
                                    selected_row = st.session_state.selected_row
                                    LOGGER.warning(f"Row selected previously: {selected_row}")
                                    st.write(f"Register selected previously: {selected_row}")
                               
                            

            elif report_option == "Missing Products":
                st.subheader("⚠️ Missing Products report")
                
              

menu = show_sidebar()
show_content(menu)
