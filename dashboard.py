
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from catboost import CatBoostRegressor

# Set page config
st.set_page_config(layout="wide", page_title="Sydney House Price Estimator")

@st.cache_data
def load_data():
    data_path = 'data/sales_history.parquet'
    if not os.path.exists(data_path):
        return None
    df = pd.read_parquet(data_path)
    return df

@st.cache_resource
def load_model():
    model_path = 'models/catboost_model.cbm'
    if not os.path.exists(model_path):
        return None
    model = CatBoostRegressor(logging_level='Silent')
    model.load_model(model_path)
    return model

def tab_explore(df):
    st.header("🔎 Explore Historical Data")
    
    # Sidebar Filters (Specific to Explore)
    st.sidebar.header("Explore Filters")
    
    # Year Range
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    
    # Suburb Selection
    all_suburbs = sorted(df['Suburb'].unique())
    selected_suburbs = st.sidebar.multiselect("Select Suburbs (Leave empty for all)", all_suburbs, default=['SYDNEY', 'PARRAMATTA', 'NEWTOWN'])
    
    # Property Type
    all_types = sorted(df['PropertyType'].unique())
    selected_types = st.sidebar.multiselect("Property Type", all_types, default=['RESIDENCE', 'STRATA UNIT'])

    # Filtering Logic
    mask = (df['Year'] >= years[0]) & (df['Year'] <= years[1])
    if selected_suburbs:
        mask &= df['Suburb'].isin(selected_suburbs)
    if selected_types:
        mask &= df['PropertyType'].isin(selected_types)
        
    filtered_df = df[mask]
    
    st.write(f"Showing **{len(filtered_df):,}** sales records.")
    
    if filtered_df.empty:
        st.warning("No data matches your filters.")
        return

    # KPI Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Median Price", f"${filtered_df['PurchasePrice'].median():,.0f}")
    col2.metric("Average Price", f"${filtered_df['PurchasePrice'].mean():,.0f}")
    col3.metric("Total Volume", len(filtered_df))

    # --- Charts ---
    st.subheader("📈 Median Price Trend")
    if len(filtered_df) > 0:
        trend_data = filtered_df.set_index('ContractDate').resample('M')['PurchasePrice'].median().reset_index()
        fig_trend = px.line(trend_data, x='ContractDate', y='PurchasePrice', title="Monthly Median Price", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("💰 Price Distribution")
    q95 = filtered_df['PurchasePrice'].quantile(0.95)
    hist_data = filtered_df[filtered_df['PurchasePrice'] < q95]
    fig_hist = px.histogram(hist_data, x="PurchasePrice", nbins=50, title="Price Histogram (Bottom 95%)")
    st.plotly_chart(fig_hist, use_container_width=True)
    
    if len(selected_suburbs) != 1:
        st.subheader("🏘️ Top Suburbs by Sales Volume")
        top_subs = filtered_df['Suburb'].value_counts().head(10).reset_index()
        top_subs.columns = ['Suburb', 'Sales']
        fig_bar = px.bar(top_subs, x='Sales', y='Suburb', orientation='h', title="Top 10 Suburbs by Volume")
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

def tab_predict(df):
    st.header("🤖 Estimate House Price")
    st.markdown("Use our Machine Learning model to estimate the value of a property.")
    
    model = load_model()
    if model is None:
        st.warning("⚠️ Model not found. Please train the model first by running `scripts/train_model.py`.")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        # User Inputs
        suburb = st.selectbox("Suburb", sorted(df['Suburb'].unique()))
        prop_type = st.selectbox("Property Type", sorted(df['PropertyType'].unique()))
        area = st.number_input("Area (sqm)", min_value=10.0, max_value=10000.0, value=500.0)
        
    with col2:
        postcode = st.selectbox("Postcode (Optional Estimate)", sorted(df['Postcode'].unique())) 
        # Ideally we filter postcode based on suburb, but for MVP separate is fine or we get it from data
        # Let's try to lookup postcode from suburb if possible
        potential_postcodes = df[df['Suburb'] == suburb]['Postcode'].unique()
        if len(potential_postcodes) > 0:
            default_postcode = potential_postcodes[0]
        else:
            default_postcode = postcode
            
        # Display selected (or auto-selected) encoded features info
        st.info(f"📍 Location: {suburb}, {default_postcode}")

    if st.button("Estimate Price", type="primary"):
        # Prepare Input Data
        # Features used in training: 
        # ['DistrictCode', 'Suburb', 'Postcode', 'Area', 'Zoning', 'PropertyType', 'Year', 'Month', 'Quarter']
        # We need to fill these.
        
        # Most of these are categorical. We can put placeholders for unknowns like DistrictCode/Zoning if we don't ask user.
        # Or better, exclude them from features if they aren't critical.
        # But CatBoost needs all features present during training.
        
        # We'll use "mode" (most frequent) from the suburb for missing fields like Zoning/DistrictCode
        suburb_data = df[df['Suburb'] == suburb]
        if not suburb_data.empty:
            default_district = suburb_data['DistrictCode'].mode()[0]
            default_zoning = suburb_data['Zoning'].mode()[0]
        else:
            default_district = "UNKNOWN"
            default_zoning = "UNKNOWN"
            
        today = pd.Timestamp.now()
        
        input_data = pd.DataFrame([{
            'DistrictCode': default_district,
            'Suburb': suburb,
            'Postcode': str(default_postcode),
            'Area': area,
            'Zoning': default_zoning,
            'PropertyType': prop_type,
            'Year': today.year,
            'Month': today.month,
            'Quarter': today.quarter
        }])
        
        # Predict
        prediction = model.predict(input_data)[0]
        
        st.success(f"### Estimated Value: ${prediction:,.0f}")
        st.caption("Note: This is an automated estimate based on historical data. Does not replace a professional valuation.")

def main():
    st.title("🏡 Sydney House Price Estimator")
    
    with st.spinner("Loading Data..."):
        df = load_data()
        
    if df is None:
        st.error("Data not found.")
        return

    tab1, tab2 = st.tabs(["🔎 Explore Data", "🤖 Estimate Price"])
    
    with tab1:
        tab_explore(df)
    
    with tab2:
        tab_predict(df)

if __name__ == "__main__":
    main()
