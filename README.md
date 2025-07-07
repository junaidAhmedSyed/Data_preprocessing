# ❄️ Snowflake Table Statistics Dashboard

A comprehensive Streamlit dashboard for analyzing Snowflake tables with detailed statistics, visualizations, and data quality insights.

## 🚀 Features

- **📊 Table Overview**: Display row counts, column information, and data types
- **🔍 Detailed Column Analysis**: Generate comprehensive statistics for each column
- **📈 Interactive Visualizations**: Histograms, box plots, Q-Q plots, and distribution charts
- **🎯 Data Quality Assessment**: Identify null values, cardinality issues, and potential data problems
- **📋 Summary Reports**: Quick overview of all columns with key metrics
- **🔒 Secure Connection**: Support for secure Snowflake authentication
- **📱 Responsive Design**: Modern, mobile-friendly interface

## 📦 Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Snowflake credentials** (choose one method):

   **Method 1: Using Streamlit Secrets (Recommended)**
   - Create a `.streamlit` directory in your project root
   - Copy `config_example.toml` to `.streamlit/secrets.toml`
   - Fill in your actual Snowflake credentials

   **Method 2: Environment Variables**
   ```bash
   export SNOWFLAKE_ACCOUNT="your-account-identifier"
   export SNOWFLAKE_USERNAME="your-username"
   export SNOWFLAKE_PASSWORD="your-password"
   export SNOWFLAKE_WAREHOUSE="your-warehouse"
   export SNOWFLAKE_DATABASE="your-database"
   export SNOWFLAKE_SCHEMA="your-schema"
   ```

   **Method 3: Manual Entry (Default)**
   - Enter credentials directly in the app's sidebar

## 🏃‍♂️ Usage

1. **Start the application**:
   ```bash
   streamlit run snowflake_stats_app.py
   ```

2. **Configure Connection**:
   - Enter your Snowflake connection details in the sidebar
   - Click "Connect" to establish connection

3. **Analyze Tables**:
   - Select a table from the dropdown menu
   - Adjust sample size if needed (100-5000 rows)
   - Click "Analyze Table" to generate statistics

4. **Explore Results**:
   - View table overview and column information
   - Select specific columns for detailed analysis
   - Examine visualizations and data quality insights
   - Review the overall table summary

## 📊 Statistics Generated

### Table Level
- Total row count
- Number of columns
- Column data types and properties
- Sample data preview

### Column Level
- **Basic Statistics**: Count, nulls, unique values, data type
- **Numeric Columns**: Mean, median, std dev, min/max, quartiles
- **Text Columns**: Length statistics, most common values
- **Date Columns**: Date ranges and distributions

### Data Quality
- Null value percentages
- Cardinality analysis
- Data quality warnings and insights

## 🔧 Requirements

### System Requirements
- Python 3.8+
- Internet connection for Snowflake access

### Snowflake Requirements
- Valid Snowflake account
- Read permissions on target database/schema
- Network access to Snowflake (firewall/VPN considerations)

### Dependencies
See `requirements.txt` for complete list of Python packages.

## 🛡️ Security Considerations

- **Never commit credentials to version control**
- Use `.streamlit/secrets.toml` for local development
- Use environment variables for production deployment
- Ensure your Snowflake account has appropriate security settings
- Consider using key-pair authentication for enhanced security

## 🚀 Deployment

### Local Development
```bash
streamlit run snowflake_stats_app.py
```

### Streamlit Cloud
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add secrets via the Streamlit Cloud dashboard
4. Deploy

### Docker (Optional)
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "snowflake_stats_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Common Issues

**Connection Errors**
- Verify Snowflake credentials
- Check network connectivity
- Ensure warehouse is running
- Validate account identifier format

**Performance Issues**
- Reduce sample size for large tables
- Check Snowflake warehouse size
- Monitor query execution time

**Visualization Errors**
- Ensure sufficient data in columns
- Check for unsupported data types
- Verify column contains analyzable data

### Getting Help
- Check Snowflake documentation for connection issues
- Review Streamlit logs for application errors
- Ensure all dependencies are properly installed

## 🔄 Version History

- **v1.0.0**: Initial release with comprehensive table analysis features

---

Built with ❤️ using Streamlit and Snowflake
