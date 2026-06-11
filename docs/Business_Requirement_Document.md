# Business Requirement Document (BRD)
## Sistem Prediksi Volume Sampah Kota

---

## 1. Executive Summary

### 1.1 Ringkasan Bisnis
Sistem Prediksi Volume Sampah adalah solusi berbasis Machine Learning yang dirancang untuk memprediksi volume sampah harian, mingguan, dan bulanan di wilayah perkotaan. Sistem ini bertujuan untuk mengoptimalkan operasional pengangkutan sampah, mengurangi biaya operasional hingga 20-30%, dan meningkatkan kualitas layanan kepada masyarakat.

### 1.2 Business Case
- **Problem**: Ketidakpastian volume sampah harian menyebabkan inefisiensi armada dan biaya operasional tinggi
- **Solution**: Prediksi akurat menggunakan AI/ML untuk optimasi deployment armada
- **Expected ROI**: Payback period 6-12 bulan dengan penghematan biaya 20-30%
- **Strategic Value**: Mendukung inisiatif Smart City dan sustainability

---

## 2. Stakeholder Analysis

### 2.1 Primary Stakeholders

| Stakeholder | Role | Interest | Influence |
|-------------|------|----------|-----------|
| Kepala Dinas LH | Decision Maker | Strategic planning, budget approval | High |
| Manager Operasional | End User | Daily operations, efficiency | High |
| Operator Lapangan | End User | Work scheduling, task assignment | Medium |
| Tim IT | System Owner | System maintenance, integration | High |

### 2.2 Secondary Stakeholders

| Stakeholder | Role | Interest | Influence |
|-------------|------|----------|-----------|
| Masyarakat | Beneficiary | Service quality, clean environment | Low |
| Pemerintah Kota | Regulator | Compliance, smart city vision | Medium |
| Vendor Truk | Supplier | Contract efficiency | Low |
| Media | Observer | Public perception, reporting | Low |

---

## 3. Business Goals

### 3.1 Strategic Goals
1. **Efisiensi Operasional**: Meningkatkan efisiensi operasional pengangkutan sampah sebesar 25%
2. **Cost Reduction**: Mengurangi biaya operasional sebesar 20-30% dalam 12 bulan pertama
3. **Service Quality**: Meningkatkan on-time collection rate menjadi ≥95%
4. **Smart City**: Mendukung transformasi digital menuju smart city

### 3.2 Tactical Goals
1. Menyediakan prediksi volume sampah dengan akurasi ≥85%
2. Memberikan rekomendasi deployment armada otomatis
3. Menyediakan dashboard monitoring real-time
4. Mengintegrasikan sistem dengan platform existing

### 3.3 Operational Goals
1. Mengurangi waktu perencanaan harian dari 2 jam menjadi 15 menit
2. Mengurangi idle time armada sebesar 30%
3. Meningkatkan utilisasi armada menjadi ≥85%
4. Mengurangi komplain masyarakat sebesar 40%

---

## 4. Key Performance Indicators (KPI)

### 4.1 Technical KPIs

| KPI | Target | Measurement Method | Frequency |
|-----|--------|-------------------|-----------|
| Model Accuracy (R²) | ≥ 0.85 | Model evaluation | Monthly |
| Prediction Error (MAPE) | ≤ 10% | Actual vs Predicted | Daily |
| API Response Time | < 200ms | API monitoring | Real-time |
| System Uptime | ≥ 99% | Server monitoring | Real-time |

### 4.2 Business KPIs

| KPI | Current | Target | Timeline |
|-----|---------|--------|----------|
| Operational Cost | 100% | 70-80% | 12 months |
| Fleet Utilization | 65% | ≥ 85% | 6 months |
| On-time Collection | 78% | ≥ 95% | 6 months |
| Citizen Complaints | 50/month | ≤ 30/month | 6 months |
| Fuel Efficiency | 100% | 80% | 12 months |

### 4.3 User Adoption KPIs

| KPI | Target | Timeline |
|-----|--------|----------|
| User Training Completion | 100% | 1 month |
| Daily Active Users | ≥ 90% | 3 months |
| User Satisfaction Score | ≥ 4/5 | 6 months |
| Feature Utilization Rate | ≥ 80% | 6 months |

---

## 5. Proses Bisnis

### 5.1 Proses Bisnis Saat Ini (AS-IS)

```
1. Petugas melihat data volume kemarin secara manual
2. Estimasi volume hari ini berdasarkan pengalaman/intuisi
3. Menentukan jumlah truk yang akan dikirim (sering tidak akurat)
4. Koordinasi dengan driver secara manual (telepon/radio)
5. Truk dikirim ke lapangan
6. Monitoring manual melalui laporan telepon
7. Penyesuaian armada secara reaktif jika terjadi masalah
8. Pencatatan volume aktual di akhir hari (sering terlambat)

PAIN POINTS:
❌ Estimasi tidak akurat (error ±20-30%)
❌ Waktu perencanaan lama (2 jam/hari)
❌ Sering terjadi kelebihan atau kekurangan armada
❌ Biaya operasional tinggi
❌ Respon lambat terhadap perubahan kondisi
```

### 5.2 Proses Bisnis Dengan Sistem (TO-BE)

```
1. Sistem otomatis memprediksi volume sampah besok pagi (5 menit)
2. Sistem memberikan rekomendasi jumlah armada optimal
3. Manager approve/adjust rekomendasi melalui dashboard
4. Sistem generate schedule dan assignment otomatis
5. Notifikasi otomatis ke driver melalui sistem
6. Real-time monitoring melalui dashboard
7. Sistem otomatis adjust prediction berdasarkan data real-time
8. Automatic reporting dan analytics

IMPROVEMENTS:
✅ Prediksi akurat dengan AI/ML (error ≤10%)
✅ Perencanaan cepat (15 menit/hari)
✅ Optimasi armada berdasarkan data
✅ Penghematan biaya 20-30%
✅ Respon proaktif terhadap perubahan
```

---

## 6. Functional Requirements

### 6.1 Core Features

#### FR-01: Prediksi Volume Sampah
- **Priority**: Critical
- **Description**: Sistem harus dapat memprediksi volume sampah harian, mingguan, dan bulanan
- **Input**: Date, temperature, rainfall, humidity, holiday, weekend, population_density, event_level
- **Output**: Predicted waste volume (tons)
- **Acceptance Criteria**: 
  - Prediksi tersedia dalam < 5 detik
  - Akurasi ≥ 85% (R² ≥ 0.85)
  - MAPE ≤ 10%

#### FR-02: Rekomendasi Armada
- **Priority**: Critical
- **Description**: Sistem memberikan rekomendasi jumlah truk optimal
- **Input**: Predicted volume, truck capacity
- **Output**: Number of trucks needed, utilization rate
- **Acceptance Criteria**:
  - Rekomendasi based on configurable truck capacity
  - Utilization rate calculation accurate

#### FR-03: Dashboard Monitoring
- **Priority**: High
- **Description**: Dashboard interaktif untuk visualisasi data dan prediksi
- **Features**:
  - Real-time metrics
  - Historical trends
  - Prediction visualizations
  - Data analytics
- **Acceptance Criteria**:
  - Load time < 3 seconds
  - Responsive design
  - Interactive charts

#### FR-04: REST API
- **Priority**: High
- **Description**: REST API untuk integrasi dengan sistem lain
- **Endpoints**:
  - GET /health
  - POST /predict/daily
  - POST /predict/weekly
  - POST /predict/monthly
- **Acceptance Criteria**:
  - Response time < 200ms
  - Proper error handling
  - API documentation available

### 6.2 Supporting Features

#### FR-05: Data Management
- Import/export data historical
- Data validation
- Data backup dan recovery

#### FR-06: Reporting
- Automated daily reports
- Weekly summary reports
- Monthly analytics reports
- Custom report generation

#### FR-07: User Management
- Role-based access control
- User authentication
- Activity logging

---

## 7. Non-Functional Requirements

### 7.1 Performance
- API response time < 200ms
- Dashboard load time < 3 seconds
- Support 100 concurrent users
- Batch prediction capability

### 7.2 Scalability
- Horizontal scaling capability
- Support multi-region deployment
- Data volume up to 10 years

### 7.3 Security
- HTTPS/TLS encryption
- Authentication & authorization
- Data encryption at rest
- Audit logging
- Regular security updates

### 7.4 Reliability
- System uptime ≥ 99%
- Automated backup daily
- Disaster recovery plan
- Failover mechanism

### 7.5 Usability
- Intuitive user interface
- Indonesian language support
- Mobile-responsive design
- Minimal training required (< 2 hours)

### 7.6 Maintainability
- Modular architecture
- Comprehensive documentation
- Automated testing
- Version control

---

## 8. Constraints and Assumptions

### 8.1 Constraints
- **Budget**: Terbatas pada allocated budget
- **Timeline**: Harus go-live dalam 3 bulan
- **Resources**: Tim development terbatas
- **Data**: Data historis minimal 1 tahun required

### 8.2 Assumptions
- Data historis tersedia dan berkualitas baik
- User memiliki akses internet stabil
- Infrastructure server tersedia
- Management support penuh
- User willing to adopt new system

---

## 9. Risks and Dependencies

### 9.1 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| User resistance to change | High | Medium | Comprehensive training and change management |
| Budget overrun | High | Low | Strict project management and monitoring |
| ROI not achieved | High | Low | Phased implementation with quick wins |
| Data quality issues | Medium | Medium | Data validation and cleaning procedures |

### 9.2 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Model accuracy below target | High | Low | Multiple algorithms, rigorous testing |
| System integration issues | Medium | Medium | Thorough integration testing |
| Performance bottleneck | Medium | Low | Load testing and optimization |
| Security vulnerabilities | High | Low | Security audit and penetration testing |

### 9.3 Dependencies
- Availability of historical waste data
- Weather data from BMKG API
- Calendar and holiday data
- Server infrastructure provisioning
- Network connectivity

---

## 10. Success Criteria

### 10.1 Project Success
✅ System deployed on time (≤ 3 months)  
✅ All critical features implemented  
✅ User acceptance testing passed  
✅ Users trained and onboarded  

### 10.2 Business Success
✅ Cost reduction ≥ 20% within 12 months  
✅ Fleet utilization ≥ 85% within 6 months  
✅ On-time collection rate ≥ 95% within 6 months  
✅ User satisfaction ≥ 4/5 within 6 months  

### 10.3 Technical Success
✅ Model accuracy R² ≥ 0.85  
✅ System uptime ≥ 99%  
✅ API response time < 200ms  
✅ Zero critical bugs in production  

---

## 11. Implementation Roadmap

### Phase 1: Foundation (Month 1)
- Data collection and preparation
- Infrastructure setup
- Model development and training
- Initial testing

### Phase 2: Development (Month 2)
- Dashboard development
- API development
- Integration development
- User interface design

### Phase 3: Testing & Deployment (Month 3)
- User acceptance testing
- Performance testing
- Security testing
- Production deployment
- User training

### Phase 4: Post-Launch (Ongoing)
- Monitoring and support
- Model retraining
- Feature enhancements
- Continuous improvement

---

## 12. Budget Estimation

### 12.1 Development Cost
- Personnel: Rp 150,000,000
- Infrastructure: Rp 30,000,000
- Software licenses: Rp 20,000,000
- **Total Development**: Rp 200,000,000

### 12.2 Operational Cost (Annual)
- Server hosting: Rp 24,000,000
- Maintenance: Rp 36,000,000
- Support: Rp 24,000,000
- **Total Annual**: Rp 84,000,000

### 12.3 ROI Projection
- **Investment**: Rp 200,000,000 (Year 0)
- **Annual Savings**: Rp 240,000,000 (20% of Rp 1.2B operational cost)
- **Net Annual Benefit**: Rp 156,000,000 (after operational cost)
- **Payback Period**: 15 months
- **3-Year ROI**: 234%

---

## 13. Approval and Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Owner | [Name] | _________ | ______ |
| Project Sponsor | [Name] | _________ | ______ |
| IT Director | [Name] | _________ | ______ |
| Financial Controller | [Name] | _________ | ______ |

---

**Document Version**: 1.0  
**Last Updated**: 10 Juni 2026  
**Next Review Date**: 10 Juli 2026
