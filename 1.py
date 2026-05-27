import streamlit as st
import pandas as pd
import os
import re
from streamlit_option_menu import option_menu
import plotly.express as px
import time
import google.generativeai as genai
from groq import Groq

st.set_page_config(
    page_title = "Sales Analysis",
    layout = "wide",
    page_icon = "🏪",
)
file ="data_load.csv"
df = pd.read_csv("Supermart Grocery Sales - Retail Analytics Dataset (1).csv")

def load_and_clean_data(file_path: str) -> pd.DataFrame:
    """Load and process any dataset with the standard columns."""
    df = pd.read_csv(file_path)

    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df.dropna(subset=["Order Date"], inplace=True)

    df["Month"]      = df["Order Date"].dt.month_name()
    df["Month_Num"]  = df["Order Date"].dt.month
    df["Year"]       = df["Order Date"].dt.year
    df["Quarter"]    = df["Order Date"].dt.quarter
    df["Month_Year"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Profit Margin %"] = (df["Profit"] / df["Sales"]) * 100

    return df



if "logged_in" not in st.session_state:
    st.session_state.logged_in =False
if "username" not in st.session_state:
    st.session_state.username =""
if "page" not in st.session_state:
    st.session_state.page ="Login"

def signup_page():
    st.header("Register Here")
    if not os.path.exists(file):
        pd.DataFrame(columns= [
            "Username",
            "Password",
            "Confirm Password",
            "Role"
        ]).to_csv(file,index=False)

    df = pd.read_csv(file)

    with st.form("Signup"):
        name = st.text_input("Enter Your Name",
                             placeholder="Enter Your Name")

        password = st.text_input("Enter Your Password",
                                 placeholder="Enter Your Password",
                                 type="password")
        conform_password = st.text_input("Confirm Password",
                                         placeholder="Confirm Password",
                                         type="password")
        role = st.selectbox("Select Role",["User","Admin"]) #Role base
        submit = st.form_submit_button("Submit")

        if submit:
            if not all([name,password]):
                st.error("Fill Full Data")
            elif not re.match(r"[A-Z]", password):
                st.error("Password must contain one uppercase")
            elif not re.search(r"[a-z]", password):
                st.error("Password must contain one Lowercase")
            elif password != conform_password:
                st.error("Password and Confirm Password Mismatch")
            elif name in df["Username"].values:
                st.error("Username Already Exists")
            else:

                new_user = pd.DataFrame([{
                    "Username":name,
                    "Password": password,
                    "Confirm Password": conform_password,
                    "Role":role # role base
                }])

                pd.concat([df,new_user],ignore_index=True).to_csv(file,index=False)
                st.success("Register successfully")
                st.session_state.page = "Login"
                st.rerun()


    if st.button("Already Registered ? Login Here"):
        st.session_state.page = "Login"
        st.rerun()

def login_page():

    st.header("Login Here")
    username = st.text_input("Enter Your Username",
                             placeholder="Enter Your Username")
    Password = st.text_input("Enter Your Password",
                             placeholder="Enter Your Password",
                             type="password")

    if st.button("Login"):
        if os.path.exists(file):
            df = pd.read_csv(file)
            user = df[(df["Username"] == username) & (df["Password"]== Password)]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = "Home"
                st.session_state.role = user.iloc[0]["Role"] # role base
                st.success("Login Thai gayu !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Username Or Password Is Incorrect")
    if st.button("New User ?? Register"):
        st.session_state.page = "Signup"
        st.rerun()

if st.session_state.page == "Signup":
    signup_page()
    st.stop()
elif st.session_state.page == "Login":
    login_page()
    st.stop()

elif st.session_state.page == "Home":
    if not st.session_state.logged_in:
        st.session_state.page = "Login"
        st.rerun()


with st.sidebar:

        if st.session_state.role == "Admin":
            selected = option_menu(
                menu_title="Admin Panel",
                options=[
                    "About Project",
                    "Dataset Overview",
                    "Advance Analytics",
                    "Home",
                    "User Management",
                    "AI"# Admin Only

                ],
                icons=[

                "info-circle",  # About Project
                "database",  # Dataset Overview
                "graph-up-arrow",  # Advance Analytics
                "house",  # Home
                "people-fill", # User Management
                "robot"


                ],
                menu_icon="cast"

            )


        else:  # Normal User
            selected = option_menu(
                menu_title="User Panel",
                options=[
                    "About Project",
                    "Dataset Overview",
                    "Advance Analytics",
                    "Home",
                    "AI"


                ],
                icons=[
                    "info-circle",  # About Project
                    "database",  # Dataset Overview
                    "graph-up-arrow",  # Advance Analytics
                    "house",  # Home
                    "robot"

                ],
                menu_icon="cast"
            )
        if st.sidebar.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.page = "Login"
                st.success("Logout Successfully 👋")
                time.sleep(1)
                st.rerun()

# ----------------------------------------------------------------------------------------------
if selected == "About Project":
    st.title("📖 About the Project")
    st.info(f"""
        **Objective:** Build a Python-based sales analytics dashboard for academic/portfolio purposes.

        **Tech Stack:**
        - **Python**: Core logic
        - **Streamlit**: Web Framework
        - **Pandas / NumPy**: Data Processing
        - **Plotly**: Interactive Data Visualization

        **Datasets:**
        - 🛒 Supermart Grocery Sales – Indian retail grocery transactions
        """)

elif selected == "Dataset Overview":
    st.title("📂 Dataset Overview")
    st.caption(f"Viewing: **Salse Analysis**")
    tab1, tab2 = st.tabs(["Data Preview", "Statistics"])
    with tab1:
        st.dataframe(df.head(100))
    with tab2:
        st.write(df.describe())


elif selected == "Home":
    st.title(" Intelligent Sales Analytics Dashboard ")
    st.subheader("📅 Clean Data")

    st.dataframe(
        df[["Order ID", "Order Date", "Sales", "Category", "Customer Name"]]
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Sales", f"₹ {df['Sales'].sum():,.0f}")
    col2.metric("Total Orders", len(df))
    col3.metric("Total Categories", df['Category'].nunique())


    st.subheader("Instant Insights")
    cat_sales = df.groupby("Category")["Sales"].sum().reset_index()

    fig = px.pie(cat_sales,
        names="Category",
        values="Sales",
        color="Category",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    top_cat  = cat_sales.loc[cat_sales["Sales"].idxmax(), "Category"]
    top_pct  = cat_sales["Sales"].max() / cat_sales["Sales"].sum() * 100
    st.info(
        f"📊 **Category Sales Overview:** The **{top_cat}** category dominates with "
        f"**{top_pct:.1f}%** of total sales revenue. "
        f"There are **{len(cat_sales)}** distinct categories contributing to the overall sales mix. "
        f"This snapshot gives a quick sense of where revenue is concentrated across the product portfolio."
    )



elif selected == "Advance Analytics":

    st.subheader("Intelligent Sales Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Salse",df["Sales"].mean())
    col2.metric("Total City",df["City"].nunique())
    col3.metric("Total Customer",df["Customer Name"].nunique())
    st.divider()


    col1,col2 = st.columns(2)
    with col1:
        df["Profit Margin"] = (df["Profit"] / df["Sales"]) * 100
        fig = px.box(
            df,
            x="Category",
            y="Profit Margin",
            color="Category"
        )

        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Revenue")

        show_margin = df.groupby("Order ID").agg(
            Order_id = ("Order ID","first"),
            Category = ("Category","first"),
            Sales = ("Sales","first"),
            Profit = ("Profit","first")
        )

        st.dataframe(show_margin)


    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Discount Impact Study")

        fig = px.scatter(df,
            x="Discount",
            y="Profit",
            color="Category",
            size="Sales",
            title="Profit vs Discount Intensity"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_copy = df.copy()
        df_copy["Discount_Bin"] = pd.cut(
            df_copy["Discount"],
            bins=[0,0.1,0.2,0.3,0.4,0.5],
            labels=["0-10%","10-20%","20-30%","30-40%","40%+"]
        )

        fig2 = px.box(df_copy,
                      x="Discount_Bin",
                      y="Profit",
                      color="Discount_Bin",
                      title="Profitability Distribution by Discount Tier",
                      labels={"Discount_Bin ": "Discount Bracket"})
        st.plotly_chart(fig2, use_container_width=True)

        st.divider()
    df["Profit Margin"] = (df["Profit"] / df["Sales"]) * 100

    corr_cols = ["Sales", "Profit", "Discount", "Profit Margin"]
    corr_matrix = df[corr_cols].corr()

    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                        color_continuous_scale="Blues",
                        title="Correlation Matrix Heatmap (Interactive)")
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    tab1, tab2, tab3 = st.tabs(["Regions", "Categories", "Salespersons"])

    with tab1:
        r = df.groupby("Region")["Sales"].sum().sort_values(ascending=False).reset_index()
        r["Rank"] = range(1, len(r) + 1)
        st.table(r)

    with tab2:
        r = df.groupby("Category")["Sales"].sum().sort_values(ascending=False).reset_index()
        r["Rank"] = range(1, len(r) + 1)
        st.table(r)

    with tab3:
        r = df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).reset_index()
        r["Rank"] = range(1, len(r) + 1)
        st.dataframe(r.head(10))


elif selected == "User Management":

    st.title("👨‍💼 User Management Panel")

    if not os.path.exists(file):
        st.warning("No users found!")
        st.stop()

    users_df = pd.read_csv(file)

    st.subheader("All Users")
    st.dataframe(users_df)

    st.divider()

    # ===============================
    # 🔄 CHANGE ROLE
    # ===============================
    st.subheader("🔄 Change User Role")

    selected_user = st.selectbox(
        "Select User",
        users_df["Username"]
    )

    new_role = st.selectbox(
        "Select New Role",
        ["User", "Admin"]
    )

    if st.button("Update Role"):
        users_df.loc[
            users_df["Username"] == selected_user, "Role"
        ] = new_role

        users_df.to_csv(file, index=False)

        st.success(f"✅ Role updated for {selected_user}")
        time.sleep(1)
        st.rerun()

    st.divider()

    # ===============================
    # ❌ DELETE USER
    # ===============================
    st.subheader("❌ Delete User")

    delete_user = st.selectbox(
        "Select User to Delete",
        users_df["Username"],
        key="delete_user"
    )

    if st.button("Delete User"):

        if delete_user == st.session_state.get("username"):
            st.error("⚠️ You cannot delete your own account!")
        else:
            users_df = users_df[
                users_df["Username"] != delete_user
            ]

            users_df.to_csv(file, index=False)

            st.success(f"🗑️ {delete_user} deleted successfully")
            time.sleep(1)
            st.rerun()

elif selected == "AI":

    select = st.radio("Select your Ai", ["Google Ai", "Groq Ai"])

    user_input = st.text_input("Enter your Question")

    if st.button("Submit"):
        if select == "Google Ai":
            try:
                genai.configure(api_key="AIzaSyCOZWMaY_i-_DBiVO-xWN0QIPgD3HEtNHk")
                model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
                response = model.generate_content(user_input)
                st.info(response.text)
            except Exception as e:
                st.error(f"error: {e}")

        elif select == "Groq Ai":
            try:
                client = Groq(api_key="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")
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{
                        "role": "user",
                        "content": user_input,
                    }])
                answer = response.choices[0].message.content
                st.info(answer)
            except Exception as e:
                st.error(f"error: {e}")


st.title("AI Startup Idea Analyzer & Builder")

st.header("Enter details")
idea = st.text_area("Business Idea")
industry = st.selectbox("Industry",
                                ["Technology",
                                 "Finance",
                                 "Healthcare",
                                 "Education",
                                 "E-Commerce",
                                 "Other"])

target_user = st.text_input("Target User")

tab1, tab2 = st.tabs(["Idea Analyzer", "How to start"])


def analyze_business():
    prompt = f"""
    You are Startup Expert
    Business Idea: {idea}
    Industry: {industry}
    Target User: {target_user}


    Provide:
    1.Idea explanation 
    2.Problem it solves
    3.Target audience
    4.Market Potential
    5.Competitor
    6.Strength & Weakness
    7.Investment
    8.Risk management
    9.Revenue Model
    10. Final verdict(Good/Risky/needs improvement)


    keep it structured
"""
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are startup analyst"
            },
            {
                "role": "user",
                "content": prompt
            }
        ])

    return res.choices[0].message.content


def generate_roadmap():
    prompt = f"""

    you are Startup Mentor

    Business Idea: {idea}
    Industry: {industry}
    Target User: {target_user}

    Give a practical execution roadmap

    1.First 5 steps to start
    2.MVP(minimum Valuable Product) plan
    3.Tech Stack suggestion 
    4.Monetization strategy
    5.Got-to-market strategy
    6.Mistakes to avoid

    keep it actionable and beginner friendly

    """

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are Expertenced startup mentor"
            },
            {
                "role": "user",
                "content": prompt
            }
        ])

    return res.choices[0].message.content


with tab1:
    st.subheader("Analyze your business idea")
    if st.button("Analyze idea"):
        if idea.strip() == "":
            st.warning("Please enter your business idea")

        else:
            with st.spinner("Analyzing idea"):
                result = analyze_business()

            st.success("Analysis Completed")
            st.info(result)

with tab2:
    st.subheader("Roadmap")
    if st.button("Generate Roadmap"):
        if idea.strip() == "":
            st.warning("Please enter your business idea.")
        else:
            with st.spinner("Generating Roadmap..."):
                result = generate_roadmap()
            st.success("Roadmap Generated")
            st.info(result)