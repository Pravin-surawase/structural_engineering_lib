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
    private Action<string>? _writeMember;

    public OfflineReviewWindow()
    {
        Text = "StructAutomate"; Width = 760; Height = 170; MinimumSize = new Size(640, 150);
        Font = new Font("Segoe UI", 10); BackColor = Color.White; StartPosition = FormStartPosition.CenterScreen;
        _selection.Controls.Add(new Label { Text = "Member", AutoSize = true, Padding = new Padding(0, 5, 8, 0) });
        _selection.Controls.Add(_members); _selection.Controls.Add(_write);
        Controls.Add(_actions); Controls.Add(_selection); Controls.Add(_model); Controls.Add(_outcome);
        _selection.Visible = _model.Visible = _actions.Visible = false;
        _members.SelectedIndexChanged += (_, _) => PopulateActions();
        _write.Click += (_, _) => { if (_members.SelectedItem is string member) _writeMember?.Invoke(member); };
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
        _session = session; _writeMember = writeMember;
        _selection.Visible = _model.Visible = _actions.Visible = true;
        Width = 1120; Height = 500;
        _model.Text = $"{session.Snapshot.Metadata.ModelName} • {session.Snapshot.SourceIdentity.SourceSystem} {session.Snapshot.SourceIdentity.SourceVersion}\n" +
            $"Offline snapshot • {session.Snapshot.Members.Count} captured members • {session.Snapshot.ActionRows.Count} actions • mm, kN, kNm • engineering not evaluated";
        _members.Items.Clear();
        _members.Items.AddRange(session.Snapshot.Members.Select(member => member.MemberId).Cast<object>().ToArray());
        if (_members.Items.Count > 0) _members.SelectedIndex = 0;
    }

    public void ClearReview()
    {
        _session = null; _writeMember = null; _members.Items.Clear(); _actions.Rows.Clear(); _model.Text = ""; _write.Enabled = false;
        _selection.Visible = _model.Visible = _actions.Visible = false;
        Height = 170;
    }

    private void PopulateActions()
    {
        _actions.Rows.Clear(); _actions.Columns.Clear(); _write.Enabled = false;
        if (_session is null || _members.SelectedItem is not string id) return;
        foreach (var header in OfflineCommands.ActionHeaders) _actions.Columns.Add(header, header);
        foreach (var row in _session.ActionsForMember(id)) _actions.Rows.Add(OfflineCommands.ActionValues(_session, row).Cast<object>().ToArray());
        _write.Enabled = true;
    }
}
