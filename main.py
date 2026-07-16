import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import base64

def main():
    st.set_page_config(page_title="Result Analysis System", layout="wide")
    
    # Custom CSS to improve appearance
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">Result Analysis System</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    pages = ["Data Upload", "Basic Analysis", "Advanced Analysis", "Report Generation"]
    selection = st.sidebar.radio("Go to", pages)
    
    # Initialize session state if not exists
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    
    # Data Upload Page
    if selection == "Data Upload":
        st.markdown('<h2 class="section-header">Data Upload</h2>', unsafe_allow_html=True)
        
        # File upload with multiple formats support
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                # Read the file based on format
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Save to session state
                st.session_state.df = df
                st.session_state.processed = True
                
                # Display raw data with filter options
                st.subheader("Preview Data")
                
                # Column selector for display
                all_columns = df.columns.tolist()
                selected_columns = st.multiselect("Select columns to display", all_columns, default=all_columns[:5] if len(all_columns) > 5 else all_columns)
                
                if selected_columns:
                    st.dataframe(df[selected_columns])
                
                # Display data summary
                st.subheader("Data Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Total Records: {len(df)}")
                    st.write(f"Total Features: {len(df.columns)}")
                with col2:
                    # Detect numeric columns for potential mark columns
                    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
                    st.write(f"Potential Mark Columns: {', '.join(numeric_columns) if numeric_columns else 'None detected'}")
                
                # Data cleaning options
                st.subheader("Data Cleaning Options")
                
                # Handle missing values
                if df.isna().any().any():
                    st.warning(f"Missing values detected in dataset: {df.isna().sum().sum()} total missing values")
                    missing_handling = st.radio("How to handle missing values?", 
                                               ["Drop rows with missing values", 
                                                "Fill missing values with mean/mode", 
                                                "Keep as is"])
                    
                    if missing_handling == "Drop rows with missing values":
                        df = df.dropna()
                        st.success(f"Dropped rows with missing values. New shape: {df.shape}")
                        st.session_state.df = df
                    elif missing_handling == "Fill missing values with mean/mode":
                        for col in df.columns:
                            if pd.api.types.is_numeric_dtype(df[col]):
                                df[col] = df[col].fillna(df[col].mean())
                            else:
                                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
                        st.success("Filled missing values with mean/mode values")
                        st.session_state.df = df
                
                # Identify and handle outliers in numeric columns
                st.subheader("Outlier Detection")
                outlier_columns = st.multiselect("Select columns to check for outliers", 
                                                numeric_columns,
                                                default=[])
                
                if outlier_columns:
                    for col in outlier_columns:
                        q1 = df[col].quantile(0.25)
                        q3 = df[col].quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        
                        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                        if not outliers.empty:
                            st.warning(f"Found {len(outliers)} outliers in column '{col}'")
                            handle_outliers = st.radio(f"How to handle outliers in '{col}'?", 
                                                      ["Leave outliers as is", 
                                                       "Cap outliers at boundaries",
                                                       "Remove outlier rows"], key=f"outlier_{col}")
                            
                            if handle_outliers == "Cap outliers at boundaries":
                                df[col] = df[col].clip(lower_bound, upper_bound)
                                st.success(f"Capped outliers in column '{col}'")
                                st.session_state.df = df
                            elif handle_outliers == "Remove outlier rows":
                                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                                st.success(f"Removed {len(outliers)} outlier rows from column '{col}'")
                                st.session_state.df = df
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            st.info("Please upload a file to continue.")

    # Basic Analysis Page
    elif selection == "Basic Analysis":
        if st.session_state.processed:
            df = st.session_state.df
            st.markdown('<h2 class="section-header">Basic Analysis</h2>', unsafe_allow_html=True)
            
            # Select mark column
            st.subheader("Select Mark Column")
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            mark_column = st.selectbox("Select the column containing marks:", numeric_columns)
            
            if mark_column:
                # Basic statistics
                st.subheader("Statistical Summary")
                stats = df[mark_column].describe().to_frame().T
                st.dataframe(stats)
                
                # Mark distribution
                st.subheader("Distribution of Marks")
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Create a more informative histogram
                sns.histplot(data=df, x=mark_column, kde=True, ax=ax, bins=20)
                ax.axvline(df[mark_column].mean(), color='red', linestyle='--', label=f'Mean: {df[mark_column].mean():.2f}')
                ax.axvline(df[mark_column].median(), color='green', linestyle='--', label=f'Median: {df[mark_column].median():.2f}')
                ax.set_xlabel(f"{mark_column}")
                ax.set_ylabel("Frequency")
                ax.set_title(f"Distribution of {mark_column}")
                ax.legend()
                st.pyplot(fig)
                
                # Pass/Fail Analysis with customizable threshold
                st.subheader("Pass/Fail Analysis")

                # User enters the maximum mark
                max_mark = st.number_input("Enter maximum mark:", min_value=1.0, step=1.0)
                
                # Fix minimum mark at 0
                min_mark = 0.0  
                
                # Only show slider if user has entered a valid max mark
                if max_mark > 0:
                    pass_mark = st.slider(
                        "Set pass mark:", 
                        min_value=min_mark, 
                        max_value=max_mark, 
                        value=max_mark * 0.4
                    )

                
                # Create result column
                df['Result'] = df[mark_column].apply(lambda x: 'Pass' if x >= pass_mark else 'Fail')
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    # Create pie chart
                    result_counts = df['Result'].value_counts()
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.pie(result_counts.values, labels=result_counts.index, autopct='%1.1f%%', 
                          startangle=90, colors=['#4CAF50', '#F44336'] if 'Pass' in result_counts.index else ['#F44336', '#4CAF50'])
                    ax.axis('equal')
                    ax.set_title("Pass/Fail Distribution")
                    st.pyplot(fig)
                
                with col2:
                    # Pass percentage and statistics
                    pass_percentage = (df['Result'] == 'Pass').mean() * 100
                    st.metric("Pass Percentage", f"{pass_percentage:.2f}%")
                    
                    passed_df = df[df['Result'] == 'Pass']
                    failed_df = df[df['Result'] == 'Fail']
                    
                    st.write(f"Total Students: {len(df)}")
                    st.write(f"Passed: {len(passed_df)} students")
                    st.write(f"Failed: {len(failed_df)} students")
                    
                    if len(passed_df) > 0:
                        st.write(f"Average score of passed students: {passed_df[mark_column].mean():.2f}")
                    if len(failed_df) > 0:
                        st.write(f"Average score of failed students: {failed_df[mark_column].mean():.2f}")
                
                # Top and bottom performers
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Top 5 Performers")
                    name_columns = df.select_dtypes(include=['object']).columns.tolist()
                    id_column = st.selectbox("Select student name/ID column (optional):", 
                                        ['None'] + name_columns,
                                        index=0)
                    
                    if id_column != 'None':
                        top_performers = df.nlargest(5, mark_column)[[id_column, mark_column, 'Result']]
                    else:
                        top_performers = df.nlargest(5, mark_column)[[mark_column, 'Result']]
                    
                    st.table(top_performers)
                
                with col2:
                    st.subheader("Bottom 5 Performers")
                    if id_column != 'None':
                        bottom_performers = df.nsmallest(5, mark_column)[[id_column, mark_column, 'Result']]
                    else:
                        bottom_performers = df.nsmallest(5, mark_column)[[mark_column, 'Result']]
                    
                    st.table(bottom_performers)
                
            else:
                st.warning("Please select a mark column to continue.")
        else:
            st.warning("Please upload data first in the 'Data Upload' section.")
    
    # Advanced Analysis Page
    elif selection == "Advanced Analysis":
        if st.session_state.processed:
            df = st.session_state.df
            st.markdown('<h2 class="section-header">Advanced Analysis</h2>', unsafe_allow_html=True)
            
            # Select mark columns for comparison
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            
            # Subject/Mark Category Comparison
            st.subheader("Subject/Mark Category Comparison")
            comparison_columns = st.multiselect("Select columns to compare:", numeric_columns)
            
            if len(comparison_columns) > 1:
                # Create comparison visualizations
                st.subheader("Comparative Analysis")
                
                # Box plot comparison
                fig, ax = plt.subplots(figsize=(12, 6))
                df_melt = df[comparison_columns].melt()
                sns.boxplot(x='variable', y='value', data=df_melt, ax=ax)
                ax.set_xlabel("Subjects/Categories")
                ax.set_ylabel("Marks")
                ax.set_title("Mark Distribution Across Subjects/Categories")
                st.pyplot(fig)
                
                # Correlation analysis
                st.subheader("Correlation Analysis")
                corr = df[comparison_columns].corr()
                
                fig, ax = plt.subplots(figsize=(10, 8))
                mask = np.zeros_like(corr, dtype=bool)
                mask[np.triu_indices_from(mask, k=1)] = True
                cmap = sns.diverging_palette(230, 20, as_cmap=True)
                
                sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                           square=True, linewidths=.5, annot=True, fmt='.2f', ax=ax)
                ax.set_title("Correlation Between Subjects/Categories")
                st.pyplot(fig)
                
                # Scatter plot matrix for detailed comparison
                if len(comparison_columns) <= 4:  # Limit to avoid overloading
                    st.subheader("Detailed Pairwise Comparison")
                    fig = sns.pairplot(df[comparison_columns], height=2.5, diag_kind='kde')
                    fig.fig.suptitle("Pairwise Relationships Between Subjects/Categories", y=1.02)
                    st.pyplot(fig.fig)
            
            # Grade distribution analysis
            st.subheader("Grade Distribution Analysis")
            grade_column = st.selectbox("Select column for grade analysis:", numeric_columns)
            
            if grade_column:
                # Define grade boundaries
                st.write("Define grade boundaries:")
                col1, col2 = st.columns(2)
                
                with col1:
                    min_val = float(df[grade_column].min())
                    max_val = float(df[grade_column].max())
                    
                    # Custom grade boundaries
                    use_custom_grades = st.checkbox("Use custom grade boundaries", value=False)
                    
                    if use_custom_grades:
                        grade_boundaries = {}
                        grade_boundaries['A'] = st.slider("Minimum mark for A grade", min_val, max_val, max_val * 0.8)
                        grade_boundaries['B'] = st.slider("Minimum mark for B grade", min_val, grade_boundaries['A'] - 0.01, max_val * 0.7)
                        grade_boundaries['C'] = st.slider("Minimum mark for C grade", min_val, grade_boundaries['B'] - 0.01, max_val * 0.6)
                        grade_boundaries['D'] = st.slider("Minimum mark for D grade", min_val, grade_boundaries['C'] - 0.01, max_val * 0.5)
                        grade_boundaries['F'] = min_val
                    else:
                        # Default percentage-based grades
                        percentage_max = 100 if max_val <= 100 else max_val
                        grade_boundaries = {
                            'A': percentage_max * 0.8,
                            'B': percentage_max * 0.7,
                            'C': percentage_max * 0.6,
                            'D': percentage_max * 0.5,
                            'F': min_val
                        }
                
                # Assign grades
                def assign_grade(mark):
                    if mark >= grade_boundaries['A']:
                        return 'A'
                    elif mark >= grade_boundaries['B']:
                        return 'B'
                    elif mark >= grade_boundaries['C']:
                        return 'C'
                    elif mark >= grade_boundaries['D']:
                        return 'D'
                    else:
                        return 'F'
                
                df['Grade'] = df[grade_column].apply(assign_grade)
                
                with col2:
                    # Grade distribution visualization
                    grade_counts = df['Grade'].value_counts().reindex(['A', 'B', 'C', 'D', 'F'])
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
                    grade_counts.plot(kind='bar', ax=ax, color=colors)
                    ax.set_xlabel('Grade')
                    ax.set_ylabel('Number of Students')
                    ax.set_title('Grade Distribution')
                    
                    # Add count labels on top of bars
                    for i, count in enumerate(grade_counts):
                        ax.annotate(f'{count}', xy=(i, count), ha='center', va='bottom')
                    
                    st.pyplot(fig)
                
                # Grade statistics
                st.subheader("Grade Statistics")
                grade_stats = df.groupby('Grade')[grade_column].agg(['count', 'mean', 'min', 'max']).reset_index()
                grade_stats.columns = ['Grade', 'Count', 'Average Score', 'Minimum Score', 'Maximum Score']
                grade_stats = grade_stats.sort_values(by='Grade')
                st.table(grade_stats)
                
                # Percentile analysis
                st.subheader("Percentile Analysis")
                
                percentiles = [0, 10, 25, 50, 75, 90, 100]
                percentile_values = np.percentile(df[grade_column], percentiles)
                
                percentile_df = pd.DataFrame({
                    'Percentile': percentiles,
                    'Score': percentile_values
                })
                
                st.table(percentile_df)
                
                # Percentile graph
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(percentile_df['Percentile'], percentile_df['Score'], marker='o', linestyle='-', color='blue')
                ax.set_xlabel('Percentile')
                ax.set_ylabel('Score')
                ax.set_title('Score Distribution by Percentile')
                ax.grid(True)
                st.pyplot(fig)
        else:
            st.warning("Please upload data first in the 'Data Upload' section.")
    
    # Report Generation Page
    elif selection == "Report Generation":
        if st.session_state.processed:
            df = st.session_state.df
            st.markdown('<h2 class="section-header">Report Generation</h2>', unsafe_allow_html=True)
            
            # Report options
            st.subheader("Report Configuration")
            
            # Select mark columns for report
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            name_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            mark_columns = st.multiselect("Select mark columns to include in report:", numeric_columns)
            id_column = st.selectbox("Select student ID/name column:", ['None'] + name_columns, index=0)
            
            if mark_columns:
                # Define pass mark for each column
                st.subheader("Define Pass Marks")
                pass_marks = {}
                
                for col in mark_columns:
                    min_val = 0.0
                    max_val = st.number_input(f"Enter maximum mark for {col}:", min_value=1.0, step=1.0)
                    pass_marks[col] = st.slider(f"Pass mark for {col}:", min_val, max_val, max_val * 0.4, key=f"pass_{col}")
                
                # Generate the report
                st.subheader("Generated Report")
                
                # Create a copy of the DataFrame for the report
                report_df = df.copy()
                
                # Add result for each subject
                for col in mark_columns:
                    report_df[f"{col}_Result"] = report_df[col].apply(lambda x: 'Pass' if x >= pass_marks[col] else 'Fail')
                
                # Create overall result
                def overall_result(row):
                    results = [row[f"{col}_Result"] for col in mark_columns]
                    if all(result == 'Pass' for result in results):
                        return 'Pass'
                    else:
                        return 'Fail'
                
                report_df['Overall_Result'] = report_df.apply(overall_result, axis=1)
                
                # Calculate total and percentage
                if len(mark_columns) > 0:
                    report_df['Total'] = report_df[mark_columns].sum(axis=1)
                    max_possible = sum(df[col].max() for col in mark_columns)
                    report_df['Percentage'] = (report_df['Total'] / max_possible) * 100
                
                # Display report
                display_columns = []
                if id_column != 'None':
                    display_columns.append(id_column)
                
                display_columns.extend(mark_columns)
                
                for col in mark_columns:
                    display_columns.append(f"{col}_Result")
                
                display_columns.extend(['Total', 'Percentage', 'Overall_Result'])
                
                # Show the report
                st.dataframe(report_df[display_columns])
                
                # Summary statistics
                st.subheader("Report Summary")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Overall pass rate
                    overall_pass_rate = (report_df['Overall_Result'] == 'Pass').mean() * 100
                    st.metric("Overall Pass Rate", f"{overall_pass_rate:.2f}%")
                    
                    # Subject-wise pass rates
                    st.write("Subject-wise Pass Rates:")
                    for col in mark_columns:
                        pass_rate = (report_df[f"{col}_Result"] == 'Pass').mean() * 100
                        st.write(f"{col}: {pass_rate:.2f}%")
                
                with col2:
                    # Average marks per subject
                    st.write("Average Marks per Subject:")
                    for col in mark_columns:
                        avg_mark = report_df[col].mean()
                        max_mark = report_df[col].max()
                        st.write(f"{col}: {avg_mark:.2f}/{max_mark:.2f} ({(avg_mark/max_mark*100):.2f}%)")
                    
                    if len(mark_columns) > 0:
                        st.write(f"Average Total: {report_df['Total'].mean():.2f}/{max_possible:.2f}")
                        st.write(f"Average Percentage: {report_df['Percentage'].mean():.2f}%")
                
                # Download options
                st.subheader("Download Report")
                
                # Create Excel report
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Create sheet for the report
                    report_df[display_columns].to_excel(writer, sheet_name='Detailed Report', index=False)
                    
                    # Create summary sheet
                    summary_data = {
                        'Metric': ['Total Students', 'Overall Pass Rate', 'Average Percentage'],
                        'Value': [
                            len(report_df),
                            f"{overall_pass_rate:.2f}%",
                            f"{report_df['Percentage'].mean():.2f}%"
                        ]
                    }
                    
                    for col in mark_columns:
                        summary_data['Metric'].append(f"{col} Pass Rate")
                        pass_rate = (report_df[f"{col}_Result"] == 'Pass').mean() * 100
                        summary_data['Value'].append(f"{pass_rate:.2f}%")
                        
                        summary_data['Metric'].append(f"{col} Average")
                        avg_mark = report_df[col].mean()
                        max_mark = report_df[col].max()
                        summary_data['Value'].append(f"{avg_mark:.2f}/{max_mark:.2f} ({(avg_mark/max_mark*100):.2f}%)")
                    
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Create a sheet for statistical analysis
                    stats_df = report_df[mark_columns].describe().T
                    stats_df['Pass Rate (%)'] = [
                        (report_df[f"{col}_Result"] == 'Pass').mean() * 100 for col in mark_columns
                    ]
                    stats_df.to_excel(writer, sheet_name='Statistics')
                    
                    # Create workbook and worksheet objects
                    workbook = writer.book
                    
                    # Add chart sheet with pass/fail distribution
                    chart_sheet = workbook.add_worksheet('Charts')
                    
                    # Add pass/fail pie chart
                    chart = workbook.add_chart({'type': 'pie'})
                    
                    # Write the data for the chart
                    summary_sheet = workbook.get_worksheet_by_name('Summary')
                    summary_sheet.write_column('D1', ['Pass', 'Fail'])
                    summary_sheet.write_column('E1', [
                        sum(report_df['Overall_Result'] == 'Pass'),
                        sum(report_df['Overall_Result'] == 'Fail')
                    ])
                    
                    # Configure the chart
                    chart.add_series({
                        'name': 'Overall Result',
                        'categories': '=Summary!$D$1:$D$2',
                        'values': '=Summary!$E$1:$E$2',
                    })
                    
                    chart.set_title({'name': 'Pass/Fail Distribution'})
                    chart_sheet.insert_chart('A1', chart)
                
                # Download button
                excel_data = buffer.getvalue()
                b64 = base64.b64encode(excel_data).decode()
                href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'
                
                st.download_button(
                    label="Download Complete Report (Excel)",
                    data=excel_data,
                    file_name="result_analysis_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # Download simplified CSV
                csv = report_df[display_columns].to_csv(index=False)
                st.download_button(
                    label="Download Simple Report (CSV)",
                    data=csv,
                    file_name="result_analysis_simple.csv", 
                    mime="text/csv"
                )
            else:
                st.warning("Please select at least one mark column for the report.")
        else:
            st.warning("Please upload data first in the 'Data Upload' section.")

if __name__ == "__main__":
    main()
