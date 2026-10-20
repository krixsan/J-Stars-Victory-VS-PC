# anyPS4 Reference Target: J-Stars Victory VS+

- **Title ID:** `CUSA01593` (US) / `CUSA01661` (EU)
- **Engine:** Custom Spike Chunsoft 3D Fighting Engine + Havok Physics 2013
- **Status:** **FULLY PLAYABLE (100% Native PC)**
- **Target Performance:** 60 FPS Normal Speed (1.0x Real-Time) / Native 30 FPS toggle

---

## Analisis REA & Penyelesaian Masalah

### 1. Fix Game Speed / Delta Time untuk 60 FPS (Atasi Fast-Forward 2x)
- **Akar Masalah:** Engine J-Stars tidak menggunakan delta time dinamis berbasis jam dinding (`now - last`). Game melakukan akumulasi tetap per *tick* frame. Memaksa *flip rate* dari 1 (30 Hz) ke 0 (60 Hz) membuat logika engine dieksekusi 60 kali per detik sehingga game berjalan 2x lipat lebih cepat.
- **Solusi REA Patches:**
  1. **Flip Rate Override (`0x43d8e6`):** Mengganti `movl $1, %esi` / `movl $2, %esi` menjadi `xorl %esi, %esi` (force rate 0).
  2. **Havok Timestep (`0x1817be`, `0x18189c`, `0x182cbb`, `0x186c52`):** Mengganti nilai float `1/30.0f` (`0x3d088889`) menjadi `1/60.0f` (`0x3c888889`), sehingga gravitasi, lompatan, dan knockback karakter berjalan normal 1.0x pada 60 FPS.
  3. **Animation Speed Multiplier (`0x24630c`):** Mengurangi *motion step constant* menjadi setengahnya (`15.0f` / `0.5x`) untuk menormalkan animasi bertarung.
  4. **Global Delta Time (`0x585bc8`):** Mengganti konstanta frame delta global menjadi `0.016667f`.

### 2. Present Mode Deadlock Prevention
- Menggunakan `VK_PRESENT_MODE_MAILBOX_KHR` yang dipadukan dengan pembatas waktu 16.666 ms (`driver.cpp`) agar swapchain tidak pernah membeku (*hang*) di GPU NVIDIA Optimus laptop.

### 3. Asynchronous GUI Launcher
- Launcher interaktif berbasis WinForms C# (`Launcher.exe`) dengan live XInput polling controller, pemilih 30/60 FPS, dan minimasi asinkron agar tidak memicu status *"Not Responding"*.
