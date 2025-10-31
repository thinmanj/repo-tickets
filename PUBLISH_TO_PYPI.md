# Publishing to PyPI - Quick Start

## 🎉 Status: PUBLISHED!

**repo-tickets v1.0.0 is now live on PyPI!**

- **Install**: `pip install repo-tickets`
- **PyPI Page**: https://pypi.org/project/repo-tickets/
- **Release Date**: October 31, 2024
- **Git Tag**: v1.0.0

## ✅ Verify It's Live

Test the published package:

```bash
# Install from PyPI
pip install repo-tickets

# Verify it works
tickets --version
tickets --help

# Try it out
cd /tmp
mkdir test-repo && cd test-repo
git init
tickets init
tickets create "Test ticket" --priority high
tickets list
```

## 📦 Published Packages

- `repo_tickets-1.0.0-py3-none-any.whl` (103 KB) - Wheel distribution
- `repo-tickets-1.0.0.tar.gz` (194 KB) - Source distribution

Both packages **PASSED** twine validation and are now available on PyPI.

## 🚀 To Publish Now:

### Step 1: Create PyPI Account (if needed)

1. Go to https://pypi.org/account/register/
2. Verify your email
3. Enable 2FA (required)

### Step 2: Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: "repo-tickets-upload"
4. Scope: "Entire account" (or create project first and scope to project)
5. **Copy the token** (starts with `pypi-`) - you won't see it again!

### Step 3: Upload to PyPI

```bash
# Navigate to project
cd /Volumes/Projects/repo-tickets

# Upload (you'll be prompted for credentials)
python3 -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: (paste your API token, including the `pypi-` prefix)

### Step 4: Verify Publication

After upload completes:

1. Visit: https://pypi.org/project/repo-tickets/
2. Check that the page renders correctly
3. Test installation:

```bash
# In a new terminal/environment
pip install repo-tickets

# Verify it works
tickets --help
```

## 🧪 Optional: Test on TestPyPI First

If you want to test before publishing to production PyPI:

```bash
# Create TestPyPI account at https://test.pypi.org/account/register/
# Create API token at https://test.pypi.org/manage/account/token/

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ repo-tickets
```

Note: TestPyPI needs `--extra-index-url` for dependencies like click, pyyaml, etc.

## 📋 Post-Publication Checklist

After successful upload:

- [ ] Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Create GitHub release at https://github.com/thinmanj/repo-tickets/releases
- [ ] Add PyPI badge to README.md
- [ ] Announce on social media / relevant channels

## 🎯 PyPI Badge for README

Add this to README.md after publication:

```markdown
[![PyPI version](https://badge.fury.io/py/repo-tickets.svg)](https://badge.fury.io/py/repo-tickets)
[![Downloads](https://pepy.tech/badge/repo-tickets)](https://pepy.tech/project/repo-tickets)
```

## 📊 What Gets Published

The package includes:

### Python Code
- All `repo_tickets/*.py` modules (16 files)
- Command-line interface (`tickets` command)

### Documentation
- README.md
- LICENSE (MIT)
- All *.md documentation files (~8,800 lines)
- USAGE_GUIDE.md, ARCHITECTURE.md, WORKFLOWS.md
- Agent guides, requirements docs, etc.

### Examples
- All files in `examples/` directory

### Configuration
- requirements.txt
- pyproject.toml

## 🔧 Troubleshooting

### "Invalid credentials"
- Make sure username is exactly `__token__` (with underscores)
- Make sure you're pasting the full API token including `pypi-` prefix
- Check there are no extra spaces before/after the token

### "Filename already exists"
- Version 1.0.0 has already been uploaded
- You cannot replace an existing version
- Bump version in `pyproject.toml` and `setup.py`, rebuild, and upload

### "Invalid package"
- Run `python3 -m twine check dist/*` to see specific errors
- Check that README.md is valid Markdown
- Ensure all required metadata is present

## 📝 Version Updates

For future releases:

1. Update version in both:
   - `pyproject.toml` line 7
   - `setup.py` line 16

2. Rebuild:
   ```bash
   rm -rf dist/ build/
   python3 -m build
   python3 -m twine check dist/*
   ```

3. Upload:
   ```bash
   python3 -m twine upload dist/*
   ```

## 🎉 Success!

Once published, your package will be available via:

```bash
pip install repo-tickets
```

And visible at: https://pypi.org/project/repo-tickets/

---

**Questions?** See [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for detailed information.
