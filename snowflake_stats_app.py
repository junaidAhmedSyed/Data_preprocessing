import streamlit as st
import snowflake.connector
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Snowflake Table Statistics",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'connection' not in st.session_state:
    st.session_state.connection = None
if 'tables' not in st.session_state:
    st.session_state.tables = []

def create_snowflake_connection(account, username, password, warehouse, database, schema):
    """Create and return a Snowflake connection"""
    try:
        conn = snowflake.connector.connect(
            account=account,
            user=username,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        return conn, None
    except Exception as e:
        return None, str(e)

def get_tables_list(connection, database, schema):
    """Get list of tables from the specified database and schema"""
    try:
        cursor = connection.cursor()
        query = f"SHOW TABLES IN {database}.{schema}"
        cursor.execute(query)
        tables = cursor.fetchall()
        return [table[1] for table in tables]  # Table name is in the second column
    except Exception as e:
        st.error(f"Error fetching tables: {str(e)}")
        return []

def get_table_info(connection, database, schema, table_name):
    """Get basic information about the table"""
    try:
        cursor = connection.cursor()
        
        # Get table description
        desc_query = f"DESCRIBE TABLE {database}.{schema}.{table_name}"
        cursor.execute(desc_query)
        columns_info = cursor.fetchall()
        
        # Get row count
        count_query = f"SELECT COUNT(*) FROM {database}.{schema}.{table_name}"
        cursor.execute(count_query)
        row_count = cursor.fetchone()[0]
        
        return columns_info, row_count
    except Exception as e:
        st.error(f"Error getting table info: {str(e)}")
        return None, None

def get_table_sample(connection, database, schema, table_name, sample_size=1000):
    """Get a sample of data from the table"""
    try:
        cursor = connection.cursor()
        query = f"SELECT * FROM {database}.{schema}.{table_name} SAMPLE({min(sample_size, 1000)} ROWS)"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch data
        data = cursor.fetchall()
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)
        return df
    except Exception as e:
        st.error(f"Error sampling table data: {str(e)}")
        return None

def generate_column_statistics(df, column_name):
    """Generate detailed statistics for a specific column"""
    column_data = df[column_name]
    stats = {}
    
    # Basic info
    stats['data_type'] = str(column_data.dtype)
    stats['total_count'] = len(column_data)
    stats['null_count'] = column_data.isnull().sum()
    stats['null_percentage'] = (stats['null_count'] / stats['total_count']) * 100
    stats['unique_count'] = column_data.nunique()
    stats['unique_percentage'] = (stats['unique_count'] / stats['total_count']) * 100
    
    # Type-specific statistics
    if pd.api.types.is_numeric_dtype(column_data):
        non_null_data = column_data.dropna()
        if len(non_null_data) > 0:
            stats['min'] = non_null_data.min()
            stats['max'] = non_null_data.max()
            stats['mean'] = non_null_data.mean()
            stats['median'] = non_null_data.median()
            stats['std'] = non_null_data.std()
            stats['q25'] = non_null_data.quantile(0.25)
            stats['q75'] = non_null_data.quantile(0.75)
    
    elif pd.api.types.is_string_dtype(column_data) or pd.api.types.is_object_dtype(column_data):
        non_null_data = column_data.dropna()
        if len(non_null_data) > 0:
            stats['avg_length'] = non_null_data.astype(str).str.len().mean()
            stats['min_length'] = non_null_data.astype(str).str.len().min()
            stats['max_length'] = non_null_data.astype(str).str.len().max()
            stats['most_common'] = non_null_data.value_counts().head(5).to_dict()
    
    elif pd.api.types.is_datetime64_any_dtype(column_data):
        non_null_data = column_data.dropna()
        if len(non_null_data) > 0:
            stats['min_date'] = non_null_data.min()
            stats['max_date'] = non_null_data.max()
            stats['date_range'] = stats['max_date'] - stats['min_date']
    
    return stats

def create_visualizations(df, column_name, stats):
    """Create appropriate visualizations based on column type"""
    column_data = df[column_name].dropna()
    
    if len(column_data) == 0:
        return None
    
    if pd.api.types.is_numeric_dtype(column_data):
        # Create subplot for numeric data
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Distribution', 'Box Plot', 'Q-Q Plot', 'Summary Stats'),
            specs=[[{"type": "xy"}, {"type": "xy"}],
                   [{"type": "xy"}, {"type": "table"}]]
        )
        
        # Histogram
        fig.add_trace(
            go.Histogram(x=column_data, name="Distribution", nbinsx=30),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(y=column_data, name="Box Plot"),
            row=1, col=2
        )
        
        # Q-Q plot (approximation)
        from scipy import stats as scipy_stats
        theoretical_quantiles = scipy_stats.norm.ppf(np.linspace(0.01, 0.99, len(column_data)))
        sample_quantiles = np.sort(column_data)
        
        fig.add_trace(
            go.Scatter(x=theoretical_quantiles, y=sample_quantiles, 
                      mode='markers', name="Q-Q Plot"),
            row=2, col=1
        )
        
        # Summary table
        summary_data = [
            ['Mean', f"{stats.get('mean', 'N/A'):.2f}"],
            ['Median', f"{stats.get('median', 'N/A'):.2f}"],
            ['Std Dev', f"{stats.get('std', 'N/A'):.2f}"],
            ['Min', f"{stats.get('min', 'N/A'):.2f}"],
            ['Max', f"{stats.get('max', 'N/A'):.2f}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Statistic', 'Value']),
                cells=dict(values=list(zip(*summary_data)))
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False, title=f"Analysis for {column_name}")
        return fig
        
    elif pd.api.types.is_string_dtype(column_data) or pd.api.types.is_object_dtype(column_data):
        # For categorical data
        value_counts = column_data.value_counts().head(20)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Top Values', 'Value Distribution'),
            specs=[[{"type": "xy"}, {"type": "xy"}]]
        )
        
        # Bar chart of top values
        fig.add_trace(
            go.Bar(x=value_counts.index, y=value_counts.values, name="Top Values"),
            row=1, col=1
        )
        
        # Pie chart
        fig.add_trace(
            go.Pie(labels=value_counts.index[:10], values=value_counts.values[:10], name="Distribution"),
            row=1, col=2
        )
        
        fig.update_layout(height=400, title=f"Analysis for {column_name}")
        return fig
    
    return None

# Main app layout
st.markdown('<h1 class="main-header">❄️ Snowflake Table Statistics Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for connection
with st.sidebar:
    st.header("🔗 Snowflake Connection")
    
    with st.form("connection_form"):
        account = st.text_input("Account", help="Your Snowflake account identifier")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        warehouse = st.text_input("Warehouse")
        database = st.text_input("Database")
        schema = st.text_input("Schema")
        
        connect_button = st.form_submit_button("Connect")
        
        if connect_button and all([account, username, password, warehouse, database, schema]):
            with st.spinner("Connecting to Snowflake..."):
                conn, error = create_snowflake_connection(account, username, password, warehouse, database, schema)
                
                if conn:
                    st.session_state.connection = conn
                    st.session_state.connected = True
                    st.success("✅ Connected successfully!")
                    
                    # Get tables list
                    st.session_state.tables = get_tables_list(conn, database, schema)
                    
                else:
                    st.error(f"❌ Connection failed: {error}")
                    st.session_state.connected = False

# Main content area
if st.session_state.connected:
    st.success("🎉 Connected to Snowflake!")
    
    # Table selection
    if st.session_state.tables:
        selected_table = st.selectbox(
            "📊 Select a table to analyze:",
            st.session_state.tables,
            index=0
        )
        
        if selected_table:
            col1, col2 = st.columns([2, 1])
            
            with col2:
                analyze_button = st.button("🔍 Analyze Table", type="primary")
                sample_size = st.slider("Sample size for analysis", 100, 5000, 1000)
            
            with col1:
                st.subheader(f"📋 Table: {selected_table}")
            
            if analyze_button:
                with st.spinner("Fetching table information..."):
                    # Get table basic info
                    columns_info, row_count = get_table_info(
                        st.session_state.connection, database, schema, selected_table
                    )
                    
                    if columns_info and row_count is not None:
                        # Display basic table info
                        st.subheader("📈 Table Overview")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Rows", f"{row_count:,}")
                        with col2:
                            st.metric("Total Columns", len(columns_info))
                        with col3:
                            st.metric("Sample Size", f"{min(sample_size, row_count):,}")
                        
                        # Display column information
                        st.subheader("🗂️ Column Information")
                        columns_df = pd.DataFrame(columns_info, columns=[
                            'Column Name', 'Data Type', 'Nullable', 'Default', 'Primary Key', 'Unique Key', 'Check', 'Expression', 'Comment'
                        ])
                        st.dataframe(columns_df[['Column Name', 'Data Type', 'Nullable']], use_container_width=True)
                        
                        # Get sample data
                        with st.spinner("Sampling table data..."):
                            df_sample = get_table_sample(
                                st.session_state.connection, database, schema, selected_table, sample_size
                            )
                            
                            if df_sample is not None and not df_sample.empty:
                                st.subheader("📊 Data Sample")
                                st.dataframe(df_sample.head(10), use_container_width=True)
                                
                                # Column-wise analysis
                                st.subheader("🔍 Detailed Column Analysis")
                                
                                # Select column for detailed analysis
                                selected_column = st.selectbox(
                                    "Select a column for detailed analysis:",
                                    df_sample.columns.tolist()
                                )
                                
                                if selected_column:
                                    with st.spinner(f"Analyzing column: {selected_column}"):
                                        # Generate statistics
                                        stats = generate_column_statistics(df_sample, selected_column)
                                        
                                        # Display statistics
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            st.metric("Data Type", stats['data_type'])
                                        with col2:
                                            st.metric("Null Count", f"{stats['null_count']} ({stats['null_percentage']:.1f}%)")
                                        with col3:
                                            st.metric("Unique Values", f"{stats['unique_count']} ({stats['unique_percentage']:.1f}%)")
                                        with col4:
                                            st.metric("Total Count", stats['total_count'])
                                        
                                        # Type-specific statistics
                                        if pd.api.types.is_numeric_dtype(df_sample[selected_column]):
                                            st.subheader("📊 Numeric Statistics")
                                            col1, col2, col3, col4 = st.columns(4)
                                            
                                            with col1:
                                                st.metric("Mean", f"{stats.get('mean', 0):.2f}")
                                            with col2:
                                                st.metric("Median", f"{stats.get('median', 0):.2f}")
                                            with col3:
                                                st.metric("Std Dev", f"{stats.get('std', 0):.2f}")
                                            with col4:
                                                st.metric("Range", f"{stats.get('min', 0):.2f} - {stats.get('max', 0):.2f}")
                                        
                                        elif pd.api.types.is_string_dtype(df_sample[selected_column]) or pd.api.types.is_object_dtype(df_sample[selected_column]):
                                            st.subheader("📝 Text Statistics")
                                            col1, col2, col3 = st.columns(3)
                                            
                                            with col1:
                                                st.metric("Avg Length", f"{stats.get('avg_length', 0):.1f}")
                                            with col2:
                                                st.metric("Min Length", stats.get('min_length', 0))
                                            with col3:
                                                st.metric("Max Length", stats.get('max_length', 0))
                                            
                                            if 'most_common' in stats:
                                                st.subheader("🏆 Most Common Values")
                                                most_common_df = pd.DataFrame(
                                                    list(stats['most_common'].items()), 
                                                    columns=['Value', 'Count']
                                                )
                                                st.dataframe(most_common_df, use_container_width=True)
                                        
                                        # Create visualizations
                                        fig = create_visualizations(df_sample, selected_column, stats)
                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Data quality insights
                                        st.subheader("🎯 Data Quality Insights")
                                        
                                        quality_issues = []
                                        if stats['null_percentage'] > 10:
                                            quality_issues.append(f"⚠️ High null percentage: {stats['null_percentage']:.1f}%")
                                        
                                        if stats['unique_percentage'] < 1 and stats['unique_count'] > 1:
                                            quality_issues.append(f"ℹ️ Low cardinality: {stats['unique_count']} unique values")
                                        
                                        if stats['unique_percentage'] > 95:
                                            quality_issues.append("ℹ️ High cardinality: Most values are unique")
                                        
                                        if quality_issues:
                                            for issue in quality_issues:
                                                st.warning(issue)
                                        else:
                                            st.success("✅ No major data quality issues detected")
                                
                                # Overall table statistics
                                st.subheader("📋 Overall Table Summary")
                                
                                # Generate summary statistics for all columns
                                summary_stats = []
                                for col in df_sample.columns:
                                    col_stats = generate_column_statistics(df_sample, col)
                                    summary_stats.append({
                                        'Column': col,
                                        'Data Type': col_stats['data_type'],
                                        'Null %': f"{col_stats['null_percentage']:.1f}%",
                                        'Unique %': f"{col_stats['unique_percentage']:.1f}%",
                                        'Unique Count': col_stats['unique_count']
                                    })
                                
                                summary_df = pd.DataFrame(summary_stats)
                                st.dataframe(summary_df, use_container_width=True)
                            
                            else:
                                st.error("❌ Could not sample data from the table")
                    else:
                        st.error("❌ Could not fetch table information")
    else:
        st.warning("⚠️ No tables found in the specified database and schema")

else:
    st.info("👈 Please configure your Snowflake connection in the sidebar to get started")
    
    # Show some example usage
    st.markdown("""
    ## 🚀 Getting Started
    
    This dashboard helps you analyze Snowflake tables with comprehensive statistics and visualizations.
    
    ### Features:
    - 📊 **Table Overview**: Row counts, column information, and data types
    - 🔍 **Column Analysis**: Detailed statistics for each column
    - 📈 **Visualizations**: Histograms, box plots, and distribution charts
    - 🎯 **Data Quality**: Identify null values, cardinality, and potential issues
    - 📋 **Summary Reports**: Quick overview of all columns
    
    ### To use this app:
    1. Enter your Snowflake connection details in the sidebar
    2. Select a table from the dropdown
    3. Click "Analyze Table" to generate comprehensive statistics
    4. Explore individual columns for detailed insights
    
    ### Requirements:
    - Valid Snowflake account and credentials
    - Appropriate permissions to read from the specified database/schema
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Snowflake | © 2024")