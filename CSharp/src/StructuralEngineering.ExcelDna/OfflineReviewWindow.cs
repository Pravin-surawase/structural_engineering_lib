using System.Drawing;
using System.Windows.Forms;

namespace StructuralEngineering.ExcelDna;

internal sealed class OfflineReviewWindow : Form
{
    private readonly Label _outcome = new() { Dock = DockStyle.Top, Height = 76, Padding = new Padding(12), AutoEllipsis = true };
    private readonly Label _model = new() { Dock = DockStyle.Top, Height = 66, Padding = new Padding(12), AutoEllipsis = true };
    private readonly ComboBox _members = new() { DropDownStyle = ComboBoxStyle.DropDownList, Width = 350 };
    private readonly Button _write = new() { Text = "Write member review", AutoSize = true, Enabled = false };
    private readonly DataGridView _actions = new()
    {
        Dock = DockStyle.Fill,
        ReadOnly = true,
        AllowUserToAddRows = false,
        AllowUserToDeleteRows = false,
        AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.DisplayedCells,
        BackgroundColor = Color.White,
        BorderStyle = BorderStyle.None,
        RowHeadersVisible = false
    };
    private readonly FlowLayoutPanel _selection = new() { Dock = DockStyle.Top, Height = 48, Padding = new Padding(10) };
    private OfflineSnapshotSession? _session;
    private EtabsConnectionSession? _context;
    private Action<string>? _writeMember;
    private readonly Button _cancelConnection = new() { Text = "Cancel connection", Dock = DockStyle.Top, Height = 32, Visible = false };
    private Action? _cancel;

    public OfflineReviewWindow()
    {
        Text = "StructAutomate"; Width = 760; Height = 170; MinimumSize = new Size(640, 150);
        Font = new Font("Segoe UI", 10); BackColor = Color.White; StartPosition = FormStartPosition.CenterScreen;
        _selection.Controls.Add(new Label { Text = "Member", AutoSize = true, Padding = new Padding(0, 5, 8, 0) });
        _selection.Controls.Add(_members); _selection.Controls.Add(_write);
        Controls.Add(_actions); Controls.Add(_selection); Controls.Add(_model); Controls.Add(_cancelConnection); Controls.Add(_outcome);
        _selection.Visible = _model.Visible = _actions.Visible = false;
        _members.SelectedIndexChanged += (_, _) => PopulateActions();
        _write.Click += (_, _) => { if (_members.SelectedItem is string member) _writeMember?.Invoke(member); };
        _cancelConnection.Click += (_, _) => _cancel?.Invoke();
        FormClosing += (_, args) =>
        {
            if (args.CloseReason == CloseReason.UserClosing) { args.Cancel = true; Hide(); }
        };
    }

    public void SetOutcome(string workbook, string message)
    {
        Text = "StructAutomate — " + workbook;
        _outcome.Text = message;
        _outcome.BackColor = Color.FromArgb(237, 244, 249);
    }

    public void SetReview(OfflineSnapshotSession session, Action<string> writeMember)
    {
        _context = null; _session = session; _writeMember = writeMember;
        _selection.Visible = _model.Visible = _actions.Visible = true;
        Width = 1120; Height = 500;
        _model.Height = 66;
        _model.Text = $"{session.Snapshot.Metadata.ModelName} • {session.Snapshot.SourceIdentity.SourceSystem} {session.Snapshot.SourceIdentity.SourceVersion}\n" +
            $"Offline snapshot • {session.Snapshot.Members.Count} captured members • {session.Snapshot.ActionRows.Count} actions • mm, kN, kNm • engineering not evaluated";
        _members.Items.Clear();
        _members.Items.AddRange(session.Snapshot.Members.Select(member => member.MemberId).Cast<object>().ToArray());
        if (_members.Items.Count > 0) _members.SelectedIndex = 0;
    }

    public void ClearReview()
    {
        _context = null; _session = null; _writeMember = null; _members.Items.Clear(); _actions.Rows.Clear(); _model.Text = ""; _write.Enabled = false;
        _selection.Visible = _model.Visible = _actions.Visible = false;
        Height = 170;
    }

    private void PopulateActions()
    {
        _actions.Rows.Clear(); _actions.Columns.Clear(); _write.Enabled = false;
        if (_context is not null && _members.SelectedItem is string frameId)
        {
            var frame = _context.Frames[frameId];
            var point1 = _context.Points[frame.SourcePoint1Id]; var point2 = _context.Points[frame.SourcePoint2Id];
            _actions.Columns.Add("Field", "Source field"); _actions.Columns.Add("Value", "Captured value");
            void Row(string field, object value) => _actions.Rows.Add(field, value);
            Row("Frame ID", frame.SourceFrameId); Row("Type", frame.DesignOrientation); Row("Story", frame.SourceStoryId);
            Row("Section", frame.SourceSectionId); Row("Material reference", _context.Sections[frame.SourceSectionId].SourceMaterialId);
            Row("Start joint", point1.SourcePointId); Row("Start X / Y / Z (mm)", $"{point1.Xmm:G12} / {point1.Ymm:G12} / {point1.Zmm:G12}");
            Row("End joint", point2.SourcePointId); Row("End X / Y / Z (mm)", $"{point2.Xmm:G12} / {point2.Ymm:G12} / {point2.Zmm:G12}");
            Row("Frames sharing these joints", string.Join(", ", _context.Neighbours(frameId)));
            Row("Basis", "Source geometry only. Supports, physical spans, forces and engineering checks are not classified here.");
            return;
        }
        if (_session is null || _members.SelectedItem is not string id) return;
        foreach (var header in OfflineCommands.ActionHeaders) _actions.Columns.Add(header, header);
        foreach (var row in _session.ActionsForMember(id)) _actions.Rows.Add(OfflineCommands.ActionValues(_session, row).Cast<object>().ToArray());
        _write.Enabled = true;
    }

    public void SetPendingConnection(Action cancel)
    {
        _cancel = cancel; _cancelConnection.Visible = true;
        Height = Math.Max(Height, 220);
    }
    public void EndPendingConnection() { _cancel = null; _cancelConnection.Visible = false; }
    public void SetContext(EtabsConnectionSession context, string? frameId = null)
    {
        _context = context; _session = null; _writeMember = null;
        _selection.Visible = _model.Visible = _actions.Visible = true;
        Width = 1120; Height = 570; _model.Height = 105;
        var source = context.Artifact.Inventory.Source;
        _model.Text = $"ETABS {source.EtabsApiVersion} • {Path.GetFileName(source.ModelPath)} • process {source.ProcessId}\n{source.ModelPath}\n" +
            $"{context.Frames.Count} frames • {context.Points.Count} joints • source kN, m, C • coordinates displayed in mm\n" +
            $"Captured {context.Artifact.Inventory.CapturedUtc.ToLocalTime():g} • session only; reconnect after model changes • no forces loaded";
        _members.Items.Clear();
        _members.Items.AddRange(context.Frames.Keys.Order(StringComparer.Ordinal).Cast<object>().ToArray());
        if (frameId is not null && context.Frames.ContainsKey(frameId)) _members.SelectedItem = frameId;
        else if (_members.Items.Count > 0) _members.SelectedIndex = 0;
    }
}
