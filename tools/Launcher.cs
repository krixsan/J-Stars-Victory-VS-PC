using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Text;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace JStarsLauncher
{
    // Modern Rounded Button with Gradient, Hover & Pressed animations
    public class ModernButton : Button
    {
        public Color ColorTop { get; set; }
        public Color ColorBottom { get; set; }
        public Color HoverColorTop { get; set; }
        public Color HoverColorBottom { get; set; }
        public Color PressedColorTop { get; set; }
        public Color PressedColorBottom { get; set; }
        public Color BorderColor { get; set; }
        public int Radius { get; set; }

        private bool isHovered = false;
        private bool isPressed = false;

        public ModernButton()
        {
            this.SetStyle(ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint | ControlStyles.OptimizedDoubleBuffer, true);
            this.DoubleBuffered = true;
            this.FlatStyle = FlatStyle.Flat;
            this.FlatAppearance.BorderSize = 0;
            this.Cursor = Cursors.Hand;
            this.Radius = 8;
            this.ColorTop = Color.FromArgb(245, 80, 0);
            this.ColorBottom = Color.FromArgb(220, 50, 0);
            this.HoverColorTop = Color.FromArgb(255, 110, 20);
            this.HoverColorBottom = Color.FromArgb(240, 75, 10);
            this.PressedColorTop = Color.FromArgb(200, 45, 0);
            this.PressedColorBottom = Color.FromArgb(180, 35, 0);
            this.BorderColor = Color.FromArgb(255, 140, 40);
        }

        protected override void OnMouseEnter(EventArgs e)
        {
            isHovered = true;
            base.OnMouseEnter(e);
            this.Invalidate();
        }

        protected override void OnMouseLeave(EventArgs e)
        {
            isHovered = false;
            isPressed = false;
            base.OnMouseLeave(e);
            this.Invalidate();
        }

        protected override void OnMouseDown(MouseEventArgs mevent)
        {
            if (mevent.Button == MouseButtons.Left) isPressed = true;
            base.OnMouseDown(mevent);
            this.Invalidate();
        }

        protected override void OnMouseUp(MouseEventArgs mevent)
        {
            isPressed = false;
            base.OnMouseUp(mevent);
            this.Invalidate();
        }

        private GraphicsPath GetRoundRectPath(Rectangle rect, int radius)
        {
            GraphicsPath path = new GraphicsPath();
            int diameter = radius * 2;
            Rectangle arc = new Rectangle(rect.X, rect.Y, diameter, diameter);

            path.AddArc(arc, 180, 90);
            arc.X = rect.Right - diameter;
            path.AddArc(arc, 270, 90);
            arc.Y = rect.Bottom - diameter;
            path.AddArc(arc, 0, 90);
            arc.X = rect.Left;
            path.AddArc(arc, 90, 90);
            path.CloseFigure();
            return path;
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.TextRenderingHint = TextRenderingHint.ClearTypeGridFit;

            Rectangle rect = new Rectangle(0, 0, this.Width - 1, this.Height - 1);
            if (rect.Width <= 0 || rect.Height <= 0) return;

            using (GraphicsPath path = GetRoundRectPath(rect, this.Radius))
            {
                if (!this.Enabled)
                {
                    using (SolidBrush b = new SolidBrush(Color.FromArgb(60, 65, 80)))
                    {
                        g.FillPath(b, path);
                    }
                    using (Pen p = new Pen(Color.FromArgb(80, 85, 100)))
                    {
                        g.DrawPath(p, path);
                    }
                    TextRenderer.DrawText(g, this.Text, this.Font, rect, Color.FromArgb(170, 175, 190),
                        TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);
                    return;
                }

                Color c1 = isPressed ? PressedColorTop : (isHovered ? HoverColorTop : ColorTop);
                Color c2 = isPressed ? PressedColorBottom : (isHovered ? HoverColorBottom : ColorBottom);

                using (LinearGradientBrush brush = new LinearGradientBrush(rect, c1, c2, LinearGradientMode.Vertical))
                {
                    g.FillPath(brush, path);
                }

                if (BorderColor != Color.Empty && BorderColor != Color.Transparent)
                {
                    Color border = isHovered ? Color.FromArgb(255, 200, 120) : BorderColor;
                    using (Pen p = new Pen(border, 1.2f))
                    {
                        g.DrawPath(p, path);
                    }
                }

                // Drop shadow text effect
                Rectangle shadowRect = new Rectangle(rect.X + 1, rect.Y + 1, rect.Width, rect.Height);
                TextRenderer.DrawText(g, this.Text, this.Font, shadowRect, Color.FromArgb(100, 0, 0, 0),
                    TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);

                TextRenderer.DrawText(g, this.Text, this.Font, rect, this.ForeColor,
                    TextFormatFlags.HorizontalCenter | TextFormatFlags.VerticalCenter);
            }
        }
    }

    // Modern Gaming Launcher Form
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

        // Window drag & rounded region P/Invokes
        [DllImport("user32.dll")]
        public static extern bool ReleaseCapture();

        [DllImport("user32.dll")]
        public static extern int SendMessage(IntPtr hWnd, int Msg, int wParam, int lParam);

        [DllImport("gdi32.dll", EntryPoint = "CreateRoundRectRgn")]
        private static extern IntPtr CreateRoundRectRgn(
            int nLeftRect, int nTopRect, int nRightRect, int nBottomRect,
            int nWidthEllipse, int nHeightEllipse
        );

        private const int WM_NCLBUTTONDOWN = 0xA1;
        private const int HT_CAPTION = 0x2;

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
        private Panel panelController;
        private ModernButton btnPlay;
        private ModernButton btnSaves;
        private ModernButton btnReadme;
        private Timer timerController;
        private Bitmap backgroundBanner;

        // Custom Palette
        private readonly Color colorGreen = Color.FromArgb(16, 185, 129);
        private readonly Color colorAmber = Color.FromArgb(245, 158, 11);
        private readonly Color textMain = Color.FromArgb(243, 244, 246);
        private readonly Color textMuted = Color.FromArgb(156, 163, 175);

        public LauncherForm()
        {
            this.SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.OptimizedDoubleBuffer, true);
            this.DoubleBuffered = true;

            LoadSplashBanner();
            InitializeComponent();
            LoadConfig();
            UpdateControllerStatus();

            timerController = new Timer();
            timerController.Interval = 1500;
            timerController.Tick += (s, e) => UpdateControllerStatus();
            timerController.Start();
        }

        private void LoadSplashBanner()
        {
            string baseDir = AppDomain.CurrentDomain.BaseDirectory;
            string[] searchPaths = new string[]
            {
                Path.Combine(baseDir, "extracted_game", "app0", "sce_sys", "pic0.png"),
                Path.Combine(baseDir, "extracted_game", "app0", "sce_sys", "pic1.png"),
                Path.Combine(baseDir, "..", "extracted_game", "app0", "sce_sys", "pic0.png"),
                Path.Combine(baseDir, "..", "extracted_game", "app0", "sce_sys", "pic1.png"),
                Path.Combine(baseDir, "J-Stars Victory+ PC Version", "extracted_game", "app0", "sce_sys", "pic0.png"),
                Path.Combine(baseDir, "pic0.png"),
                Path.Combine(baseDir, "assets", "pic0.png")
            };

            foreach (string p in searchPaths)
            {
                if (File.Exists(p))
                {
                    try
                    {
                        // Use MemoryStream to avoid holding a lock on the file
                        byte[] bytes = File.ReadAllBytes(p);
                        using (MemoryStream ms = new MemoryStream(bytes))
                        {
                            backgroundBanner = new Bitmap(Image.FromStream(ms));
                        }
                        break;
                    }
                    catch { }
                }
            }
        }

        private void DragWindow(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                ReleaseCapture();
                SendMessage(this.Handle, WM_NCLBUTTONDOWN, HT_CAPTION, 0);
            }
        }

        private void InitializeComponent()
        {
            this.Text = "J-Stars Victory VS+ | Native PC Launcher";
            this.Size = new Size(940, 560);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.None;
            this.BackColor = Color.FromArgb(14, 16, 24);
            this.ForeColor = textMain;

            // Apply modern rounded window region
            try
            {
                this.Region = Region.FromHrgn(CreateRoundRectRgn(0, 0, this.Width, this.Height, 18, 18));
            }
            catch { }

            // Set Application Icon
            string icoPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "icon.ico");
            if (!File.Exists(icoPath))
                icoPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets", "jstars.ico");
            if (!File.Exists(icoPath))
                icoPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "assets", "jstars.ico");

            if (File.Exists(icoPath))
            {
                try { this.Icon = new Icon(icoPath); } catch { }
            }
            else
            {
                try { this.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }
            }

            // Top Custom Title Bar (Draggable)
            Panel titleBar = new Panel();
            titleBar.Location = new Point(0, 0);
            titleBar.Size = new Size(this.Width, 38);
            titleBar.BackColor = Color.Transparent;
            titleBar.MouseDown += DragWindow;

            Label titleBarIcon = new Label();
            titleBarIcon.Text = "★";
            titleBarIcon.Font = new Font("Segoe UI", 10f, FontStyle.Bold);
            titleBarIcon.ForeColor = Color.FromArgb(255, 160, 0);
            titleBarIcon.Location = new Point(16, 9);
            titleBarIcon.AutoSize = true;
            titleBarIcon.MouseDown += DragWindow;

            Label titleBarText = new Label();
            titleBarText.Text = "J-STARS VICTORY VS+   //   PC LAUNCHER";
            titleBarText.Font = new Font("Segoe UI Semibold", 8.5f, FontStyle.Bold);
            titleBarText.ForeColor = Color.FromArgb(170, 180, 205);
            titleBarText.Location = new Point(36, 11);
            titleBarText.AutoSize = true;
            titleBarText.MouseDown += DragWindow;

            Button btnMin = new Button();
            btnMin.Text = "—";
            btnMin.Font = new Font("Segoe UI", 9f);
            btnMin.Size = new Size(38, 28);
            btnMin.Location = new Point(this.Width - 84, 5);
            btnMin.FlatStyle = FlatStyle.Flat;
            btnMin.FlatAppearance.BorderSize = 0;
            btnMin.ForeColor = Color.FromArgb(180, 190, 210);
            btnMin.BackColor = Color.FromArgb(30, 0, 0, 0);
            btnMin.Cursor = Cursors.Hand;
            btnMin.Click += (s, e) => this.WindowState = FormWindowState.Minimized;
            btnMin.MouseEnter += (s, e) => { btnMin.BackColor = Color.FromArgb(60, 70, 95); btnMin.ForeColor = Color.White; };
            btnMin.MouseLeave += (s, e) => { btnMin.BackColor = Color.FromArgb(30, 0, 0, 0); btnMin.ForeColor = Color.FromArgb(180, 190, 210); };

            Button btnClose = new Button();
            btnClose.Text = "✕";
            btnClose.Font = new Font("Segoe UI", 9f);
            btnClose.Size = new Size(38, 28);
            btnClose.Location = new Point(this.Width - 44, 5);
            btnClose.FlatStyle = FlatStyle.Flat;
            btnClose.FlatAppearance.BorderSize = 0;
            btnClose.ForeColor = Color.FromArgb(180, 190, 210);
            btnClose.BackColor = Color.FromArgb(30, 0, 0, 0);
            btnClose.Cursor = Cursors.Hand;
            btnClose.Click += (s, e) => Application.Exit();
            btnClose.MouseEnter += (s, e) => { btnClose.BackColor = Color.FromArgb(220, 38, 38); btnClose.ForeColor = Color.White; };
            btnClose.MouseLeave += (s, e) => { btnClose.BackColor = Color.FromArgb(30, 0, 0, 0); btnClose.ForeColor = Color.FromArgb(180, 190, 210); };

            titleBar.Controls.Add(titleBarIcon);
            titleBar.Controls.Add(titleBarText);
            titleBar.Controls.Add(btnMin);
            titleBar.Controls.Add(btnClose);
            this.Controls.Add(titleBar);

            // Hero Branding Area
            Label tagPill = new Label();
            tagPill.Text = "  PS4 NATIVE PORT • SHADPS4 VULKAN ARCHITECTURE  ";
            tagPill.Font = new Font("Segoe UI", 7.5f, FontStyle.Bold);
            tagPill.ForeColor = Color.FromArgb(255, 175, 40);
            tagPill.BackColor = Color.FromArgb(140, 24, 28, 40);
            tagPill.Location = new Point(44, 52);
            tagPill.AutoSize = true;
            tagPill.Padding = new Padding(4, 3, 4, 3);
            tagPill.MouseDown += DragWindow;

            Label titleHero = new Label();
            titleHero.Text = "J-STARS VICTORY VS+";
            titleHero.Font = new Font("Segoe UI", 28f, FontStyle.Bold);
            titleHero.ForeColor = Color.White;
            titleHero.Location = new Point(38, 76);
            titleHero.AutoSize = true;
            titleHero.BackColor = Color.Transparent;
            titleHero.MouseDown += DragWindow;

            Label subTitleHero = new Label();
            subTitleHero.Text = "WEEKLY SHONEN JUMP 45TH ANNIVERSARY • NATIVE PC WRAPPER";
            subTitleHero.Font = new Font("Segoe UI Semibold", 8.5f, FontStyle.Regular);
            subTitleHero.ForeColor = Color.FromArgb(180, 190, 215);
            subTitleHero.Location = new Point(44, 130);
            subTitleHero.AutoSize = true;
            subTitleHero.BackColor = Color.Transparent;
            subTitleHero.MouseDown += DragWindow;

            this.Controls.Add(tagPill);
            this.Controls.Add(titleHero);
            this.Controls.Add(subTitleHero);

            // Controller Status Indicator Card
            panelController = new Panel();
            panelController.Location = new Point(44, 158);
            panelController.Size = new Size(450, 36);
            panelController.BackColor = Color.FromArgb(215, 18, 22, 34);
            panelController.Paint += (s, e) =>
            {
                using (Pen p = new Pen(Color.FromArgb(60, 75, 105), 1))
                {
                    e.Graphics.DrawRectangle(p, 0, 0, panelController.Width - 1, panelController.Height - 1);
                }
            };

            lblControllerStatus = new Label();
            lblControllerStatus.Font = new Font("Segoe UI Semibold", 9f);
            lblControllerStatus.Location = new Point(14, 8);
            lblControllerStatus.Size = new Size(422, 20);
            lblControllerStatus.BackColor = Color.Transparent;
            panelController.Controls.Add(lblControllerStatus);
            this.Controls.Add(panelController);

            // Settings Card (Glassmorphic Flat Dark Box)
            Panel cardSettings = new Panel();
            cardSettings.Location = new Point(44, 205);
            cardSettings.Size = new Size(450, 230);
            cardSettings.BackColor = Color.FromArgb(220, 16, 20, 30);
            cardSettings.Paint += (s, e) =>
            {
                using (Pen p = new Pen(Color.FromArgb(55, 68, 96), 1))
                {
                    e.Graphics.DrawRectangle(p, 0, 0, cardSettings.Width - 1, cardSettings.Height - 1);
                }
            };

            Label lblCardHeader = new Label();
            lblCardHeader.Text = "GRAPHICS & ENGINE CONFIGURATION";
            lblCardHeader.Font = new Font("Segoe UI", 8f, FontStyle.Bold);
            lblCardHeader.ForeColor = Color.FromArgb(255, 165, 0);
            lblCardHeader.Location = new Point(18, 14);
            lblCardHeader.AutoSize = true;
            cardSettings.Controls.Add(lblCardHeader);

            // FPS Mode Option
            Label lblFps = new Label();
            lblFps.Text = "Framerate & Animation Timing Mode:";
            lblFps.Font = new Font("Segoe UI", 9f);
            lblFps.ForeColor = Color.FromArgb(215, 220, 235);
            lblFps.Location = new Point(18, 36);
            lblFps.AutoSize = true;

            comboFps = new ComboBox();
            comboFps.DropDownStyle = ComboBoxStyle.DropDownList;
            comboFps.Font = new Font("Segoe UI", 9f);
            comboFps.Location = new Point(18, 58);
            comboFps.Size = new Size(414, 26);
            comboFps.BackColor = Color.FromArgb(28, 33, 48);
            comboFps.ForeColor = Color.White;
            comboFps.DrawMode = DrawMode.OwnerDrawFixed;
            comboFps.ItemHeight = 22;
            comboFps.Items.Add("30 FPS - Original Console Target (Stable Normal Speed - Recommended)");
            comboFps.Items.Add("60 FPS - High Smoothness Mode (0.5x Delta Animation Speed Patch)");
            comboFps.SelectedIndex = 0;
            comboFps.DrawItem += DrawDarkComboItem;

            cardSettings.Controls.Add(lblFps);
            cardSettings.Controls.Add(comboFps);

            // Resolution Option
            Label lblRes = new Label();
            lblRes.Text = "Display Resolution:";
            lblRes.Font = new Font("Segoe UI", 9f);
            lblRes.ForeColor = Color.FromArgb(215, 220, 235);
            lblRes.Location = new Point(18, 92);
            lblRes.AutoSize = true;

            comboRes = new ComboBox();
            comboRes.DropDownStyle = ComboBoxStyle.DropDownList;
            comboRes.Font = new Font("Segoe UI", 9f);
            comboRes.Location = new Point(18, 114);
            comboRes.Size = new Size(414, 26);
            comboRes.BackColor = Color.FromArgb(28, 33, 48);
            comboRes.ForeColor = Color.White;
            comboRes.DrawMode = DrawMode.OwnerDrawFixed;
            comboRes.ItemHeight = 22;
            comboRes.Items.Add("1920 x 1080 (1080p Full HD - Recommended)");
            comboRes.Items.Add("2560 x 1440 (1440p 2K QHD)");
            comboRes.Items.Add("3840 x 2160 (2160p 4K Ultra HD)");
            comboRes.Items.Add("1280 x 720 (720p HD Standard)");
            comboRes.SelectedIndex = 0;
            comboRes.DrawItem += DrawDarkComboItem;

            cardSettings.Controls.Add(lblRes);
            cardSettings.Controls.Add(comboRes);

            // Checkbox options
            checkFullscreen = new CheckBox();
            checkFullscreen.Text = "Fullscreen / Borderless Display Mode";
            checkFullscreen.Font = new Font("Segoe UI", 9f);
            checkFullscreen.ForeColor = Color.FromArgb(220, 225, 240);
            checkFullscreen.Location = new Point(18, 150);
            checkFullscreen.Size = new Size(260, 22);
            checkFullscreen.Checked = true;

            checkFsr = new CheckBox();
            checkFsr.Text = "Enable AMD FidelityFX Super Resolution (FSR)";
            checkFsr.Font = new Font("Segoe UI", 9f);
            checkFsr.ForeColor = Color.FromArgb(220, 225, 240);
            checkFsr.Location = new Point(18, 174);
            checkFsr.Size = new Size(310, 22);
            checkFsr.Checked = true;

            Label lblNote = new Label();
            lblNote.Text = "• VSync FIFO (60Hz locked) and Windows 1ms high-res precision timer active.";
            lblNote.Font = new Font("Segoe UI", 7.5f, FontStyle.Italic);
            lblNote.ForeColor = Color.FromArgb(140, 150, 175);
            lblNote.Location = new Point(18, 203);
            lblNote.Size = new Size(414, 18);

            cardSettings.Controls.Add(checkFullscreen);
            cardSettings.Controls.Add(checkFsr);
            cardSettings.Controls.Add(lblNote);
            this.Controls.Add(cardSettings);

            // Bottom Action Controls
            btnSaves = new ModernButton();
            btnSaves.Text = "📁  Save Folder";
            btnSaves.Font = new Font("Segoe UI Semibold", 9.5f);
            btnSaves.Location = new Point(44, 452);
            btnSaves.Size = new Size(140, 48);
            btnSaves.Radius = 6;
            btnSaves.ColorTop = Color.FromArgb(34, 40, 58);
            btnSaves.ColorBottom = Color.FromArgb(26, 30, 44);
            btnSaves.HoverColorTop = Color.FromArgb(48, 56, 82);
            btnSaves.HoverColorBottom = Color.FromArgb(36, 42, 62);
            btnSaves.PressedColorTop = Color.FromArgb(22, 26, 38);
            btnSaves.PressedColorBottom = Color.FromArgb(18, 20, 30);
            btnSaves.BorderColor = Color.FromArgb(65, 78, 110);
            btnSaves.ForeColor = Color.FromArgb(230, 235, 250);
            btnSaves.Click += (s, e) => OpenSaveFolder();
            this.Controls.Add(btnSaves);

            btnReadme = new ModernButton();
            btnReadme.Text = "📖  Game Guide";
            btnReadme.Font = new Font("Segoe UI Semibold", 9.5f);
            btnReadme.Location = new Point(194, 452);
            btnReadme.Size = new Size(130, 48);
            btnReadme.Radius = 6;
            btnReadme.ColorTop = Color.FromArgb(34, 40, 58);
            btnReadme.ColorBottom = Color.FromArgb(26, 30, 44);
            btnReadme.HoverColorTop = Color.FromArgb(48, 56, 82);
            btnReadme.HoverColorBottom = Color.FromArgb(36, 42, 62);
            btnReadme.PressedColorTop = Color.FromArgb(22, 26, 38);
            btnReadme.PressedColorBottom = Color.FromArgb(18, 20, 30);
            btnReadme.BorderColor = Color.FromArgb(65, 78, 110);
            btnReadme.ForeColor = Color.FromArgb(230, 235, 250);
            btnReadme.Click += (s, e) => OpenGameGuide();
            this.Controls.Add(btnReadme);

            Label footerCredit = new Label();
            footerCredit.Text = "v1.02 Native PC Port • REA Protocol Engine • Universal anyPS Architecture";
            footerCredit.Font = new Font("Segoe UI", 7.5f);
            footerCredit.ForeColor = Color.FromArgb(120, 130, 155);
            footerCredit.Location = new Point(44, 514);
            footerCredit.AutoSize = true;
            this.Controls.Add(footerCredit);

            // Big Glowing "PLAY J-STARS" Action Button
            btnPlay = new ModernButton();
            btnPlay.Text = "▶   PLAY J-STARS";
            btnPlay.Font = new Font("Segoe UI", 13.5f, FontStyle.Bold);
            btnPlay.Location = new Point(610, 442);
            btnPlay.Size = new Size(284, 62);
            btnPlay.Radius = 10;
            // Shonen Jump fiery accent gradient
            btnPlay.ColorTop = Color.FromArgb(250, 85, 0);
            btnPlay.ColorBottom = Color.FromArgb(215, 45, 0);
            btnPlay.HoverColorTop = Color.FromArgb(255, 120, 25);
            btnPlay.HoverColorBottom = Color.FromArgb(245, 75, 10);
            btnPlay.PressedColorTop = Color.FromArgb(195, 40, 0);
            btnPlay.PressedColorBottom = Color.FromArgb(170, 30, 0);
            btnPlay.BorderColor = Color.FromArgb(255, 170, 60);
            btnPlay.ForeColor = Color.White;
            btnPlay.Click += (s, e) => LaunchGame();
            this.Controls.Add(btnPlay);
        }

        private void DrawDarkComboItem(object sender, DrawItemEventArgs e)
        {
            if (e.Index < 0) return;
            ComboBox cb = (ComboBox)sender;
            bool isSelected = (e.State & DrawItemState.Selected) == DrawItemState.Selected;

            Color bg = isSelected ? Color.FromArgb(230, 81, 0) : Color.FromArgb(26, 31, 46);
            Color fg = isSelected ? Color.White : Color.FromArgb(235, 240, 250);

            using (SolidBrush b = new SolidBrush(bg))
            {
                e.Graphics.FillRectangle(b, e.Bounds);
            }

            string text = cb.Items[e.Index].ToString();
            Rectangle textRect = new Rectangle(e.Bounds.X + 4, e.Bounds.Y, e.Bounds.Width - 8, e.Bounds.Height);
            TextRenderer.DrawText(e.Graphics, text, cb.Font, textRect, fg,
                TextFormatFlags.VerticalCenter | TextFormatFlags.Left | TextFormatFlags.EndEllipsis);
        }

        protected override void OnPaintBackground(PaintEventArgs e)
        {
            Graphics g = e.Graphics;

            // 1. Draw Background Image or Fallback Dark Color
            if (backgroundBanner != null)
            {
                g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                g.DrawImage(backgroundBanner, new Rectangle(0, 0, this.Width, this.Height));
            }
            else
            {
                using (SolidBrush b = new SolidBrush(Color.FromArgb(14, 16, 24)))
                {
                    g.FillRectangle(b, 0, 0, this.Width, this.Height);
                }
            }

            // 2. Cinematic Dark Overlay Gradients
            // A. Top Title Bar Overlay (Dark gradient from top for clear title bar reading)
            using (LinearGradientBrush topFade = new LinearGradientBrush(
                new Rectangle(0, 0, this.Width, 80),
                Color.FromArgb(230, 10, 12, 18),
                Color.FromArgb(0, 10, 12, 18),
                LinearGradientMode.Vertical))
            {
                g.FillRectangle(topFade, 0, 0, this.Width, 80);
            }

            // B. Left-to-Right Heavy Overlay for Settings and HUD Contrast
            using (LinearGradientBrush leftFade = new LinearGradientBrush(
                new Rectangle(0, 0, 560, this.Height),
                Color.FromArgb(235, 10, 12, 18),
                Color.FromArgb(10, 10, 12, 18),
                LinearGradientMode.Horizontal))
            {
                g.FillRectangle(leftFade, 0, 0, 560, this.Height);
            }

            // C. Bottom Bar Overlay (Dark base for action buttons)
            using (LinearGradientBrush bottomFade = new LinearGradientBrush(
                new Rectangle(0, 360, this.Width, this.Height - 360),
                Color.FromArgb(0, 10, 12, 18),
                Color.FromArgb(240, 8, 10, 15),
                LinearGradientMode.Vertical))
            {
                g.FillRectangle(bottomFade, 0, 360, this.Width, this.Height - 360);
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            // Subtle outer border for modern borderless window definition
            using (Pen borderPen = new Pen(Color.FromArgb(70, 85, 120), 1.5f))
            {
                e.Graphics.DrawRectangle(borderPen, 0, 0, this.Width - 1, this.Height - 1);
            }
        }

        private void UpdateControllerStatus()
        {
            if (IsControllerConnected())
            {
                lblControllerStatus.Text = "●  Xbox Gamepad Connected (XInput Slot 1 Ready)";
                lblControllerStatus.ForeColor = colorGreen;
            }
            else
            {
                lblControllerStatus.Text = "○  Keyboard & Mouse Active (No Xbox Controller Detected)";
                lblControllerStatus.ForeColor = colorAmber;
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
                MessageBox.Show("Save data directory has not been created yet. Play the game to generate save files!",
                    "Save Data", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void OpenGameGuide()
        {
            string readmePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "README_PORTABLE.txt");
            if (!File.Exists(readmePath))
                readmePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "README_PORTABLE.txt");

            if (File.Exists(readmePath))
            {
                Process.Start("notepad.exe", Path.GetFullPath(readmePath));
            }
            else
            {
                MessageBox.Show("README_PORTABLE.txt was not found in the game directory.",
                    "Game Guide", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private string ConfigPath
        {
            get { return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "launcher_config.ini"); }
        }

        private void SaveConfig()
        {
            try
            {
                string cfg = string.Format("FPS={0}\nRES={1}\nFULLSCREEN={2}\nFSR={3}",
                    comboFps.SelectedIndex, comboRes.SelectedIndex, checkFullscreen.Checked, checkFsr.Checked);
                File.WriteAllText(ConfigPath, cfg);
            }
            catch { }
        }

        private void LoadConfig()
        {
            try
            {
                if (File.Exists(ConfigPath))
                {
                    string[] lines = File.ReadAllLines(ConfigPath);
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
            if (!File.Exists(exePath)) exePath = Path.Combine(baseDir, "J-Stars Victory VS.exe");
            if (!File.Exists(exePath)) exePath = Path.Combine(baseDir, "out", "jstars_pc.exe");
            if (!File.Exists(exePath)) exePath = Path.Combine(baseDir, "out", "gpu", "jstars_pc.exe");

            if (!File.Exists(exePath))
            {
                MessageBox.Show("Could not find jstars_pc.exe!\nPlease ensure game files are properly installed.",
                    "Launcher Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
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

            // Locate app0 directory
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

            // Prioritize directory with all runtime DLLs at the front of PATH
            string currentPath = Environment.GetEnvironmentVariable("PATH") ?? "";
            psi.EnvironmentVariables["PATH"] = targetDir + ";" + currentPath;

            // Direct memory size optimization for J-Stars (4864 MiB fits memory commit smoothly)
            psi.EnvironmentVariables["BB_DMEM_MB"] = "4864";

            // Configure Environment Variables
            if (comboFps.SelectedIndex == 0) // Default: 30 FPS
            {
                psi.EnvironmentVariables["JSTARS_30FPS"] = "1";
                psi.EnvironmentVariables["BB_FPS_LIMIT"] = "30";
            }
            else // 60 FPS Mode
            {
                psi.EnvironmentVariables["JSTARS_30FPS"] = "0";
                psi.EnvironmentVariables["BB_FPS_LIMIT"] = "60";
            }

            string resStr = "1920x1080";
            if (comboRes.SelectedIndex == 1) resStr = "2560x1440";
            else if (comboRes.SelectedIndex == 2) resStr = "3840x2160";
            else if (comboRes.SelectedIndex == 3) resStr = "1280x720";

            try
            {
                string bbportIni = Path.Combine(targetDir, "bbport.ini");
                string bbportContent = string.Format(
                    "fullscreen={0}\noutput_res={1}\nfps_limit={2}\nfsr1={3}\n",
                    checkFullscreen.Checked ? "1" : "0",
                    resStr,
                    comboFps.SelectedIndex == 0 ? "30" : "60",
                    checkFsr.Checked ? "1" : "0"
                );
                File.WriteAllText(bbportIni, bbportContent);
            }
            catch { }

            psi.EnvironmentVariables["BB_FSR1"] = checkFsr.Checked ? "1" : "0";
            psi.EnvironmentVariables["BB_FULLSCREEN"] = checkFullscreen.Checked ? "1" : "0";
            psi.EnvironmentVariables["BB_FORCE_FULLSCREEN"] = checkFullscreen.Checked ? "1" : "0";
            psi.EnvironmentVariables["BB_OUTPUT_RES"] = resStr;

            btnPlay.Enabled = false;
            btnPlay.Text = "⏳   GAME RUNNING...";

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
                        btnPlay.Text = "▶   PLAY J-STARS";
                        this.WindowState = FormWindowState.Normal;
                        this.Show();
                        this.BringToFront();
                        UpdateControllerStatus();

                        if (p.ExitCode != 0)
                        {
                            MessageBox.Show(
                                string.Format("Game session completed (Exit Code: {0} / 0x{0:X}).", p.ExitCode),
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
                btnPlay.Text = "▶   PLAY J-STARS";
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
