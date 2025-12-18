# 🔒 Governed AI Execution Engine

A sophisticated AI-powered system that enables **safe, governed, and auditable** execution of natural language queries against sensitive databases. Combines natural language processing, policy-based governance, and comprehensive audit logging to ensure compliance and data protection.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red) ![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-orange)

## 🌟 Key Features

### 🤖 Natural Language Query Processing
- **NL-to-SQL Conversion**: Transform plain English questions into optimized SQL queries
- **Multi-Agent Architecture**: Specialized agents for interpretation, governance, and risk assessment
- **LangGraph Workflow**: Orchestrated execution pipeline using state-of-the-art graph-based workflows

### 🛡️ Policy-Based Governance
- **Configurable Policies**: Define data access rules, PII restrictions, and row limits
- **Real-time Enforcement**: Automatic policy application during query execution
- **Policy Playground**: Test governance policies with "what-if" simulations before deployment

### 🔍 Sandbox Simulation
- **Query Impact Analysis**: Preview query results, accessed columns, and performance metrics
- **PII Detection**: Automatic identification of personally identifiable information
- **Risk Assessment**: Evaluate query risk scores based on data sensitivity and access patterns

### 📊 Comprehensive Audit Logging
- **Full Traceability**: Complete audit trail of all queries, decisions, and policy applications
- **Invoice Compliance**: Specialized auditing for financial transactions and vendor approvals
- **Interactive Viewer**: Web-based audit log explorer with filtering and search capabilities

### 🎨 Modern Web Interface
- **Streamlit UI**: Intuitive web interface for query composition and result visualization
- **Policy Management**: Visual policy editor and testing environment
- **Real-time Monitoring**: Live audit log streaming and compliance dashboards

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│   FastAPI Server │────│  SQLite Database│
│                 │    │                  │    │                 │
│ • Query Builder │    │ • NL Processing  │    │ • Audit Logs    │
│ • Policy Editor │    │ • Policy Engine  │    │ • Query Results │
│ • Audit Viewer  │    │ • Sandbox Sim.   │    │ • User Sessions │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   AI Agent System   │
                    │                     │
                    │ • NL Interface Agent│
                    │ • Policy Interpreter│
                    │ • Governance Agent  │
                    │ • Risk Assessment   │
                    │ • Remediation Agent │
                    └─────────────────────┘
```

### Core Components

#### 🤖 Agent System (`agents/`)
- **NaturalLanguageAgent**: Converts natural language to SQL using Groq LLM
- **PolicyInterpreterAgent**: Parses policy text into structured rules
- **GovernanceDecisionAgent**: Makes allow/deny decisions based on policies
- **RiskAssessmentAgent**: Evaluates query risk levels
- **RemediationAgent**: Suggests policy adjustments and query modifications

#### 🔄 Orchestration (`agentic/`)
- **LangGraph Workflow**: Directed acyclic graph for agent coordination
- **State Management**: Persistent state tracking across agent interactions
- **Node Execution**: Modular execution units for different processing stages

#### 🚀 API Server (`api/`)
- **RESTful Endpoints**: Comprehensive API for all system operations
- **Policy Management**: CRUD operations for governance policies
- **Simulation Engine**: Query simulation without database impact
- **Audit Integration**: Real-time logging of all operations

#### 🎨 User Interface (`ui/`)
- **Query Interface**: Natural language input with SQL preview
- **Policy Playground**: Interactive policy testing and deployment
- **Audit Dashboard**: Comprehensive log viewing and analysis

#### 🔧 Core Systems (`core/`)
- **Sandbox Manager**: Isolated query execution and analysis
- **Audit Logger**: Structured logging with JSON serialization
- **PII Classifier**: Automatic sensitive data detection

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQLite3
- Groq API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/governed-ai-execution-engine.git
   cd governed-ai-execution-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env with your Groq API key
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Initialize database**
   ```bash
   python seed.py
   ```

5. **Start the system**
   ```bash
   # Terminal 1: Start API server
   cd api && python server.py

   # Terminal 2: Start web UI
   cd ui && streamlit run app.py
   ```

6. **Access the application**
   - Web UI: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 📖 Usage Examples

### Basic Query Execution
```python
from agentic.graph import graph

# Execute natural language query
result = graph.invoke({
    "user_input": "Show me all high-risk accounts with balances over $10,000"
})

print(result["final_result"])
```

### Policy Definition
```json
{
  "max_rows": 1000,
  "deny_pii": true,
  "blocked_columns": ["ssn", "salary"],
  "allowed_tables": ["accounts", "transactions"]
}
```

### API Usage
```bash
# Natural language to SQL
curl -X POST "http://localhost:8000/nl_to_sql" \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Find all accounts with negative balances"}'

# Policy simulation
curl -X POST "http://localhost:8000/policy/what_if" \
  -H "Content-Type: application/json" \
  -d '{
    "policy": {"deny_pii": true},
    "sql": "SELECT * FROM accounts WHERE balance > 10000"
  }'
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_api_key_here

# Optional
DATABASE_PATH=./db/app.db
AUDIT_LOG_PATH=./db/audit_logs.db
API_HOST=127.0.0.1
API_PORT=8000
```

### Policy Configuration
Policies are defined in JSON format with the following structure:
```json
{
  "max_rows": 1000,           // Maximum rows per query
  "deny_pii": true,           // Block PII access
  "blocked_columns": [],      // Specific columns to block
  "allowed_tables": []        // Limit table access
}
```

## 🧪 Testing

### Run Test Suite
```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# API tests
python -m pytest tests/api/
```

### Manual Testing
1. **Query Testing**: Use the web UI to test various natural language queries
2. **Policy Testing**: Utilize the Policy Playground to test governance rules
3. **Load Testing**: Simulate multiple concurrent users
4. **Security Testing**: Attempt to bypass governance controls

## 🔒 Security & Compliance

### Data Protection
- **PII Detection**: Automatic identification and blocking of sensitive data
- **Access Control**: Granular permissions based on user roles and data sensitivity
- **Audit Trail**: Complete logging of all data access and policy decisions

### Compliance Features
- **GDPR Compliance**: Built-in mechanisms for data minimization and consent
- **SOX Compliance**: Financial data access controls and audit trails
- **Industry Standards**: SOC 2 Type II ready architecture

## 📈 Performance & Scalability

### Optimization Features
- **Query Caching**: Intelligent caching of frequently accessed data
- **Connection Pooling**: Efficient database connection management
- **Async Processing**: Non-blocking operations for high concurrency

### Monitoring
- **Performance Metrics**: Query execution times and resource usage
- **Error Tracking**: Comprehensive error logging and alerting
- **Health Checks**: Automated system health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- **Code Style**: Follow PEP 8 with Black formatting
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update docs for all new features
- **Security**: All changes must pass security review

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph**: For the powerful agent orchestration framework
- **Groq**: For ultra-fast LLM inference
- **FastAPI**: For the robust API framework
- **Streamlit**: For the beautiful web interface

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/governed-ai-execution-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/governed-ai-execution-engine/discussions)
- **Documentation**: [Wiki](https://github.com/your-org/governed-ai-execution-engine/wiki)

---

**Built with ❤️ for safe and responsible AI-driven data access**
