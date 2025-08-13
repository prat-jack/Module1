# Customer Analytics Dashboard - Production Deployment Guide

## 🚀 Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account (https://share.streamlit.io/)
- Application code pushed to a GitHub repository

### Quick Deployment Steps

1. **Connect GitHub Repository**
   - Visit https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub account
   - Select repository: `your-username/customer-analytics-dashboard`
   - Choose branch: `main`
   - Main file path: `app.py`

2. **Environment Configuration**
   Set these environment variables in Streamlit Cloud:
   ```
   ENVIRONMENT=production
   DEBUG=False
   ENABLE_AUTH=True
   SECRET_KEY=your-production-secret-key-here
   ANONYMIZE_DATA=True
   ENABLE_TELEMETRY=True
   LOG_LEVEL=INFO
   MAX_FILE_SIZE_MB=200
   MAX_RECORDS=100000
   ```

3. **Deploy**
   - Click "Deploy!"
   - Wait for deployment to complete
   - Your app will be available at: `https://share.streamlit.io/your-username/customer-analytics-dashboard/main/app.py`

## 🔐 Security Configuration

### Production Security Checklist

- [ ] **Secret Key**: Generate and set a secure `SECRET_KEY`
- [ ] **Authentication**: Enable user authentication (`ENABLE_AUTH=True`)
- [ ] **Data Privacy**: Enable data anonymization (`ANONYMIZE_DATA=True`)
- [ ] **File Uploads**: Validate file types and sizes
- [ ] **Session Management**: Configure session timeout
- [ ] **HTTPS**: Ensure HTTPS is enabled (automatic with Streamlit Cloud)
- [ ] **Error Handling**: Disable debug mode (`DEBUG=False`)

### Generate Secure Secret Key
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")
```

### Default User Accounts
**⚠️ IMPORTANT: Change these credentials immediately in production!**

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| analyst | analyst123 | Analyst |

To add/modify users, update the `authenticate_user` function in `auth.py`.

## 📊 Performance Optimization

### Memory Management
- **Data Chunking**: Large datasets are processed in chunks
- **Memory Monitoring**: Real-time memory usage tracking
- **Garbage Collection**: Automatic cleanup after analysis
- **Record Limits**: Configurable maximum record limits

### Caching Strategy
- **Streamlit Caching**: Enabled for repeated operations
- **TTL Configuration**: 1-hour cache timeout (configurable)
- **Memory Threshold**: Automatic warnings for high usage

### Resource Limits
```
MAX_FILE_SIZE_MB=200      # Maximum upload size
MAX_RECORDS=100000        # Maximum records to process
MAX_MEMORY_USAGE_MB=1000  # Memory usage threshold
CHUNK_SIZE=10000          # Data processing chunk size
```

## 🗂️ File Structure for Deployment

```
customer-analytics-dashboard/
├── app.py                      # Main application
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── modules/
│   ├── __init__.py
│   ├── data_processor.py
│   ├── customer_analytics.py
│   ├── sales_analytics.py
│   └── geographic_analytics.py
├── config.py                   # Application configuration
├── utils.py                    # Utility functions
├── auth.py                     # Authentication system
├── brand_config.py            # Brand customization
├── .env.example               # Environment variables template
└── DEPLOYMENT.md              # This file
```

## 🔍 Monitoring and Logging

### Production Logging
- **Log Level**: INFO (configurable)
- **Log Format**: Structured logging with timestamps
- **Error Tracking**: Comprehensive error handling
- **Performance Metrics**: Operation timing and memory usage

### Health Monitoring
The application includes built-in health checks:
- Memory usage monitoring
- Configuration validation
- System resource checks

### Error Reporting
Configure Sentry for advanced error tracking:
```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## 🔧 Environment Variables Reference

### Core Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Application environment |
| `DEBUG` | False | Enable debug mode |
| `PORT` | 8501 | Server port |
| `HOST` | 0.0.0.0 | Server host |

### Security
| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_AUTH` | False | Enable authentication |
| `SECRET_KEY` | - | Session encryption key |
| `SESSION_TIMEOUT` | 3600 | Session timeout (seconds) |

### Performance
| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RECORDS` | 100000 | Maximum records to process |
| `MAX_FILE_SIZE_MB` | 200 | Maximum upload size (MB) |
| `MAX_MEMORY_USAGE_MB` | 1000 | Memory usage threshold |
| `CACHE_TTL` | 3600 | Cache timeout (seconds) |

### Privacy
| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMIZE_DATA` | False | Enable data anonymization |
| `DATA_RETENTION_DAYS` | 90 | Data retention period |
| `ENABLE_DATA_ENCRYPTION` | False | Enable data encryption |

### Monitoring
| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging level |
| `ENABLE_FILE_LOGGING` | True | Enable file logging |
| `ENABLE_TELEMETRY` | False | Enable telemetry |
| `SENTRY_DSN` | - | Sentry error tracking |

## 🐛 Troubleshooting

### Common Issues

1. **Memory Errors**
   - Reduce `MAX_RECORDS`
   - Increase `MAX_MEMORY_USAGE_MB`
   - Use smaller datasets

2. **Authentication Issues**
   - Verify `SECRET_KEY` is set
   - Check user credentials
   - Ensure `ENABLE_AUTH=True`

3. **File Upload Issues**
   - Check file size limits
   - Verify file format (CSV only)
   - Ensure required columns are present

4. **Performance Issues**
   - Enable caching
   - Reduce data processing chunk size
   - Monitor memory usage

### Debug Mode
Enable debug mode for development:
```
DEBUG=True
LOG_LEVEL=DEBUG
```

## 🔄 Data Backup and Recovery

### Data Privacy Considerations
- **No Persistent Storage**: Data is processed in memory only
- **Session-Based**: Data exists only during user session
- **Automatic Cleanup**: Memory cleared after analysis
- **Privacy Compliance**: Optional data anonymization

### Backup Recommendations
- **Export Features**: Built-in data export functionality
- **User Responsibility**: Users should backup their source data
- **Audit Trails**: Access logging for compliance

## 🚦 Production Checklist

### Pre-Deployment
- [ ] All environment variables configured
- [ ] Secret key generated and set
- [ ] Authentication credentials updated
- [ ] Debug mode disabled
- [ ] Logging configured
- [ ] Performance limits set

### Post-Deployment
- [ ] Application accessible via HTTPS
- [ ] Authentication working
- [ ] File uploads functional
- [ ] Memory monitoring active
- [ ] Error handling tested
- [ ] Performance metrics reviewed

### Security Audit
- [ ] No sensitive data in logs
- [ ] Secure file upload validation
- [ ] Session management working
- [ ] Data anonymization active
- [ ] Error messages sanitized

## 📞 Support and Maintenance

### Monitoring
- Monitor application logs
- Track memory usage patterns
- Review user access patterns
- Monitor error rates

### Updates
- Regular dependency updates
- Security patch management
- Performance optimization
- Feature enhancements

### Scaling Considerations
- **Vertical Scaling**: Increase memory/CPU limits
- **Horizontal Scaling**: Deploy multiple instances
- **Database Integration**: For larger datasets
- **Caching Solutions**: Redis for improved performance

---

## 🎯 Quick Start Commands

### Local Development
```bash
# Set up environment
cp .env.example .env
# Edit .env with your settings

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Production Deployment
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables
4. Deploy

Your Customer Analytics Dashboard is now ready for production! 🚀

For additional support, refer to the [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-cloud) or create an issue in the project repository.