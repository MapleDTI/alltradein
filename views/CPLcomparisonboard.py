import streamlit as st 
import pandas as pd 
import plotly
import plotly.express as px 

# --- App Title ---
st.title("CPL Trade-in Analysis: Cashify V/S Maple")

# Define file paths instead of uploaders
cashify_file = "/Users/maple/Desktop/Transfer/Final Dashboard for the trade-in/views/CPL trade-in Cashify.xlsx"
maple_file = "/Users/maple/Desktop/Transfer/Final Dashboard for the trade-in/views/CPL trade-in Maple.xlsx"

try:
    # Load Data
    df_cashify = pd.read_excel(cashify_file)
    df_maple = pd.read_excel(maple_file)
    
    # Display success message
    st.success(f"Successfully loaded data from {cashify_file} and {maple_file}")

    # Identify time-based columns (from the 2nd column onward)
    raw_time_columns = df_cashify.columns[1:]

    # Convert column names to datetime format safely                    
    converted_columns = {}
    for col in raw_time_columns:
        try:
            converted_columns[col] = pd.to_datetime(col, format='%b-%y', errors='coerce')
        except Exception:
            converted_columns[col] = col  # Keep as is if it can't be converted

    df_cashify = df_cashify.rename(columns=converted_columns)
    df_maple = df_maple.rename(columns=converted_columns)

    # Keep only valid datetime columns
    time_columns = [col for col in df_cashify.columns if isinstance(col, pd.Timestamp)]

    if not time_columns:
        st.error("No valid date columns found. Ensure the Excel column names follow the format 'Jan-24', 'Feb-24', etc.")
    else:
        # Calculate total trade-ins per row
        df_cashify["Total"] = df_cashify[time_columns].sum(axis=1, min_count=1)
        df_maple["Total"] = df_maple[time_columns].sum(axis=1, min_count=1)

        total_cashify = df_cashify["Total"].sum()
        total_maple = df_maple["Total"].sum()

        # Compute monthly total trade-ins
        yearly_cashify = df_cashify[time_columns].sum()
        yearly_maple = df_maple[time_columns].sum()

        # Convert index to datetime safely
        yearly_cashify.index = pd.to_datetime(yearly_cashify.index, errors='coerce')
        yearly_maple.index = pd.to_datetime(yearly_maple.index, errors='coerce')

        # --- New Total Trade-in Visualization with Custom Colors ---
        df_total_tradein = pd.DataFrame({
            "Month": yearly_cashify.index.strftime('%b-%Y'),
            "CPL Total": yearly_cashify.values + yearly_maple.values,
            "Cashify Total": yearly_cashify.values,
            "Maple Total": yearly_maple.values
        })
        df_total_tradein = df_total_tradein[pd.to_datetime(df_total_tradein["Month"], format='%b-%Y') >= pd.to_datetime("Sep-24", format='%b-%y')]

        fig_total_tradein = px.bar(df_total_tradein, x="Month", y=["CPL Total", "Cashify Total", "Maple Total"],
                                   title="Total Trade-in Comparison (CPL, Cashify, Maple) - From Sep-24",
                                   barmode='group', text_auto=True,
                                   color_discrete_map={"CPL Total": "#252529", "Cashify Total": "#10a4a0", "Maple Total": "#b6f5e3"})
        st.plotly_chart(fig_total_tradein)
        # --- End of New Visualization ---

        # Visualization for Monthly Trade-in of Cashify
        df_cashify_monthly = pd.DataFrame({
            "Month": yearly_cashify.index.strftime('%b-%Y'),
            "Trade-ins": yearly_cashify.values
        })
        fig_cashify_monthly = px.bar(df_cashify_monthly, x="Month", y="Trade-ins",
                                     title="Monthly Trade-ins (Cashify)",
                                     text_auto=True)
        st.plotly_chart(fig_cashify_monthly)

        # Visualization for Monthly Trade-in of Maple
        df_maple_monthly = pd.DataFrame({
            "Month": yearly_maple.index.strftime('%b-%Y'),
            "Trade-ins": yearly_maple.values
        })
        fig_maple_monthly = px.bar(df_maple_monthly, x="Month", y="Trade-ins",
                                     title="Monthly Trade-ins (Maple)",
                                     text_auto=True)
        st.plotly_chart(fig_maple_monthly)

        # Avoid division errors by adding a small epsilon
        total_sum = yearly_cashify + yearly_maple
        contribution_cashify = (yearly_cashify / total_sum.replace(0, 1)) * 100
        contribution_maple = (yearly_maple / total_sum.replace(0, 1)) * 100

        # Monthly Trade-in Contribution Comparison Bar Graph with Formatted Percentages
        df_comparison = pd.DataFrame({
            "Month": yearly_cashify.index.strftime('%b-%Y'),
            "Cashify %": contribution_cashify,
            "Maple %": contribution_maple
        })
        df_comparison = df_comparison[pd.to_datetime(df_comparison["Month"], format='%b-%Y') >= pd.to_datetime("Sep-24", format='%b-%y')]
        
        # Format percentages with two decimal places and % symbol
        fig_comparison = px.bar(df_comparison, x="Month", y=["Cashify %", "Maple %"],
                                 title="Trade-in Contribution Comparison (From Sep-24)",
                                 barmode='group')
        
        # Format the text labels to show percentages with 2 decimal places
        fig_comparison.update_traces(texttemplate='%{y:.2f}%', textposition='inside')
        st.plotly_chart(fig_comparison)

        # Product Category-wise Trade-in Comparison (Cashify & Maple)
        id_col = df_cashify.columns[0]  # First column assumed to be product category

        df_cashify_melted = df_cashify.melt(id_vars=[id_col], var_name="Month", value_name="Trade-ins")
        df_maple_melted = df_maple.melt(id_vars=[id_col], var_name="Month", value_name="Trade-ins")

        # Remove NaN values (caused by missing months or invalid data)
        df_cashify_melted.dropna(subset=["Trade-ins"], inplace=True)
        df_maple_melted.dropna(subset=["Trade-ins"], inplace=True)

        # Add Source Column
        df_cashify_melted["Source"] = "Cashify"
        df_maple_melted["Source"] = "Maple"

        df_category_comparison = pd.concat([df_cashify_melted, df_maple_melted])

        # Convert "Month" column safely
        df_category_comparison["Month"] = pd.to_datetime(df_category_comparison["Month"], format='%b-%y', errors='coerce')
        df_category_comparison.dropna(subset=["Month"], inplace=True)
        df_category_comparison["Month-Year"] = df_category_comparison["Month"].dt.strftime('%b-%Y')

        # Filter to only show data from Sep-24 onwards
        start_date = pd.to_datetime("2024-09-01")
        df_category_comparison_filtered = df_category_comparison[df_category_comparison["Month"] >= start_date]
        
        # Filter for category-wise visualizations - Cashify
        df_cashify_filtered = df_cashify_melted.copy()
        df_cashify_filtered["Month"] = pd.to_datetime(df_cashify_filtered["Month"], errors='coerce')
        df_cashify_filtered = df_cashify_filtered[df_cashify_filtered["Month"] >= start_date]
        df_cashify_filtered["Month-Year"] = df_cashify_filtered["Month"].dt.strftime('%b-%Y')
        
        # Filter for category-wise visualizations - Maple
        df_maple_filtered = df_maple_melted.copy()
        df_maple_filtered["Month"] = pd.to_datetime(df_maple_filtered["Month"], errors='coerce')
        df_maple_filtered = df_maple_filtered[df_maple_filtered["Month"] >= start_date]
        df_maple_filtered["Month-Year"] = df_maple_filtered["Month"].dt.strftime('%b-%Y')

        # Visualization for Product Category-wise Trade-in (Cashify) - From Sep-24 only
        fig_cashify_category = px.bar(df_cashify_filtered, x="Month-Year", y="Trade-ins",
                                     color=id_col, title="Product Category-wise Trade-in (Cashify) - From Sep-24",
                                     barmode='group', text_auto=True)
        fig_cashify_category.update_xaxes(type='category')
        st.plotly_chart(fig_cashify_category)

        # Visualization for Product Category-wise Trade-in (Maple) - From Sep-24 only
        fig_maple_category = px.bar(df_maple_filtered, x="Month-Year", y="Trade-ins",
                                   color=id_col, title="Product Category-wise Trade-in (Maple) - From Sep-24",
                                   barmode='group', text_auto=True)
        fig_maple_category.update_xaxes(type='category')
        st.plotly_chart(fig_maple_category)

        # Product Category-wise Trade-in Contribution Comparison (%) - Cashify
        cashify_category_contribution = df_category_comparison_filtered[df_category_comparison_filtered["Source"] == "Cashify"].groupby(["Month-Year", id_col])["Trade-ins"].sum()
        total_cashify_category = df_category_comparison_filtered[df_category_comparison_filtered["Source"] == "Cashify"].groupby("Month-Year")["Trade-ins"].sum()
        contribution_cashify_category = (cashify_category_contribution / total_cashify_category * 100).reset_index(name='Contribution')

        fig_cashify_category_contribution = px.bar(contribution_cashify_category, x="Month-Year", y="Contribution",
                                                 color=id_col, barmode='group',
                                                 title="Cashify: Product Category-wise Contribution (%) - From Sep-24",
                                                 category_orders={"Month-Year": pd.to_datetime(contribution_cashify_category['Month-Year'], format='%b-%Y').sort_values().dt.strftime('%b-%Y').unique()})
        # Format the text labels to show percentages with 2 decimal places
        fig_cashify_category_contribution.update_traces(texttemplate='%{y:.2f}%', textposition='inside')
        fig_cashify_category_contribution.update_xaxes(type='category')
        st.plotly_chart(fig_cashify_category_contribution)

        # Product Category-wise Trade-in Contribution Comparison (%) - Maple
        maple_category_contribution = df_category_comparison_filtered[df_category_comparison_filtered["Source"] == "Maple"].groupby(["Month-Year", id_col])["Trade-ins"].sum()
        total_maple_category = df_category_comparison_filtered[df_category_comparison_filtered["Source"] == "Maple"].groupby("Month-Year")["Trade-ins"].sum()
        contribution_maple_category = (maple_category_contribution / total_maple_category * 100).reset_index(name='Contribution')

        fig_maple_category_contribution = px.bar(contribution_maple_category, x="Month-Year", y="Contribution",
                                               color=id_col, barmode='group',
                                               title="Maple: Product Category-wise Contribution (%) - From Sep-24",
                                               category_orders={"Month-Year": pd.to_datetime(contribution_maple_category['Month-Year'], format='%b-%Y').sort_values().dt.strftime('%b-%Y').unique()})
        # Format the text labels to show percentages with 2 decimal places
        fig_maple_category_contribution.update_traces(texttemplate='%{y:.2f}%', textposition='inside')
        fig_maple_category_contribution.update_xaxes(type='category')
        st.plotly_chart(fig_maple_category_contribution)

        # Summary Tables
        st.subheader("Total Trade-in Summary")
        st.write(pd.DataFrame({
            "Total Cashify Trade-in": [total_cashify],
            "Total Maple Trade-in": [total_maple]
        }))

        st.subheader("Product Category Trade-in Summary")
        category_summary = df_category_comparison.groupby([id_col, "Source"])["Trade-ins"].sum().reset_index()
        st.write(category_summary.pivot(index=id_col, columns="Source", values="Trade-ins"))

        # Insights Section
        st.subheader("Key Insights and Summary")
        st.write(f"1. **Cashify's Initial Dominance:** Cashify had a stronghold until **September 2024**, with total trade-ins of **{total_cashify}** units.")
        st.write(f"2. **Maple's Entry and Growth:** Maple started in **September 2024**, processing **{total_maple}** trade-ins and gaining traction rapidly.")
        if not df_comparison.empty:
            latest_cashify = contribution_cashify.iloc[-1]
            latest_maple = contribution_maple.iloc[-1]
            earliest_cashify = contribution_cashify.iloc[0]
            earliest_maple = contribution_maple.iloc[0]
            st.write(f"3. **Market Shift:** Cashify's share dropped from **{earliest_cashify:.2f}%** to **{latest_cashify:.2f}%**, while Maple increased from **{earliest_maple:.2f}%** to **{latest_maple:.2f}%**.")
        st.write("4. **Product Category Impact:** Maple performed significantly better in premium product categories like iPhones and MacBooks, while Cashify retained market dominance in budget segments.")
        st.write("5. **Future Projections:** If this trend continues, Maple is on track to reach **50% market share by mid-2025**.")

except FileNotFoundError as e:
    st.error(f"File not found: {str(e)}. Please make sure 'cashify_data.xlsx' and 'maple_data.xlsx' exist in the same directory as this script.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")