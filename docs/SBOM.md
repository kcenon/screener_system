# Software Bill of Materials (SBOM)

This document describes the SBOM generation process for the Stock Screening Platform.

## Overview

The Stock Screening Platform generates Software Bill of Materials (SBOM) in CycloneDX v1.5 format for all components. SBOMs are automatically generated during releases and can be manually generated at any time.

## What is SBOM?

A Software Bill of Materials (SBOM) is a formal record containing the details and supply chain relationships of various components used in building software. It provides:

- **Transparency**: Complete visibility into software dependencies
- **Security**: Rapid vulnerability identification and impact assessment
- **Compliance**: Meets regulatory requirements (US EO 14028, EU CRA)
- **Risk Management**: Supply chain risk assessment and mitigation

## Generated SBOMs

| Component | File | Description |
|-----------|------|-------------|
| Frontend | `sbom-frontend.json` | npm/Node.js dependencies |
| Backend | `sbom-backend.json` | Python dependencies |
| Data Pipeline | `sbom-datapipeline.json` | Airflow/Python dependencies |
| **Complete** | `sbom-complete.json` | Merged SBOM with all components |

## SBOM Format

All SBOMs are generated in [CycloneDX](https://cyclonedx.org/) v1.5 JSON format, which includes:

- **Component Information**: Name, version, type, purl (package URL)
- **License Information**: SPDX license identifiers
- **Hash Values**: SHA-256 checksums for integrity verification
- **Dependency Graph**: Relationships between components

### Example Component Entry

```json
{
  "type": "library",
  "name": "react",
  "version": "18.2.0",
  "purl": "pkg:npm/react@18.2.0",
  "licenses": [
    {
      "license": {
        "id": "MIT"
      }
    }
  ],
  "hashes": [
    {
      "alg": "SHA-256",
      "content": "abc123..."
    }
  ]
}
```

## Generating SBOMs

### Local Generation

Generate SBOMs locally using the provided scripts:

```bash
# Generate all SBOMs
./scripts/generate-sbom.sh

# Generate specific component
./scripts/sbom/generate-frontend.sh
./scripts/sbom/generate-backend.sh
./scripts/sbom/generate-pipeline.sh

# Custom output directory
OUTPUT_DIR=./dist/sbom ./scripts/generate-sbom.sh

# Skip specific components
./scripts/generate-sbom.sh --skip-pipeline --skip-merge
```

### CI/CD Generation

SBOMs are automatically generated:

1. **On Release**: When a new GitHub release is published
2. **Manual Trigger**: Via GitHub Actions workflow dispatch

Generated SBOMs are attached to GitHub releases as artifacts.

### Manual Workflow Trigger

```bash
# Trigger SBOM generation via GitHub CLI
gh workflow run sbom.yml

# With release attachment
gh workflow run sbom.yml -f attach_to_release=true
```

## Accessing SBOMs

### From GitHub Releases

1. Go to [Releases](https://github.com/kcenon/screener_system/releases)
2. Find the desired release
3. Download SBOM files from the release assets

### From GitHub Actions

1. Go to [Actions](https://github.com/kcenon/screener_system/actions)
2. Find the "Generate SBOM" workflow run
3. Download artifacts from the workflow summary

## Vulnerability Scanning

SBOMs can be scanned for known vulnerabilities using tools like [Grype](https://github.com/anchore/grype):

```bash
# Install grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s

# Scan SBOM
grype sbom:sbom-complete.json

# Output formats
grype sbom:sbom-complete.json -o table
grype sbom:sbom-complete.json -o json > vulnerabilities.json
grype sbom:sbom-complete.json -o sarif > vulnerabilities.sarif
```

## Tools Used

| Tool | Purpose | Component |
|------|---------|-----------|
| [@cyclonedx/cyclonedx-npm](https://github.com/CycloneDX/cyclonedx-node-npm) | npm SBOM generation | Frontend |
| [cyclonedx-py](https://github.com/CycloneDX/cyclonedx-python) | Python SBOM generation | Backend, Data Pipeline |
| [Grype](https://github.com/anchore/grype) | Vulnerability scanning | All |

## Compliance

This SBOM implementation supports compliance with:

- **US Executive Order 14028**: Improving the Nation's Cybersecurity
- **NTIA SBOM Minimum Elements**: All required fields included
- **EU Cyber Resilience Act**: Software transparency requirements
- **PCI DSS 4.0**: Software inventory management

### NTIA Minimum Elements Checklist

| Element | Status | Notes |
|---------|--------|-------|
| Supplier Name | ✅ | Included in component metadata |
| Component Name | ✅ | Package name |
| Component Version | ✅ | Package version |
| Unique Identifier | ✅ | Package URL (purl) |
| Dependency Relationship | ✅ | Dependency graph included |
| Author of SBOM Data | ✅ | Tool metadata |
| Timestamp | ✅ | Generation timestamp |

## Best Practices

### For Development Teams

1. **Generate Before Release**: Always generate fresh SBOMs before releases
2. **Review Vulnerabilities**: Scan SBOMs and address critical issues
3. **Keep Dependencies Updated**: Regular dependency updates reduce vulnerabilities
4. **Verify Integrity**: Use hash values to verify component integrity

### For Security Teams

1. **Monitor Releases**: Review SBOMs with each release
2. **Automate Scanning**: Integrate vulnerability scanning in CI/CD
3. **Track Changes**: Compare SBOMs between versions
4. **Alert on Critical**: Set up alerts for critical vulnerabilities

### For Customers

1. **Request SBOM**: Available as release assets
2. **Verify Format**: CycloneDX v1.5 JSON format
3. **Scan Independently**: Use your own scanning tools
4. **Report Issues**: Contact us for security concerns

## Troubleshooting

### Common Issues

#### SBOM generation fails

```bash
# Ensure dependencies are installed
cd frontend && npm ci
cd ../backend && pip install -r requirements.txt

# Check tool versions
npx @cyclonedx/cyclonedx-npm --version
python -m cyclonedx_py --version
```

#### Empty or incomplete SBOM

```bash
# Verify lock files exist
ls frontend/package-lock.json
ls backend/requirements.txt

# Regenerate lock files if needed
cd frontend && npm install
cd ../backend && pip freeze > requirements.txt
```

#### Merge fails

```bash
# Ensure jq is installed
brew install jq  # macOS
apt install jq   # Linux

# Or install cyclonedx-cli for better merging
# https://github.com/CycloneDX/cyclonedx-cli
```

## References

- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [NTIA SBOM Resources](https://www.ntia.gov/page/software-bill-materials)
- [US Executive Order 14028](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)
- [OWASP Dependency-Track](https://owasp.org/www-project-dependency-track/)
- [Grype Documentation](https://github.com/anchore/grype)

## Support

For questions or issues related to SBOM:

1. Open an issue with the `security` label
2. Contact the security team
3. Review existing documentation

---

**Last Updated**: 2025-11-27
**Version**: 1.0.0
**Maintained By**: Development Team
