# StructLib Product Tour

See the supported workflow before installing anything. These screenshots are
authentic captures from StructLib v0.23.0 running locally with the bundled
ETABS sample building: 153 beams across six stories.

> [!IMPORTANT]
> This tour demonstrates software behavior and presentation. It is not a
> structural-design approval, benchmark certificate, or claim of complete
> IS 456 coverage. Review outputs independently before engineering use.

## 1. Import and verify the model

![Import preview showing 153 beams, six stories, dimensions, actions, materials, and 3D-position coverage](../images/product/import-preview.jpg)

The import preview makes the batch visible before calculations run. Confirm
member count, story assignment, dimensions, actions, material grades, and the
availability of 3D coordinates. StructLib accepts single combined CSV files,
dual geometry-and-forces CSV files, and the bundled sample.

## 2. Review the building in 3D

![Building editor showing the six-story frame and beam result table](../images/product/building-editor.jpg)

The Building Editor keeps the spatial model and engineering table together.
Filter by floor, adjust global materials, run batch design, select members, and
compare reinforcement, utilization, and status without leaving the workspace.

## 3. Inspect a member

![Selected beam with 3D reinforcement, capacity utilization, cross-section, clause checks, and export actions](../images/product/beam-inspector.jpg)

Selecting a beam opens its reinforcement view and review panel. The panel
surfaces dimensions, materials, required steel, selected bars and stirrups,
governing utilization, clause-linked checks, and BBS/DXF/report actions.

## 4. Understand the batch

![Dashboard showing pass rate, utilization, critical beams, material quantities, and story summaries](../images/product/design-dashboard.jpg)

The dashboard summarizes the current imported batch. It brings pass/fail
status, utilization, high-demand members, material quantities, story-level
results, and export actions into one view. Values shown here belong to the
bundled sample and are not a general performance claim.

## Try the same workflow

From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e Python/
cd react_app && npm install && cd ..
./run.sh dev
```

Then:

1. Open <http://localhost:5173>.
2. Choose **Explore**.
3. Select **Sample Building**.
4. Review the import preview and choose **Open Building Editor**.
5. Select a beam for member-level checks or open **Dashboard** for the batch summary.

The API documentation is available at <http://localhost:8000/docs> while the
stack is running.

## Continue exploring

- [Python quick start](python-quickstart.md)
- [React UI user flow](../guides/react-ui-user-flow.md)
- [Developer platform guide](../developers/platform-guide.md)
- [Supported evidence crosswalk](../verification/is456-library-first-evidence.md)
- [Engineering verification checklist](../legal/verification-checklist.md)

Return to the [project README](../../README.md) or the
[documentation hub](../README.md).
