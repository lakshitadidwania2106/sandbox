# Bifrost Security Plugin Test Suite - Complete Index

## 📚 Documentation Files

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - 5-minute quick start guide for beginners
  - Prerequisites check
  - Step-by-step setup
  - First test run
  - Troubleshooting basics

### Main Documentation
- **[README.md](README.md)** - Complete documentation (main reference)
  - Full setup instructions
  - Detailed test scenarios
  - Comprehensive troubleshooting
  - Configuration guide
  - Production deployment tips

### Quick References
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheatsheet
  - One-line commands
  - Quick test examples
  - Log locations
  - Common issues
  - Environment variables

### Architecture & Design
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture diagrams
  - Component interactions
  - Request flow diagrams
  - Data structures
  - Security layers
  - Performance characteristics

### Test Suite Details
- **[TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md)** - Comprehensive test overview
  - What the suite tests
  - Security features validated
  - Test result interpretation
  - CI/CD integration
  - Extending the suite

## 🔧 Configuration Files

### Main Configuration
- **[config.json](config.json)** - Bifrost configuration with security plugin
  - Server settings
  - Provider configuration (OpenAI)
  - Security plugin settings
  - PII detection config
  - Tool validation config

### Docker Configuration
- **[docker-compose.yml](docker-compose.yml)** - Presidio services
  - Presidio Analyzer (port 5000)
  - Presidio Anonymizer (port 5001)
  - Health checks
  - Network configuration

### Environment Configuration
- **[.env.example](.env.example)** - Environment variable template
  - OpenAI API key
  - Lakera API key (optional)
  - Service URLs

## 📜 Policy Files

### OPA Policies (Rego)
- **[policies/request_validation.rego](policies/request_validation.rego)** - Request validation policy
  - Threat score validation
  - PII detection rules
  - Provider restrictions
  - Model access control
  - Time-based access

- **[policies/tool_validation.rego](policies/tool_validation.rego)** - Tool execution policy
  - Safe tool whitelist
  - Dangerous tool blacklist
  - Command injection prevention
  - Path traversal protection
  - Role-based access control

## 🧪 Test Files

### Test Scripts
- **[test-security.sh](test-security.sh)** - Main test script (10 tests)
  - Test 1: Normal request
  - Test 2: PII detection (email)
  - Test 3: PII blocking (SSN)
  - Test 4: Multiple PII entities
  - Test 5: Prompt injection
  - Test 6: Allowed tool call
  - Test 7: Denied tool call
  - Test 8: Dangerous command
  - Test 9: Path traversal
  - Test 10: Unapproved provider

### Sample Input Files
- **[sample-inputs/](sample-inputs/)** - JSON files for manual OPA testing
  - [normal-request.json](sample-inputs/normal-request.json) - Clean request
  - [pii-request.json](sample-inputs/pii-request.json) - Request with PII
  - [injection-request.json](sample-inputs/injection-request.json) - Injection attempt
  - [allowed-tool.json](sample-inputs/allowed-tool.json) - Safe tool call
  - [denied-tool.json](sample-inputs/denied-tool.json) - Dangerous tool
  - [path-traversal-tool.json](sample-inputs/path-traversal-tool.json) - Path traversal
  - [README.md](sample-inputs/README.md) - How to use sample inputs

## 🚀 Utility Scripts

### Setup & Management
- **[start-test-environment.sh](start-test-environment.sh)** - Complete environment setup
  - Prerequisites check
  - Start Presidio
  - Test Presidio
  - Build Bifrost
  - Setup logs

- **[cleanup.sh](cleanup.sh)** - Cleanup script
  - Stop Bifrost
  - Stop Presidio
  - Clean logs
  - Remove Docker volumes

## 📁 Directory Structure

```
bifrost/tests/security-plugin-test/
│
├── Documentation/
│   ├── INDEX.md                    ← You are here
│   ├── GETTING_STARTED.md          ← Start here if new
│   ├── README.md                   ← Main documentation
│   ├── QUICK_REFERENCE.md          ← Command cheatsheet
│   ├── ARCHITECTURE.md             ← System design
│   └── TEST_SUITE_OVERVIEW.md      ← Test details
│
├── Configuration/
│   ├── config.json                 ← Bifrost config
│   ├── docker-compose.yml          ← Presidio services
│   ├── .env.example                ← Environment template
│   └── .gitignore                  ← Git ignore rules
│
├── Policies/
│   ├── request_validation.rego     ← Request policy
│   └── tool_validation.rego        ← Tool policy
│
├── Tests/
│   ├── test-security.sh            ← Main test script
│   └── sample-inputs/              ← Test data
│       ├── README.md
│       ├── normal-request.json
│       ├── pii-request.json
│       ├── injection-request.json
│       ├── allowed-tool.json
│       ├── denied-tool.json
│       └── path-traversal-tool.json
│
├── Scripts/
│   ├── start-test-environment.sh   ← Setup script
│   └── cleanup.sh                  ← Cleanup script
│
└── Logs/ (generated)
    ├── bifrost.log                 ← Bifrost logs
    └── security-audit.log          ← Security events
```

## 🎯 Quick Navigation

### I want to...

**Get started quickly**
→ [GETTING_STARTED.md](GETTING_STARTED.md)

**Understand the architecture**
→ [ARCHITECTURE.md](ARCHITECTURE.md)

**Run the tests**
→ [test-security.sh](test-security.sh) or [README.md](README.md)

**Find a specific command**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Customize policies**
→ [policies/](policies/) and [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md)

**Test policies manually**
→ [sample-inputs/README.md](sample-inputs/README.md)

**Troubleshoot issues**
→ [README.md#troubleshooting](README.md#troubleshooting)

**Deploy to production**
→ [TEST_SUITE_OVERVIEW.md#production-deployment](TEST_SUITE_OVERVIEW.md)

**Extend the test suite**
→ [TEST_SUITE_OVERVIEW.md#extending-the-test-suite](TEST_SUITE_OVERVIEW.md)

**Integrate with CI/CD**
→ [TEST_SUITE_OVERVIEW.md#integration-with-cicd](TEST_SUITE_OVERVIEW.md)

## 📊 Test Coverage

| Security Feature | Tests | Files |
|-----------------|-------|-------|
| PII Detection | 3 tests | test-security.sh, pii-request.json |
| Prompt Injection | 1 test | test-security.sh, injection-request.json |
| Tool Validation | 4 tests | test-security.sh, *-tool.json |
| Policy Enforcement | 2 tests | test-security.sh, request_validation.rego |
| **Total** | **10 tests** | **Multiple files** |

## 🔐 Security Features

| Feature | Config Key | Policy File | Test |
|---------|-----------|-------------|------|
| PII Detection | `enable_pii_detection` | request_validation.rego | 2-4 |
| Prompt Injection | `enable_prompt_injection` | request_validation.rego | 5 |
| Tool Validation | `enable_tool_validation` | tool_validation.rego | 6-9 |
| Policy Enforcement | `enable_policy_enforcement` | Both | All |

## 🛠️ Common Tasks

### Setup
```bash
./start-test-environment.sh
```

### Run Tests
```bash
./test-security.sh
```

### View Logs
```bash
tail -f logs/bifrost.log
tail -f logs/security-audit.log
```

### Cleanup
```bash
./cleanup.sh
```

### Test Policies
```bash
cd sample-inputs
opa eval -d ../policies/request_validation.rego \
  -i normal-request.json \
  "data.bifrost.security.allow"
```

## 📖 Reading Order

### For Beginners
1. [GETTING_STARTED.md](GETTING_STARTED.md) - Quick start
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Commands
3. [README.md](README.md) - Full docs

### For Developers
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
2. [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md) - Test details
3. [policies/](policies/) - Policy code
4. [README.md](README.md) - Full reference

### For Security Engineers
1. [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md) - Security features
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Security layers
3. [policies/](policies/) - Policy implementation
4. [README.md#security-best-practices](README.md) - Best practices

### For DevOps
1. [GETTING_STARTED.md](GETTING_STARTED.md) - Quick setup
2. [docker-compose.yml](docker-compose.yml) - Services
3. [TEST_SUITE_OVERVIEW.md#integration-with-cicd](TEST_SUITE_OVERVIEW.md) - CI/CD
4. [README.md#troubleshooting](README.md) - Operations

## 🔗 External Resources

- [Bifrost Documentation](../../docs/)
- [Security Plugin Source](../../plugins/security/)
- [OPA Documentation](https://www.openpolicyagent.org/docs/)
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- [Lakera Guard](https://lakera.ai/)

## 📝 File Sizes

| File | Lines | Purpose |
|------|-------|---------|
| README.md | ~800 | Main documentation |
| test-security.sh | ~500 | Test script |
| ARCHITECTURE.md | ~600 | Architecture diagrams |
| TEST_SUITE_OVERVIEW.md | ~700 | Test overview |
| GETTING_STARTED.md | ~300 | Quick start |
| QUICK_REFERENCE.md | ~400 | Command reference |
| request_validation.rego | ~200 | Request policy |
| tool_validation.rego | ~300 | Tool policy |

## 🎓 Learning Path

### Level 1: Basic Usage
- [ ] Read [GETTING_STARTED.md](GETTING_STARTED.md)
- [ ] Run `./start-test-environment.sh`
- [ ] Run `./test-security.sh`
- [ ] View logs

### Level 2: Understanding
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Read [TEST_SUITE_OVERVIEW.md](TEST_SUITE_OVERVIEW.md)
- [ ] Review policy files
- [ ] Test policies manually

### Level 3: Customization
- [ ] Modify policies
- [ ] Add new tests
- [ ] Customize configuration
- [ ] Integrate with CI/CD

### Level 4: Production
- [ ] Review security best practices
- [ ] Set up monitoring
- [ ] Configure audit logging
- [ ] Deploy to production

## 🆘 Getting Help

1. **Check documentation** - Start with [README.md](README.md)
2. **Review troubleshooting** - See [README.md#troubleshooting](README.md)
3. **Check logs** - `tail -f logs/*.log`
4. **Test components** - Use sample inputs
5. **Open issue** - GitHub issues
6. **Contact team** - Bifrost support

## 📅 Maintenance

### Regular Tasks
- Update policies as threats evolve
- Review audit logs weekly
- Update dependencies monthly
- Test new security features
- Review and update documentation

### Version History
- v1.0.0 (2025-01-01) - Initial release
  - 10 test scenarios
  - Complete documentation
  - Sample inputs
  - Setup scripts

---

**Last Updated:** 2025-01-01
**Version:** 1.0.0
**Maintainer:** Bifrost Security Team
**License:** Same as Bifrost project
