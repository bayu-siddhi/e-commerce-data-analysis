import os
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
from babel.numbers import format_currency

DATA_DIRECTORY = "data"
sns.set_theme(style='dark')


def data_path(filename: str) -> str:
    """Function: Mendapatkan file data"""
    return os.path.join(DATA_DIRECTORY, filename)


def set_datetime_columns(dataframe: pd.DataFrame, datetime_columns: list) -> None:
    """Procedure: Mengubah tipe data datetiem_columns menjadi datetime"""
    for column in datetime_columns:
        dataframe[column] = pd.to_datetime(dataframe[column])


def create_monthly_orders_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe jumlah dan penghasilan setiap bulan"""
    result_df = dataframe[dataframe["order_status"] == "delivered"]. \
        resample(rule='ME', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })

    result_df.index = result_df.index.strftime('%Y-%m')
    result_df = result_df.reset_index()
    result_df.rename(columns={
        "order_purchase_timestamp": "order_month",
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return result_df


def create_sum_order_items_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe jumlah dan penghasilan setiap kategori produk"""
    result_df = dataframe.groupby(by="product_category_name_english").agg({
        "product_id": "nunique",
        "price": "sum"
    }).reset_index().sort_values(by="product_id", ascending=False)

    result_df = result_df.rename(columns={
        "product_category_name_english": "product_category",
        "product_id": "count",
        "price": "revenue"
    }, inplace=False)

    return result_df


def create_payment_type_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe jenis metode pembayaran"""
    result_df = dataframe["payment_type"].value_counts().sort_values(ascending=False)
    result_df.to_frame()
    result_df = result_df.reset_index()
    return result_df


def create_payment_installments_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe jumlah pengguna cicilan"""
    result_df = dataframe["payment_installments"].value_counts().sort_values(ascending=False)
    result_df.to_frame()
    result_df = result_df.reset_index()
    result_df["use_installment"] = result_df["payment_installments"].apply(lambda x: True if x > 1 else False)

    result_df = result_df.groupby(by="use_installment")["count"].sum()
    result_df.to_frame()
    result_df = result_df.reset_index().sort_values(by="count", ascending=False)

    return result_df


def create_customer_order_revenue_city(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe jumlah pesanan dan total revenue setiap kota"""
    result_df = dataframe.groupby(by="customer_city").agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index().sort_values(by="order_id", ascending=False)

    result_df.rename(columns={
        "customer_city": "customer_city",
        "order_id": "order",
        "payment_value": "revenue"
    }, inplace=True)

    return result_df


def create_customer_order_revenue_state(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe jumlah pesanan dan total revenue setiap negara bagian"""
    result_df = dataframe.groupby(by="customer_state").agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index().sort_values(by="order_id", ascending=False)

    result_df.rename(columns={
        "customer_state": "customer_state",
        "order_id": "order",
        "payment_value": "revenue"
    }, inplace=True)

    return result_df


def create_customer_scores_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe skor kepuasan pelanggan"""
    result_df = dataframe["review_score"].value_counts()
    result_df.to_frame()
    result_df = result_df.reset_index()
    result_df["satisfaction"] = result_df["review_score"].apply(
        lambda x: "satisfied" if x >= 4 else "not satisfied"
    )
    result_df = result_df.sort_values(by="review_score", ascending=True)
    return result_df


def create_satisfied_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    result_df = dataframe.groupby(by="satisfaction")["count"].sum()
    result_df.to_frame()
    result_df = result_df.reset_index()
    result_df = result_df.sort_values(by="count", ascending=False)
    return result_df


def create_rfm_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Function: Mendapatkan dataframe RFM (Recency, Frequency, Monetary)"""
    result_df = dataframe[dataframe["order_status"] == "delivered"].\
        groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })

    result_df.rename(columns={
        "customer_unique_id": "customer_id",
        "order_purchase_timestamp": "max_order_purchase_timestamp",
        "order_id": "frequency",
        "payment_value": "monetary"
    }, inplace=True)

    result_df["max_order_purchase_timestamp"] = result_df["max_order_purchase_timestamp"].dt.date
    recent_date = dataframe["order_purchase_timestamp"].dt.date.max()
    result_df["recency"] = result_df["max_order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)
    result_df.drop("max_order_purchase_timestamp", axis=1, inplace=True)

    return result_df


if __name__ == '__main__':
    # Memuat dataset 1
    dataset_1_df = pd.read_csv(data_path("order_customers_payments_dataset.csv"))
    datetime_colums = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
                       "order_delivered_customer_date", "order_estimated_delivery_date"]
    set_datetime_columns(dataset_1_df, datetime_colums)

    # Memuat dataset 2
    dataset_2_df = pd.read_csv(data_path("orders_order_items_products_category_dataset.csv"))
    set_datetime_columns(dataset_2_df, ["shipping_limit_date"])

    # Memuat dataset 3
    order_reviews_df = pd.read_csv(data_path("order_reviews_dataset.csv"))
    set_datetime_columns(order_reviews_df, ["review_creation_date", "review_answer_timestamp"])

    min_date = dataset_1_df["order_purchase_timestamp"].min()
    max_date = dataset_1_df["order_purchase_timestamp"].max()

    with st.sidebar:
        st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png")

        # Mengambil start_date & end_date dari date_input
        start_date, end_date = st.date_input(
            label="Timeframe",
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

        st.caption("Use light mode for best visualization. Change from \"⋮\" → \"Settings\" → \"Theme\"")

    # Melakukan filter tanggal pada 3 dataset utama
    main_1_df = dataset_1_df[(dataset_1_df["order_purchase_timestamp"] >= str(start_date))
                             & (dataset_1_df["order_purchase_timestamp"] <= str(end_date))]
    main_2_df = dataset_2_df[(dataset_2_df["order_purchase_timestamp"] >= str(start_date))
                             & (dataset_2_df["order_purchase_timestamp"] <= str(end_date))]
    main_3_df = order_reviews_df[(order_reviews_df["review_creation_date"] >= str(start_date))
                                 & (order_reviews_df["review_creation_date"] <= str(end_date))]

    # Menyiapkan berbagai dataframe
    monthly_orders_df = create_monthly_orders_df(main_1_df)
    sum_order_items_df = create_sum_order_items_df(main_2_df)
    payment_type_df = create_payment_type_df(main_1_df)
    payment_installments_df = create_payment_installments_df(main_1_df)
    customer_order_revenue_city = create_customer_order_revenue_city(main_1_df)
    customer_order_revenue_state = create_customer_order_revenue_state(main_1_df)
    customer_scores_df = create_customer_scores_df(main_3_df)
    satisfied_df = create_satisfied_df(customer_scores_df)
    rfm_df = create_rfm_df(main_1_df)

    # Dashboard
    st.header('E-Commerce Public Dataset Analysis :sparkles:')

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Monthly Orders and Revenue",
        "Product Category Performance",
        "Payment Methods",
        "Customer Reviews",
        "RFM Analysis"
    ])

    with tab1:
        st.subheader('Monthly Orders and Revenue')

        col1, col2 = st.columns(2)
        with col1:
            total_orders = main_1_df["order_id"].nunique()
            st.metric("Total orders", value=total_orders)
        with col2:
            total_revenue = format_currency(main_1_df["payment_value"].sum(), "BRL", locale="pt_BR")
            st.metric("Total Revenue", value=total_revenue)

        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(
            monthly_orders_df["order_month"],
            monthly_orders_df["order_count"],
            marker='o',
            linewidth=0.75,
            color="#1230AE"
        )
        ax.set_title("Number of Orders per Month", loc="left", fontsize=18)
        ax.tick_params(axis='y', labelsize=15)
        ax.tick_params(axis='x', labelsize=15, rotation=90)

        st.pyplot(fig)

        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(
            monthly_orders_df["order_month"],
            monthly_orders_df["revenue"],
            marker='o',
            linewidth=0.75,
            color="#1230AE"
        )
        ax.set_title("Total of Revenue per Month", loc="left", fontsize=18)
        ax.ticklabel_format(style='plain', axis='y')
        ax.tick_params(axis='y', labelsize=15)
        ax.tick_params(axis='x', labelsize=15, rotation=90)

        st.pyplot(fig)

        st.write(" ")

        st.subheader('Best Number of Orders by City and State')

        col1, col2 = st.columns(2)
        with col1:
            best_total_order_city_idx = customer_order_revenue_city["order"].idxmax()
            best_total_order_city = customer_order_revenue_city.loc[best_total_order_city_idx, "customer_city"]
            best_total_order_city = " ".join(best_total_order_city.split("_")).capitalize()
            st.metric("City with the most orders", value=best_total_order_city)

            best_total_order_city_value = customer_order_revenue_city.loc[best_total_order_city_idx, "order"]
            st.metric("Total orders for the city above", value=best_total_order_city_value)

        with col2:
            best_total_order_state_idx = customer_order_revenue_state["order"].idxmax()
            best_total_order_state = customer_order_revenue_state.loc[best_total_order_state_idx, "customer_state"]
            best_total_order_state = " ".join(best_total_order_state.split("_")).upper()
            st.metric("State with the most orders", value=best_total_order_state)

            best_total_order_state_value = customer_order_revenue_state.loc[best_total_order_state_idx, "order"]
            st.metric("Total orders for the state above", value=best_total_order_state_value)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
        colors = ["#1230AE", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

        sns.barplot(x="customer_city", y="order",
                    data=customer_order_revenue_city.sort_values(by="order", ascending=False).head(5),
                    palette=colors, ax=ax[0], hue="customer_city")
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Number of Orders by City", loc="center", fontsize=25)
        ax[0].tick_params(axis='y', labelsize=20)
        ax[0].tick_params(axis='x', labelsize=18)

        sns.barplot(x="customer_state", y="order",
                    data=customer_order_revenue_state.sort_values(by="order", ascending=False).head(5),
                    palette=colors, ax=ax[1], hue="customer_state")
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()
        ax[1].set_title("Best Number of Orders by State", loc="center", fontsize=25)
        ax[1].tick_params(axis='y', labelsize=20)
        ax[1].tick_params(axis='x', labelsize=20)

        st.pyplot(fig)

        st.write(" ")

        st.subheader('Best Total Revenue by City and State')

        col1, col2 = st.columns(2)
        with col1:
            best_total_revenue_city_idx = customer_order_revenue_city["revenue"].idxmax()
            best_total_revenue_city = customer_order_revenue_city.loc[best_total_revenue_city_idx, "customer_city"]
            best_total_revenue_city = " ".join(best_total_revenue_city.split("_")).capitalize()
            st.metric("City with the most total revenue", value=best_total_revenue_city)

            best_total_revenue_city_value = customer_order_revenue_city.loc[best_total_revenue_city_idx, "revenue"]
            best_total_revenue_city_value = format_currency(best_total_revenue_city_value, "BRL", locale="pt_BR")
            st.metric("Total revenue for the city above", value=best_total_revenue_city_value)

        with col2:
            best_total_revenue_state_idx = customer_order_revenue_state["revenue"].idxmax()
            best_total_revenue_state = customer_order_revenue_state.loc[best_total_revenue_state_idx, "customer_state"]
            best_total_revenue_state = " ".join(best_total_revenue_state.split("_")).upper()
            st.metric("State with the most total revenue", value=best_total_revenue_state)

            best_total_revenue_state_value = customer_order_revenue_state.loc[best_total_revenue_state_idx, "revenue"]
            best_total_revenue_state_value = format_currency(best_total_revenue_state_value, "BRL", locale="pt_BR")
            st.metric("Total revenue for the state above", value=best_total_revenue_state_value)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
        colors = ["#1230AE", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

        sns.barplot(x="customer_city", y="revenue",
                    data=customer_order_revenue_city.sort_values(by="revenue", ascending=False).head(5),
                    palette=colors, ax=ax[0], hue="customer_city")
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Total Revenue by City", loc="center", fontsize=25)
        ax[0].tick_params(axis='y', labelsize=20)
        ax[0].tick_params(axis='x', labelsize=18)

        sns.barplot(x="customer_state", y="revenue",
                    data=customer_order_revenue_state.sort_values(by="revenue", ascending=False).head(5),
                    palette=colors, ax=ax[1], hue="customer_state")
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()
        ax[1].set_title("Best Total Revenue by State", loc="center", fontsize=25)
        ax[1].tick_params(axis='y', labelsize=20)
        ax[1].tick_params(axis='x', labelsize=20)

        st.pyplot(fig)

    with tab2:
        st.subheader("Best Performing Product Category by Number of Orders")

        col1, col2 = st.columns(2)
        best_orders_category_idx = sum_order_items_df["count"].idxmax()
        with col1:
            best_orders_category = sum_order_items_df.loc[best_orders_category_idx, "product_category"]
            best_orders_category = " ".join(best_orders_category.split("_")).capitalize()
            st.metric("Best Orders Category", value=best_orders_category)
        with col2:
            num_orders_category = sum_order_items_df.loc[best_orders_category_idx, "count"]
            st.metric("Num of Orders", value=num_orders_category)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

        colors_1 = ["#1230AE", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="count", y="product_category",
                    data=sum_order_items_df.sort_values(by="count", ascending=False).head(5),
                    palette=colors_1, ax=ax[0], hue="product_category")
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Performing Product Category", loc="left", fontsize=25)
        ax[0].tick_params(axis='y', labelsize=20)
        ax[0].tick_params(axis='x', labelsize=20)

        colors_2 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#1230AE"]
        sns.barplot(x="count", y="product_category",
                    data=sum_order_items_df.sort_values(by="count", ascending=False).tail(5),
                    palette=colors_2, ax=ax[1], hue="product_category")
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].invert_xaxis()
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()
        ax[1].set_title("Worst Performing Product Category", loc="right", fontsize=25)
        ax[1].tick_params(axis='y', labelsize=20)
        ax[1].tick_params(axis='x', labelsize=20)

        st.pyplot(fig)

        st.write(" ")

        st.subheader("Best Performing Product Category by Total Revenue")

        col1, col2 = st.columns(2)
        best_revenue_category_idx = sum_order_items_df["revenue"].idxmax()
        with col1:
            best_revenue_category = sum_order_items_df.loc[best_revenue_category_idx, "product_category"]
            best_revenue_category = " ".join(best_revenue_category.split("_")).capitalize()
            st.metric("Best Revenue Category", value=best_revenue_category)
        with col2:
            total_revenue_category = sum_order_items_df.loc[best_revenue_category_idx, "revenue"]
            total_revenue_category = format_currency(total_revenue_category, "BRL", locale="pt_BR")
            st.metric("Total Revenue Category", value=total_revenue_category)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

        colors_1 = ["#1230AE", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="revenue", y="product_category",
                    data=sum_order_items_df.sort_values(by="revenue", ascending=False).head(5),
                    palette=colors_1, ax=ax[0], hue="product_category")
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Performing Product Category", loc="left", fontsize=25)
        ax[0].tick_params(axis='y', labelsize=20)
        ax[0].tick_params(axis='x', labelsize=20)

        colors_2 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#1230AE"]
        sns.barplot(x="revenue", y="product_category",
                    data=sum_order_items_df.sort_values(by="revenue", ascending=False).tail(5),
                    palette=colors_2, ax=ax[1], hue="product_category")
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].invert_xaxis()
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()
        ax[1].set_title("Worst Performing Product Category", loc="right", fontsize=25)
        ax[1].tick_params(axis='y', labelsize=20)
        ax[1].tick_params(axis='x', labelsize=20)

        st.pyplot(fig)

    with (tab3):
        st.subheader("Best Payment Method")

        col1, col2 = st.columns(2)
        with col1:
            best_payment_method_idx = payment_type_df["count"].idxmax()
            best_payment_method = payment_type_df.loc[best_payment_method_idx, "payment_type"]
            best_payment_method = " ".join(best_payment_method.split("_")).capitalize()
            st.metric("Best Payment Method", value=best_payment_method)
        with col2:
            percentage_installment_idx = int(
                payment_installments_df[payment_installments_df["use_installment"] == True].index[0])
            percentage_installment = payment_installments_df.loc[percentage_installment_idx, "count"] / int(
                payment_installments_df["count"].sum())
            percentage_installment = "{}%".format(round(percentage_installment * 100, 2))
            st.metric("Percentage using installments", value=percentage_installment)

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

        colors_1 = ["#1230AE", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        sns.barplot(x="payment_type", y="count", data=payment_type_df.head(5), palette=colors_1, ax=ax[0],
                    hue="payment_type")
        ax[0].set_ylabel(None)
        ax[0].set_xlabel(None)
        ax[0].set_title("Best Payment Type", loc="center", fontsize=25)
        ax[0].tick_params(axis='y', labelsize=20)
        ax[0].tick_params(axis='x', labelsize=20)

        colors_2 = ["#D3D3D3", "#1230AE"]
        sns.barplot(x="use_installment", y="count", data=payment_installments_df.head(5), palette=colors_2, ax=ax[1],
                    hue="use_installment", legend=False)
        ax[1].set_ylabel(None)
        ax[1].set_xlabel(None)
        ax[1].yaxis.set_label_position("right")
        ax[1].yaxis.tick_right()
        ax[1].set_title("Use Installment?", loc="center", fontsize=25)
        ax[1].tick_params(axis='y', labelsize=20)
        ax[1].tick_params(axis='x', labelsize=20)

        st.pyplot(fig)

    with (tab4):
        st.subheader("Customer Review Scores")

        col1, col2 = st.columns(2)
        with col1:
            satisfied_idx = int(
                satisfied_df[satisfied_df["satisfaction"] == "satisfied"].index[0])
            satisfied_value = satisfied_df.loc[satisfied_idx, "count"]
            satisfied_value = satisfied_value / satisfied_df["count"].sum()
            satisfied_value = "{}%".format(round(satisfied_value * 100, 2))
            st.metric("Percentage of satisfied (4-5:star:)", value=satisfied_value)
        with col2:
            not_satisfied_idx = int(
                satisfied_df[satisfied_df["satisfaction"] == "not satisfied"].index[0])
            not_satisfied_value = satisfied_df.loc[not_satisfied_idx, "count"]
            not_satisfied_value = not_satisfied_value / satisfied_df["count"].sum()
            not_satisfied_value = "{}%".format(round(not_satisfied_value * 100, 2))
            st.metric("Percentage of dissatisfied (1-3:star:)", value=not_satisfied_value)

        colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
        colors[int(customer_scores_df["count"].argmax())] = "#1230AE"

        fig, ax = plt.subplots(figsize=(16, 8))
        sns.barplot(x="review_score", y="count", data=customer_scores_df,
                    palette=colors, hue="review_score", legend=False)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.set_title("Customer Review Score", loc="left", fontsize=20)
        ax.tick_params(axis='y', labelsize=15)
        ax.tick_params(axis='x', labelsize=15)

        st.pyplot(fig)

        st.subheader("New Review Messages")

        st.write(
            main_3_df[~main_3_df["review_comment_message"].isna()].\
                sort_values(by="review_creation_date", ascending=False).reset_index()\
                [["review_creation_date", "review_score", "review_comment_title", "review_comment_message"]]
        )

    with tab5:
        st.subheader("Best Customer Based on RFM Parameters")

        col1, col2, col3 = st.columns(3)
        with col1:
            avg_recency = round(rfm_df.recency.mean(), 1)
            st.metric("Average Recency (days)", value=avg_recency)
        with col2:
            avg_frequency = round(rfm_df.frequency.mean(), 2)
            st.metric("Average Frequency", value=avg_frequency)
        with col3:
            avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale="pt_BR")
            st.metric("Average Monetary", value=avg_monetary)

        st.caption('There is no customer name, only customer_unique_id')

        colors = ["#1230AE", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

        st.subheader("By Recency (days)")

        fig, ax = plt.subplots(figsize=(16, 8))
        sns.barplot(y="customer_id", x="recency", data=rfm_df.sort_values(by="recency", ascending=True).head(5),
                    palette=colors, hue="customer_id")
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis='y', labelsize=18)
        ax.tick_params(axis='x', labelsize=20)
        st.pyplot(fig)

        st.subheader("By Frequency")
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.barplot(y="customer_id", x="frequency", data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
                    palette=colors, hue="customer_id")
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis='y', labelsize=18)
        ax.tick_params(axis='x', labelsize=20)
        st.pyplot(fig)

        st.subheader("By Monetary (R$)")
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.barplot(y="customer_id", x="monetary", data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
                    palette=colors, hue="customer_id")
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis='y', labelsize=18)
        ax.tick_params(axis='x', labelsize=20)
        st.pyplot(fig)
