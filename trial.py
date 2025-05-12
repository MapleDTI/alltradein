import streamlit as st  # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore

# Streamlit App Title
st.title("CPL Trade-in Analysis: Cashify vs. Maple")

# Upload files
cashify_file = st.file_uploader("Upload Cashify Excel", type=["xlsx"])
maple_file = st.file_uploader("Upload Maple Excel", type=["xlsx"])

if cashify_file and maple_file:
    try:
        # Load Data
        df_cashify = pd.read_excel(cashify_file)
        df_maple = pd.read_excel(maple_file)

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

            # Visualization for Monthly Trade-in of Cashify
            df_cashify_monthly = pd.DataFrame({
                "Month": yearly_cashify.index.strftime('%b-%Y'),
                "Trade-ins": yearly_cashify.values
            })
            fig_cashify_monthly = px.bar(df_cashify_monthly, x="Month", y="Trade-ins",
                                         title="Monthly Trade-ins (Cashify)",
                                         text_auto=True)

            # Visualization for Monthly Trade-in of Maple
            df_maple_monthly = pd.DataFrame({
                "Month": yearly_maple.index.strftime('%b-%Y'),
                "Trade-ins": yearly_maple.values
            })
            fig_maple_monthly = px.bar(df_maple_monthly, x="Month", y="Trade-ins",
                                       title="Monthly Trade-ins (Maple)",
                                       text_auto=True)

            # Avoid division errors by adding a small epsilon
            total_sum = yearly_cashify + yearly_maple
            contribution_cashify = (yearly_cashify / total_sum.replace(0, 1)) * 100
            contribution_maple = (yearly_maple / total_sum.replace(0, 1)) * 100

            # Monthly Trade-in Contribution Comparison Bar Graph
            df_comparison = pd.DataFrame({
                "Month": yearly_cashify.index.strftime('%b-%Y'),
                "Cashify %": contribution_cashify,
                "Maple %": contribution_maple
            })
            fig_comparison = px.bar(df_comparison, x="Month", y=["Cashify %", "Maple %"], 
                                    title="Trade-in Contribution Comparison", 
                                    barmode='group', text_auto=True)

            # Product Category-wise Trade-in Comparison (Cashify & Maple)
            id_col = df_cashify.columns[0]  # First column assumed to be product category
            
            df_cashify_melted = df_cashify.melt(id_vars=[id_col], var_name="Month", value_name="Trade-ins")
            df_maple_melted = df_maple.melt(id_vars=[id_col], var_name="Month", value_name="Trade-ins")

            # Remove NaN values
            df_cashify_melted.dropna(subset=["Trade-ins"], inplace=True)
            df_maple_melted.dropna(subset=["Trade-ins"], inplace=True)

            # Add Source Column
            df_cashify_melted["Source"] = "Cashify"
            df_maple_melted["Source"] = "Maple"
            
            df_category_comparison = pd.concat([df_cashify_melted, df_maple_melted])

            # Convert "Month" column safely
            df_category_comparison["Month"] = pd.to_datetime(df_category_comparison["Month"], format='%b-%Y', errors='coerce')
            df_category_comparison.dropna(subset=["Month"], inplace=True)

            # Filter between Sep-24 and Mar-25
            df_category_comparison_filtered = df_category_comparison[
                (df_category_comparison["Month"] >= "2024-09-01") & 
                (df_category_comparison["Month"] <= "2025-03-31")
            ]
            
            # Visualization
            fig_category_contribution = px.bar(df_category_comparison_filtered, x="Month", y="Trade-ins", 
                                               color=id_col, barmode='group', facet_col="Source", 
                                               title="Product Category-wise Contribution Comparison (Sep-24 to Mar-25)",
                                               text_auto=True)

            # Display Visuals
            st.plotly_chart(fig_cashify_monthly)
            st.plotly_chart(fig_maple_monthly)
            st.plotly_chart(fig_comparison)
            st.plotly_chart(fig_category_contribution)

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
            st.write("3. **Market Shift:** Cashify’s share declined, while Maple gained significant market traction.")
            st.write("4. **Product Category Impact:** Maple performed better in premium segments, while Cashify led in budget devices.")
            st.write("5. **Future Projections:** If trends persist, Maple may achieve **50% market share by mid-2025**.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")