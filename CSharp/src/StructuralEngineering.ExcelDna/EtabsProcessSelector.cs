using System.Drawing;
using System.Windows.Forms;

namespace StructuralEngineering.ExcelDna;

internal static class EtabsProcessSelector
{
    public static EtabsProcessChoice? Choose(IReadOnlyList<EtabsProcessChoice> choices)
    {
        using var form = new Form { Text = "Choose ETABS model", Width = 760, Height = 180, StartPosition = FormStartPosition.CenterScreen, Font = new Font("Segoe UI", 10) };
        var label = new Label { Text = "Several ETABS processes are open. Choose the one to read.", Dock = DockStyle.Top, Height = 40, Padding = new Padding(8) };
        var list = new ComboBox { Dock = DockStyle.Top, DropDownStyle = ComboBoxStyle.DropDownList };
        foreach (var choice in choices) list.Items.Add(new Choice(choice));
        list.SelectedIndex = 0;
        var buttons = new FlowLayoutPanel { Dock = DockStyle.Bottom, Height = 45, FlowDirection = FlowDirection.RightToLeft };
        var connect = new Button { Text = "Connect", AutoSize = true, DialogResult = DialogResult.OK };
        var cancel = new Button { Text = "Cancel", AutoSize = true, DialogResult = DialogResult.Cancel };
        buttons.Controls.Add(connect); buttons.Controls.Add(cancel);
        form.Controls.Add(list); form.Controls.Add(label); form.Controls.Add(buttons);
        form.AcceptButton = connect; form.CancelButton = cancel;
        return form.ShowDialog() == DialogResult.OK ? ((Choice)list.SelectedItem!).Value : null;
    }
    private sealed record Choice(EtabsProcessChoice Value)
    {
        public override string ToString() => $"{Value.WindowTitle} — process {Value.ProcessId}";
    }
}
