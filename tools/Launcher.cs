using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace JStarsLauncher
{
    public class LauncherForm : Form
    {
        // P/Invoke XInput to detect Xbox Controllers
        [DllImport("xinput1_4.dll", EntryPoint = "XInputGetState")]
        private static extern int XInputGetState14(int dwUserIndex, ref XINPUT_STATE pState);

        [DllImport("xinput9_1_0.dll", EntryPoint = "XInputGetState")]
        private static extern int XInputGetState91(int dwUserIndex, ref XINPUT_STATE pState);

        [StructLayout(LayoutKind.Sequential)]
        private struct XINPUT_STATE
        {
            public uint dwPacketNumber;
            public XINPUT_GAMEPAD Gamepad;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct XINPUT_GAMEPAD
        {
            public ushort wButtons;
            public byte bLeftTrigger;
            public byte bRightTrigger;
            public short sThumbLX;
            public short sThumbLY;
            public short sThumbRX;
            public short sThumbRY;
        }

        private static bool IsControllerConnected()
        {
            try
            {
                XINPUT_STATE state = new XINPUT_STATE();
                if (XInputGetState14(0, ref state) == 0) return true;
            }
            catch
            {
                try
                {
                    XINPUT_STATE state = new XINPUT_STATE();
                    if (XInputGetState91(0, ref state) == 0) return true;
                }
                catch { }
            }
            return false;
        }

        // UI Controls
        private ComboBox comboFps;
        private ComboBox comboRes;
        private CheckBox checkFullscreen;
        private CheckBox checkFsr;
        private Label lblControllerStatus;
        private Button btnPlay;
        private Button btnSaves;
        private Timer timerController;

        // Colors
        private readonly Color bgDark = Color.FromArgb(20, 22, 32);
        private readonly Color bgCard = Color.FromArgb(30, 33, 48);
        private readonly Color accentOrange = Color.FromArgb(245, 124, 0);
        private readonly Color accentHover = Color.FromArgb(255, 152, 0);
        private readonly Color textWhite = Color.FromArgb(240, 240, 245);
        private readonly Color textMuted = Color.FromArgb(160, 165, 185);
        private readonly Color greenConnected = Color.FromArgb(46, 204, 113);
        private readonly Color amberDisconnected = Color.FromArgb(241, 196, 15);

        public LauncherForm()
        {
            InitializeComponent();
            LoadConfig();
            UpdateControllerStatus();

            timerController = new Timer();
            timerController.Interval = 1500;
            timerController.Tick += (s, e) => UpdateControllerStatus();
            timerController.Start();
        }

        private void InitializeComponent()
        {
            this.Text = "J-Stars Victory VS+ | Native PC Launcher";
            this.Size = new Size(540, 620);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.BackColor = bgDark;
            this.ForeColor = textWhite;

            // Header Banner Panel
            Panel headerPanel = new Panel();
            headerPanel.Dock = DockStyle.Top;
            headerPanel.Height = 110;
            headerPanel.BackColor = Color.FromArgb(25, 27, 40);
            headerPanel.Paint += (s, e) =>
            {
                using (LinearGradientBrush brush = new LinearGradientBrush(
                    new Rectangle(0, 0, headerPanel.Width, headerPanel.Height),
                    Color.FromArgb(230, 81, 0), Color.FromArgb(25, 27, 40), 90F))
                {
                    e.Graphics.FillRectangle(brush, 0, 0, headerPanel.Width, 6);
                }
            };

            Label titleLabel = new Label();
            titleLabel.Text = "J-STARS VICTORY VS+";
            titleLabel.Font = new Font("Segoe UI", 18, FontStyle.Bold);
            titleLabel.ForeColor = Color.FromArgb(255, 179, 0);
            titleLabel.AutoSize = true;
            titleLabel.Location = new Point(25, 22);

            Label subTitleLabel = new Label();
            subTitleLabel.Text = "PS4 Native PC Translation Wrapper (shadPS4 Vulkan Core)";
            subTitleLabel.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
            subTitleLabel.ForeColor = textMuted;
            subTitleLabel.AutoSize = true;
            subTitleLabel.Location = new Point(27, 60);

            headerPanel.Controls.Add(titleLabel);
            headerPanel.Controls.Add(subTitleLabel);

            // Settings Card Panel
            Panel cardSettings = new Panel();
            cardSettings.Location = new Point(25, 125);
            cardSettings.Size = new Size(475, 340);
            cardSettings.BackColor = bgCard;
            cardSettings.Paint += (s, e) =>
            {
                using (Pen p = new Pen(Color.FromArgb(45, 50, 72), 1))
                {
                    e.Graphics.DrawRectangle(p, 0, 0, cardSettings.Width - 1, cardSettings.Height - 1);
                }
            };

            // Controller Status Indicator
            Label lblCtrlHeader = new Label();
            lblCtrlHeader.Text = "CONTROLLER STATUS";
            lblCtrlHeader.Font = new Font("Segoe UI", 8f, FontStyle.Bold);
            lblCtrlHeader.ForeColor = Color.FromArgb(255, 152, 0);
            lblCtrlHeader.Location = new Point(20, 15);
            lblCtrlHeader.AutoSize = true;

            lblControllerStatus = new Label();
            lblControllerStatus.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            lblControllerStatus.Location = new Point(20, 35);
            lblControllerStatus.Size = new Size(435, 25);

            // Separator 1
            Panel sep1 = new Panel();
            sep1.Location = new Point(20, 68);
            sep1.Size = new Size(435, 1);
            sep1.BackColor = Color.FromArgb(45, 50, 72);

            // FPS Option
            Label lblFps = new Label();
            lblFps.Text = "Framerate & Game Speed Mode:";
            lblFps.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
            lblFps.Location = new Point(20, 80);
            lblFps.AutoSize = true;

            comboFps = new ComboBox();
            comboFps.DropDownStyle = ComboBoxStyle.DropDownList;
            comboFps.Font = new Font("Segoe UI", 9.5f);
            comboFps.Location = new Point(20, 105);
            comboFps.Size = new Size(435, 28);
            comboFps.Items.Add("60 FPS - High Smoothness (Normal Speed Fixed, 0.5x Delta)");
            comboFps.Items.Add("30 FPS - Original Console Target (PS4 Native Rate)");
            comboFps.SelectedIndex = 0;

            // Resolution Option
            Label lblRes = new Label();
            lblRes.Text = "Display Resolution:";
            lblRes.Font = new Font("Segoe UI", 9.5f, FontStyle.Regular);
            lblRes.Location = new Point(20, 145);
            lblRes.AutoSize = true;

            comboRes = new ComboBox();
            comboRes.DropDownStyle = ComboBoxStyle.DropDownList;
            comboRes.Font = new Font("Segoe UI", 9.5f);
            comboRes.Location = new Point(20, 170);
            comboRes.Size = new Size(435, 28);
            comboRes.Items.Add("1920 x 1080 (1080p Full HD - Recommended)");
            comboRes.Items.Add("2560 x 1440 (1440p 2K QHD)");
            comboRes.Items.Add("3840 x 2160 (2160p 4K Ultra HD)");
            comboRes.Items.Add("1280 x 720 (720p HD Standard)");
            comboRes.SelectedIndex = 0;

            // Fullscreen & FSR Toggles
            checkFullscreen = new CheckBox();
            checkFullscreen.Text = "Fullscreen / Borderless Mode";
            checkFullscreen.Font = new Font("Segoe UI", 9.5f);
            checkFullscreen.Location = new Point(20, 215);
            checkFullscreen.Size = new Size(250, 25);
            checkFullscreen.Checked = false;

            checkFsr = new CheckBox();
            checkFsr.Text = "Enable AMD FSR Quality Upscaling";
            checkFsr.Font = new Font("Segoe UI", 9.5f);
            checkFsr.Location = new Point(20, 245);
            checkFsr.Size = new Size(280, 25);
            checkFsr.Checked = true;

            // Info note
            Label lblNote = new Label();
            lblNote.Text = "* VSync FIFO (60 FPS) and Windows 1ms high-res timer are active.";
            lblNote.Font = new Font("Segoe UI", 8.5f, FontStyle.Italic);
            lblNote.ForeColor = textMuted;
            lblNote.Location = new Point(20, 285);
            lblNote.Size = new Size(435, 40);

            cardSettings.Controls.Add(lblCtrlHeader);
            cardSettings.Controls.Add(lblControllerStatus);
            cardSettings.Controls.Add(sep1);
            cardSettings.Controls.Add(lblFps);
            cardSettings.Controls.Add(comboFps);
            cardSettings.Controls.Add(lblRes);
            cardSettings.Controls.Add(comboRes);
            cardSettings.Controls.Add(checkFullscreen);
            cardSettings.Controls.Add(checkFsr);
            cardSettings.Controls.Add(lblNote);

            // Action Buttons
            btnPlay = new Button();
            btnPlay.Text = "▶  PLAY J-STARS VICTORY VS+";
            btnPlay.Font = new Font("Segoe UI", 12f, FontStyle.Bold);
            btnPlay.BackColor = accentOrange;
            btnPlay.ForeColor = Color.White;
            btnPlay.FlatStyle = FlatStyle.Flat;
            btnPlay.FlatAppearance.BorderSize = 0;
            btnPlay.Location = new Point(25, 480);
            btnPlay.Size = new Size(330, 52);
            btnPlay.Cursor = Cursors.Hand;
            btnPlay.Click += (s, e) => LaunchGame();
            btnPlay.MouseEnter += (s, e) => btnPlay.BackColor = accentHover;
            btnPlay.MouseLeave += (s, e) => btnPlay.BackColor = accentOrange;

            btnSaves = new Button();
            btnSaves.Text = "📁 Save Folder";
            btnSaves.Font = new Font("Segoe UI", 9.5f);
            btnSaves.BackColor = Color.FromArgb(40, 44, 65);
            btnSaves.ForeColor = textWhite;
            btnSaves.FlatStyle = FlatStyle.Flat;
            btnSaves.FlatAppearance.BorderSize = 0;
            btnSaves.Location = new Point(365, 480);
            btnSaves.Size = new Size(135, 52);
            btnSaves.Cursor = Cursors.Hand;
            btnSaves.Click += (s, e) => OpenSaveFolder();

            Label footerLabel = new Label();
            footerLabel.Text = "J-Stars Victory VS+ PC Translation Project • REA Protocol Port";
            footerLabel.Font = new Font("Segoe UI", 8f);
            footerLabel.ForeColor = Color.FromArgb(100, 105, 125);
            footerLabel.AutoSize = true;
            footerLabel.Location = new Point(105, 550);

            this.Controls.Add(headerPanel);
            this.Controls.Add(cardSettings);
            this.Controls.Add(btnPlay);
            this.Controls.Add(btnSaves);
            this.Controls.Add(footerLabel);
        }

        private void UpdateControllerStatus()
        {
            if (IsControllerConnected())
            {
                lblControllerStatus.Text = "●  Xbox Controller Connected (Slot 1 Ready)";
                lblControllerStatus.ForeColor = greenConnected;
            }
            else
            {
                lblControllerStatus.Text = "○  Keyboard Mode Active (No Xbox Controller Detected)";
                lblControllerStatus.ForeColor = amberDisconnected;
            }
        }

        private void OpenSaveFolder()
        {
            string savePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "extracted_game", "app0", "savedata");
            if (!Directory.Exists(savePath))
            {
                savePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "extracted_game", "app0", "savedata");
            }
            if (Directory.Exists(savePath))
            {
                Process.Start("explorer.exe", Path.GetFullPath(savePath));
            }
            else
            {
                MessageBox.Show("Save data folder does not exist yet. Play the game to create one!", "Save Data", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void SaveConfig()
        {
            try
            {
                string cfg = string.Format("FPS={0}\nRES={1}\nFULLSCREEN={2}\nFSR={3}",
                    comboFps.SelectedIndex, comboRes.SelectedIndex, checkFullscreen.Checked, checkFsr.Checked);
                File.WriteAllText("launcher_config.ini", cfg);
            }
            catch { }
        }

        private void LoadConfig()
        {
            try
            {
                if (File.Exists("launcher_config.ini"))
                {
                    string[] lines = File.ReadAllLines("launcher_config.ini");
                    foreach (string line in lines)
                    {
                        string[] parts = line.Split('=');
                        if (parts.Length == 2)
                        {
                            string key = parts[0].Trim().ToUpperInvariant();
                            string val = parts[1].Trim();
                            if (key == "FPS") comboFps.SelectedIndex = Math.Min(int.Parse(val), comboFps.Items.Count - 1);
                            if (key == "RES") comboRes.SelectedIndex = Math.Min(int.Parse(val), comboRes.Items.Count - 1);
                            if (key == "FULLSCREEN") checkFullscreen.Checked = bool.Parse(val);
                            if (key == "FSR") checkFsr.Checked = bool.Parse(val);
                        }
                    }
                }
            }
            catch { }
        }

        private void LaunchGame()
        {
            SaveConfig();

            // Locate game executable and base directory
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string exePath = Path.Combine(baseDir, "jstars_pc.exe");
            if (!File.Exists(exePath)) exePath = Path.Combine(baseDir, "out", "jstars_pc.exe");
            if (!File.Exists(exePath)) exePath = Path.Combine(baseDir, "out", "gpu", "jstars_pc.exe");

            if (!File.Exists(exePath))
            {
                MessageBox.Show("Could not find jstars_pc.exe!\nPlease ensure game files are in place.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            string targetDir = Path.GetDirectoryName(Path.GetFullPath(exePath));

            // Locate boot-linked.bin
            string bootBin = "boot-linked.bin";
            if (!File.Exists(Path.Combine(targetDir, "boot-linked.bin")))
            {
                if (File.Exists(Path.Combine(baseDir, "boot-linked.bin")))
                    bootBin = Path.Combine(baseDir, "boot-linked.bin");
                else if (File.Exists(Path.Combine(baseDir, "out", "boot-linked.bin")))
                    bootBin = Path.Combine(baseDir, "out", "boot-linked.bin");
            }

            // Locate app0
            string app0Dir = "extracted_game/app0";
            if (!Directory.Exists(Path.Combine(targetDir, "extracted_game", "app0")))
            {
                if (Directory.Exists(Path.Combine(baseDir, "extracted_game", "app0")))
                    app0Dir = Path.Combine(baseDir, "extracted_game", "app0").Replace('\\', '/');
                else if (Directory.Exists(Path.Combine(baseDir, "..", "extracted_game", "app0")))
                    app0Dir = Path.GetFullPath(Path.Combine(baseDir, "..", "extracted_game", "app0")).Replace('\\', '/');
            }

            // Locate import_names.txt
            string importArg = "";
            if (File.Exists(Path.Combine(targetDir, "import_names.txt")))
            {
                importArg = " --import-names import_names.txt";
            }
            else if (File.Exists(Path.Combine(baseDir, "import_names.txt")))
            {
                importArg = string.Format(" --import-names \"{0}\"", Path.Combine(baseDir, "import_names.txt"));
            }
            else if (File.Exists(Path.Combine(baseDir, "out", "import_names.txt")))
            {
                importArg = string.Format(" --import-names \"{0}\"", Path.Combine(baseDir, "out", "import_names.txt"));
            }

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = Path.GetFullPath(exePath);
            psi.Arguments = string.Format("\"{0}\" --app0 \"{1}\"{2}", bootBin, app0Dir, importArg);
            psi.WorkingDirectory = targetDir;
            psi.UseShellExecute = false;

            // Ensure directory with all DLLs is at the front of PATH
            string currentPath = Environment.GetEnvironmentVariable("PATH") ?? "";
            psi.EnvironmentVariables["PATH"] = targetDir + ";" + currentPath;

            // Direct memory size optimization for J-Stars (4864 MiB fits memory commit smoothly)
            psi.EnvironmentVariables["BB_DMEM_MB"] = "4864";

            // Configure Environment Variables
            if (comboFps.SelectedIndex == 1)
            {
                psi.EnvironmentVariables["JSTARS_30FPS"] = "1";
                psi.EnvironmentVariables["BB_FPS_LIMIT"] = "30";
            }
            else
            {
                psi.EnvironmentVariables["JSTARS_30FPS"] = "0";
                psi.EnvironmentVariables["BB_FPS_LIMIT"] = "60";
            }

            psi.EnvironmentVariables["BB_FSR1"] = checkFsr.Checked ? "1" : "0";
            psi.EnvironmentVariables["BB_FULLSCREEN"] = checkFullscreen.Checked ? "1" : "0";
            psi.EnvironmentVariables["BB_FORCE_FULLSCREEN"] = checkFullscreen.Checked ? "1" : "0";

            btnPlay.Enabled = false;
            btnPlay.Text = "⏳  GAME RUNNING...";

            try
            {
                this.WindowState = FormWindowState.Minimized;
                Process p = new Process();
                p.StartInfo = psi;
                p.EnableRaisingEvents = true;

                p.Exited += (s, e) =>
                {
                    // Asynchronous completion: UI thread stays responsive at all times
                    this.BeginInvoke((Action)(() =>
                    {
                        btnPlay.Enabled = true;
                        btnPlay.Text = "▶  PLAY J-STARS VICTORY VS+";
                        this.WindowState = FormWindowState.Normal;
                        this.Show();
                        this.BringToFront();
                        UpdateControllerStatus();

                        if (p.ExitCode != 0)
                        {
                            MessageBox.Show(
                                string.Format("Game finished (Exit Code: {0} / 0x{0:X}).", p.ExitCode),
                                "J-Stars Victory VS+ Session",
                                MessageBoxButtons.OK,
                                MessageBoxIcon.Information);
                        }
                    }));
                };

                p.Start();
            }
            catch (Exception ex)
            {
                btnPlay.Enabled = true;
                btnPlay.Text = "▶  PLAY J-STARS VICTORY VS+";
                this.WindowState = FormWindowState.Normal;
                this.Show();
                MessageBox.Show("Failed to launch game: " + ex.Message, "Launch Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new LauncherForm());
        }
    }
}
