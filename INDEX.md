# HDL PO Receipt Tool - Documentation Index

Complete navigation guide for all project documentation and resources.

## 🚀 Getting Started

| Document | Purpose | Audience | Time Required |
|----------|---------|----------|---------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Get up and running in 5 minutes | Everyone | 5 minutes |
| **[README.md](README.md)** | Complete feature overview and introduction | Everyone | 10 minutes |

## 📖 Setup & Installation

| Document | Purpose | Audience | Time Required |
|----------|---------|----------|---------------|
| **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** | Detailed installation for all platforms | Developers, IT | 30-60 minutes |
| **[.env.example](.env.example)** | Environment configuration template | Developers, IT | 5 minutes |
| **[requirements.txt](requirements.txt)** | Python dependencies | Developers | Reference |
| **[docker-compose.yml](docker-compose.yml)** | Docker deployment config | IT, DevOps | Reference |

## 👨‍💼 Administration

| Document | Purpose | Audience | Time Required |
|----------|---------|----------|---------------|
| **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** | System administration and maintenance | System Admins | 45 minutes |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Production deployment checklist | IT, DevOps | 30 minutes |

## 📚 Technical Documentation

| Document | Purpose | Audience | Time Required |
|----------|---------|----------|---------------|
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Complete technical overview | Developers, Managers | 30 minutes |
| **Database Schema** | [database/schema.sql](database/schema.sql) | Developers, DBAs | 15 minutes |
| **API Client** | [cin7/cin7_client.py](cin7/cin7_client.py) | Developers | Reference |

## 📂 Project Structure

```
Receipt/
│
├── 📄 Documentation (Start Here!)
│   ├── INDEX.md                    ⬅️ You are here
│   ├── QUICKSTART.md               🚀 5-minute setup
│   ├── README.md                   📖 Feature overview
│   ├── SETUP_INSTRUCTIONS.md       🔧 Detailed setup
│   ├── ADMIN_GUIDE.md              👨‍💼 Administration
│   ├── DEPLOYMENT_CHECKLIST.md     ✅ Deployment guide
│   └── PROJECT_SUMMARY.md          📊 Technical overview
│
├── ⚙️ Configuration
│   ├── .env.example                📝 Environment template
│   ├── config.py                   🔧 Configuration loader
│   ├── docker-compose.yml          🐳 Docker setup
│   ├── Dockerfile                  🐳 Container definition
│   └── requirements.txt            📦 Dependencies
│
├── 🖥️ Application Code
│   ├── app.py                      🎯 Main entry point
│   ├── cin7/                       🔌 Cin7 API integration
│   ├── database/                   💾 Database layer
│   ├── services/                   🔧 Business logic
│   └── pages/                      📄 Streamlit pages
│
├── 🧪 Testing
│   ├── tests/                      ✅ Unit tests
│   └── pytest.ini                  🔧 Test configuration
│
└── 📁 Data
    └── uploads/                    📤 Uploaded dockets
```

## 🎯 Quick Links by Role

### 👤 New User
1. Start with [QUICKSTART.md](QUICKSTART.md)
2. Review [README.md](README.md)
3. Access application at http://localhost:8501

### 👨‍💻 Developer
1. Read [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
2. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. Explore code:
   - [app.py](app.py) - Main app
   - [cin7/cin7_client.py](cin7/cin7_client.py) - API client
   - [services/po_matcher.py](services/po_matcher.py) - Matching logic
4. Run tests: `pytest`

### 👨‍💼 System Administrator
1. Read [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
2. Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
3. Configure monitoring and backups
4. Set up maintenance schedule

### 🏢 Project Manager
1. Read [README.md](README.md)
2. Review [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. Check success metrics and KPIs
4. Plan user training

## 📋 Common Tasks

### Installation & Setup

| Task | Documentation | Command |
|------|---------------|---------|
| Quick Docker setup | [QUICKSTART.md](QUICKSTART.md) | `docker-compose up -d` |
| Manual installation | [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Multiple steps |
| Database setup | [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | `python database/migrate.py` |
| Configuration | [.env.example](.env.example) | Edit `.env` file |

### Operation & Maintenance

| Task | Documentation | Command |
|------|---------------|---------|
| Start application | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | `docker-compose up -d` |
| View logs | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | `docker-compose logs -f` |
| Database backup | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | `docker-compose exec -T db pg_dump ...` |
| Check status | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | `docker-compose ps` |

### Development

| Task | Documentation | Command |
|------|---------------|---------|
| Run tests | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | `pytest` |
| Code coverage | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | `pytest --cov` |
| Database migration | [database/migrate.py](database/migrate.py) | `python database/migrate.py` |

### Troubleshooting

| Issue | Documentation | Section |
|-------|---------------|---------|
| OCR not working | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | Troubleshooting → OCR |
| Cin7 API errors | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | Troubleshooting → API |
| Database issues | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | Troubleshooting → Database |
| General errors | [ADMIN_GUIDE.md](ADMIN_GUIDE.md) | Monitoring & Logs |

## 🔍 Feature Deep Dives

### PO Reference Handling
- **Overview**: [README.md](README.md#po-reference-handling)
- **Implementation**: [services/po_matcher.py](services/po_matcher.py)
- **Tests**: [tests/test_po_matcher.py](tests/test_po_matcher.py)

### OCR & Image Processing
- **Overview**: [README.md](README.md#intelligent-ocr)
- **Implementation**: [services/ocr_service.py](services/ocr_service.py) + [services/image_processor.py](services/image_processor.py)
- **Tests**: [tests/test_ocr_service.py](tests/test_ocr_service.py)

### Cin7 API Integration
- **Overview**: [README.md](README.md#cin7-api-integration)
- **Implementation**: [cin7/cin7_client.py](cin7/cin7_client.py)
- **Rate Limiting**: [cin7/rate_limiter.py](cin7/rate_limiter.py)
- **Tests**: [tests/test_cin7_client.py](tests/test_cin7_client.py)

### Database Schema
- **Overview**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#database-schema)
- **Schema**: [database/schema.sql](database/schema.sql)
- **Models**: [database/db.py](database/db.py)

## 🎓 Training Materials

### User Training Path
1. [QUICKSTART.md](QUICKSTART.md) - Basic usage (5 min)
2. [README.md](README.md) - Application flow (10 min)
3. Hands-on practice - Test docket (30 min)
4. Q&A session (15 min)

### Admin Training Path
1. [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Installation (60 min)
2. [ADMIN_GUIDE.md](ADMIN_GUIDE.md) - Administration (45 min)
3. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Deployment (30 min)
4. Hands-on practice (60 min)

### Developer Training Path
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture (30 min)
2. Code walkthrough (60 min)
3. Testing practice (30 min)
4. Contribution guidelines (15 min)

## 📊 Technical Specifications

| Specification | Document | Details |
|---------------|----------|---------|
| **Architecture** | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Tech stack, design patterns |
| **API Integration** | [cin7/cin7_client.py](cin7/cin7_client.py) | Rate limits, retry logic |
| **Database** | [database/schema.sql](database/schema.sql) | Tables, indexes, constraints |
| **Dependencies** | [requirements.txt](requirements.txt) | Python packages |
| **Deployment** | [docker-compose.yml](docker-compose.yml) | Container configuration |

## ❓ FAQ Quick Reference

### General Questions
**Q: What does this tool do?**
A: See [README.md](README.md#overview)

**Q: How do I get started?**
A: Follow [QUICKSTART.md](QUICKSTART.md)

### Technical Questions
**Q: How do backorder suffixes work?**
A: See [README.md](README.md#po-reference-handling)

**Q: What are the API rate limits?**
A: See [README.md](README.md#api-rate-limiting)

**Q: How is duplicate detection handled?**
A: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md#database-schema)

### Operational Questions
**Q: How do I deploy to production?**
A: Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

**Q: How do I backup the database?**
A: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md#backup--recovery)

**Q: Where are the logs?**
A: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md#monitoring--logs)

## 🆘 Support Resources

| Resource | Contact | Response Time |
|----------|---------|---------------|
| **User Questions** | support@hdl.com | 4 hours |
| **Technical Issues** | admin@hdl.com | 1 hour |
| **Critical Outages** | [Emergency contact] | 15 minutes |
| **Documentation** | This index | Immediate |

## 🔄 Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024 | Initial release |

## 📝 Contributing

For internal developers:
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Review code in [app.py](app.py) and subdirectories
3. Write tests for new features
4. Update documentation
5. Submit for review

## 📜 License

See [LICENSE](LICENSE) - Proprietary, internal use only

---

## 🗺️ Recommended Reading Order

### For First-Time Users
1. [INDEX.md](INDEX.md) ⬅️ You are here
2. [QUICKSTART.md](QUICKSTART.md)
3. [README.md](README.md)

### For Administrators
1. [README.md](README.md)
2. [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
3. [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
4. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### For Developers
1. [README.md](README.md)
2. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
3. [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
4. Code exploration

---

**Last Updated**: 2024
**Maintained By**: HDL IT Team
**Status**: Production Ready ✅

**Need help?** Start with the document that matches your role above, or contact support.
