# PyPI Release Checklist

Checklist for releasing repo-tickets v1.0.0 to PyPI.

## ✅ Pre-Release (Completed)

- [x] Create LICENSE file (MIT)
- [x] Update setup.py with correct metadata
- [x] Create pyproject.toml (modern Python packaging)
- [x] Create MANIFEST.in for documentation inclusion
- [x] Add pydantic to dependencies
- [x] Update version to 1.0.0
- [x] Update author information
- [x] Update GitHub URLs
- [x] Add comprehensive keywords
- [x] Update classifiers to Production/Stable

## 📋 Pre-Publication Steps

### 1. Install Build Tools

```bash
pip install --upgrade build twine
```

### 2. Clean Previous Builds

```bash
rm -rf build/ dist/ *.egg-info
```

### 3. Build Distribution Packages

```bash
# Build source distribution and wheel
python3 -m build
```

This creates:
- `dist/repo-tickets-1.0.0.tar.gz` (source distribution)
- `dist/repo_tickets-1.0.0-py3-none-any.whl` (wheel)

### 4. Verify Package Contents

```bash
# Check what's included
tar -tzf dist/repo-tickets-1.0.0.tar.gz | head -20

# Verify wheel
unzip -l dist/repo_tickets-1.0.0-py3-none-any.whl
```

### 5. Test Installation Locally

```bash
# Create virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from local wheel
pip install dist/repo_tickets-1.0.0-py3-none-any.whl

# Test CLI
tickets --help
tickets init

# Test import
python3 -c "import repo_tickets; print('Import successful')"

# Deactivate and cleanup
deactivate
rm -rf test_env
```

### 6. Check Package with Twine

```bash
# Check for errors and warnings
twine check dist/*
```

Should output: `Checking dist/... PASSED`

### 7. Test Upload to TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your TestPyPI API token

Then test installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ repo-tickets
```

### 8. Upload to PyPI (Production)

```bash
# Upload to production PyPI
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your PyPI API token

## 🔑 API Tokens Setup

### Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Verify email
3. Enable 2FA (required for new projects)

### Create API Token
1. Go to https://pypi.org/manage/account/token/
2. Create token with scope "Entire account" or "Project: repo-tickets"
3. Copy token (starts with `pypi-`)
4. Save securely - it won't be shown again

### (Optional) Create TestPyPI Account
1. Go to https://test.pypi.org/account/register/
2. Separate from production PyPI
3. Create API token there too

## 📦 Post-Publication Steps

### 1. Verify PyPI Page
- Visit: https://pypi.org/project/repo-tickets/
- Check description renders correctly
- Verify links work
- Check classifiers and keywords

### 2. Test Installation from PyPI

```bash
# In fresh virtual environment
python3 -m venv verify_env
source verify_env/bin/activate

# Install from PyPI
pip install repo-tickets

# Verify
tickets --version
tickets --help

deactivate
rm -rf verify_env
```

### 3. Create GitHub Release

```bash
# Tag the release
git tag -a v1.0.0 -m "Release v1.0.0 - Initial stable release"
git push origin v1.0.0
```

On GitHub:
1. Go to https://github.com/thinmanj/repo-tickets/releases
2. Click "Draft a new release"
3. Select tag v1.0.0
4. Title: "v1.0.0 - Initial Stable Release"
5. Add release notes (see below)

### 4. Update Documentation

- Add PyPI badge to README.md
- Update installation instructions
- Add link to PyPI page

## 📝 Release Notes Template

```markdown
# repo-tickets v1.0.0 - Initial Stable Release

## 🎉 First Production Release

Repo-tickets is a enterprise-grade, VCS-agnostic ticket management system optimized for agentic development workflows.

## 🚀 Key Features

- **High Performance**: 10-500x speedups through caching, indexing, and batch operations
- **AI Agent Native**: Built-in agent coordination and ML-based task assignment
- **Event-Driven**: Real-time automation with 20+ event types
- **Workflow Engine**: Multi-step orchestration with automatic progression
- **VCS Agnostic**: Works with git, mercurial, and Jujutsu
- **Comprehensive**: Epics, backlogs, requirements, BDD scenarios

## 📦 Installation

```bash
pip install repo-tickets
```

## 📚 Documentation

- [Usage Guide](USAGE_GUIDE.md)
- [Architecture](ARCHITECTURE.md)
- [Workflows](WORKFLOWS.md)
- [Agent Integration](AGENT_GUIDE.md)

## 📈 Statistics

- ~10,000 lines of production code
- ~8,800 lines of documentation
- 12 major optimization features
- 16 Python modules
- 20+ event types
- Complete test coverage

## 🙏 Acknowledgments

Built with comprehensive optimization and feature implementation across 3 phases.
```

## 🔍 Troubleshooting

### Build Fails
- Check pyproject.toml syntax
- Ensure all dependencies are available
- Check Python version compatibility

### Upload Fails
- Verify API token is correct
- Check network connection
- Ensure version number hasn't been used before

### Installation Issues
- Users may need to upgrade pip: `pip install --upgrade pip`
- Some platforms may need: `pip install --upgrade setuptools wheel`

## 📊 Success Metrics

After release, monitor:
- PyPI download statistics
- GitHub stars and forks
- Issues and pull requests
- User feedback

## 🎯 Next Steps

After v1.0.0:
- Monitor for issues
- Gather user feedback
- Plan v1.1.0 with improvements
- Consider additional platforms (Homebrew, etc.)

---

**Ready to publish?** Follow steps 1-8 above.
