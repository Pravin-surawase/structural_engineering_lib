# Documentation Images

This folder contains images referenced by the documentation, including verified
product captures and architecture diagrams.

**Updated:** 2026-08-10

---

## 📷 Image Categories

| Category | Naming Pattern | Example |
|----------|----------------|---------|
| Excel tutorial | `excel-tutorial-NN-*.png` | `excel-tutorial-01-addin-install.png` |
| Architecture | `arch-*.png` | `arch-layer-diagram.png` |
| Workflow | `workflow-*.png` | `workflow-design-process.png` |
| Screenshots | `screenshot-*.png` | `screenshot-output-example.png` |
| Product tour | `product/*.jpg` | `product/beam-inspector.jpg` |
| Social preview | `social-preview.jpg` | GitHub repository link preview |

---

## 🔧 Adding New Images

1. Use descriptive, lowercase filenames with hyphens
2. Follow the naming pattern for the category
3. Reference in markdown using relative paths:
   ```markdown
   ![Description](../images/your-image.png)
   ```

---

## 📋 Excel Tutorial Screenshots

The file [screenshot-guide.md](../_internal/screenshot-guide.md) lists target screenshot filenames for Excel tutorials.

| Screenshot | Description |
|------------|-------------|
| `excel-tutorial-01-addin-install.png` | Add-in installation dialog |
| `excel-tutorial-02-ribbon-tab.png` | Structural Engineering ribbon tab |
| `excel-tutorial-03-input-form.png` | Beam input form |

---

## 🌐 GitHub Social Preview

`social-preview.jpg` is the 1280×640 repository card uploaded through
**Settings → General → Social preview** on GitHub. It combines the verified
beam-inspector and design-dashboard captures listed in
[product/README.md](product/README.md); it is not used in place of the larger
README screenshots.

Refresh the uploaded GitHub preview whenever this file changes so link shares
and the versioned repository asset remain aligned.

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [Screenshot Guide](../_internal/screenshot-guide.md) | Full screenshot requirements |
| [Product Screenshots](product/README.md) | Verified public product captures |
| [Product Tour](../getting-started/product-tour.md) | Visitor-facing application walkthrough |

---

**Parent:** [docs/README.md](../README.md)
